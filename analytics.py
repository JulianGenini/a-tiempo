"""Database queries and schedule-performance calculations for A Tiempo?.

Developed with assistance from OpenAI Codex.
"""

from datetime import datetime, timedelta


# Rules shared by all reports
VALID_PERIODS = {"90", "365", "all"}
MAX_VALID_EARLY_SECONDS = 6 * 60 * 60
DEPARTURE_ON_TIME_LIMIT_SECONDS = 30 * 60
ARRIVAL_ON_TIME_LIMIT_SECONDS = 30 * 60

# Known beginnings help detect aircraft names joined without a separator
AIRCRAFT_MODEL_PREFIXES = (
    "Airbus ",
    "ATR ",
    "BAe ",
    "Beech ",
    "Boeing ",
    "Canadair ",
    "Dash ",
    "Embraer ",
    "McDonnell ",
    "Saab ",
)


# Period, date, and home-page helpers
def normalize_period(period):
    """Return a supported period, using one year as the default."""
    if period in VALID_PERIODS:
        return period
    return "365"


def get_dataset_dates(db):
    rows = db.execute(
        """
        SELECT MIN(flight_date) AS first_date, MAX(flight_date) AS last_date
        FROM flights
        WHERE movement = 'D'
        """
    )
    return rows[0]["first_date"], rows[0]["last_date"]


def get_start_date(db, period):
    """Calculate a period relative to the last date in the database."""
    first_date, last_date = get_dataset_dates(db)
    period = normalize_period(period)

    if period == "all":
        return first_date, last_date

    days = int(period)
    end = datetime.strptime(last_date, "%Y-%m-%d").date()
    start = end - timedelta(days=days - 1)
    return start.isoformat(), last_date


def get_airports(db):
    return db.execute(
        """
        SELECT DISTINCT a.iata, a.name
        FROM airports AS a
        JOIN flights AS f
          ON f.airport_id = a.id OR f.counterpart_airport_id = a.id
        WHERE LENGTH(a.iata) = 3
          AND a.iata NOT GLOB '*[^A-Za-z]*'
        ORDER BY a.iata
        """
    )


def get_airlines(db):
    return db.execute(
        """
        SELECT DISTINCT a.iata, a.name
        FROM airlines AS a
        JOIN flights AS f ON f.airline_id = a.id
        WHERE f.movement = 'D'
        ORDER BY a.name
        """
    )


def get_overview(db):
    rows = db.execute(
        """
        SELECT
            COUNT(*) AS movements,
            COUNT(DISTINCT airline_id) AS airlines,
            (
                SELECT COUNT(*)
                FROM (
                    SELECT airport_id AS id FROM flights
                    UNION
                    SELECT counterpart_airport_id AS id
                    FROM flights
                    WHERE counterpart_airport_id IS NOT NULL
                )
            ) AS airports
        FROM flights
        """
    )
    return rows[0]


# Input helpers
def normalize_flight_number(value):
    """Remove spaces so AR 1400 and AR1400 produce the same search."""
    if value is None:
        return ""
    return "".join(value.upper().split())


def display_flight_number(value):
    """Add one readable space before the numeric part when possible."""
    compact = normalize_flight_number(value)
    for index in range(1, len(compact)):
        if compact[index].isdigit():
            return compact[:index] + " " + compact[index:]
    return compact


def valid_iata_code(value):
    """Return True only for three-letter airport codes."""
    return isinstance(value, str) and len(value) == 3 and value.isalpha()


# Observation queries
def base_observation_query():
    """Shared SELECT used by the three report searches."""
    return """
        SELECT
            f.flight_date,
            f.delay_seconds,
            f.movement,
            fs.status_en,
            observed.iata AS airport_iata,
            counterpart.iata AS counterpart_iata,
            aircraft.model AS aircraft_model
        FROM flights AS f
        JOIN airports AS observed ON observed.id = f.airport_id
        LEFT JOIN airports AS counterpart
          ON counterpart.id = f.counterpart_airport_id
        LEFT JOIN aircraft ON aircraft.id = f.aircraft_id
        LEFT JOIN flight_statuses AS fs ON fs.id = f.status_id
    """


def get_flight_observations(db, flight_number, start_date):
    """Return one recurring observable event for this number on each date.

    The source can repeat a flight number across later events in the same daily
    rotation. The earliest event is kept per date, then the recurring movement and
    routes are selected using the complete history. The date filter is applied last
    so changing the report period does not change which event the number represents.
    This supports both departures from Argentina and arrivals whose international
    origin is outside the dataset.
    """
    compact = normalize_flight_number(flight_number)
    rows = db.execute(
        base_observation_query()
        + """
        WHERE REPLACE(UPPER(f.flight_number), ' ', '') = ?
        ORDER BY
            f.flight_date,
            f.scheduled_at IS NULL,
            f.scheduled_at,
            f.id
        """,
        compact,
    )

    # Choose a stable meaning for the flight number before filtering by date
    daily_observations = first_observation_each_day(rows)
    same_movement = dominant_movement(daily_observations)
    recurring_routes = recurring_observation_routes(same_movement)

    selected = []
    for row in recurring_routes:
        if row["flight_date"] >= start_date:
            selected.append(row)
    return selected


def first_observation_each_day(rows):
    """Keep the first row for each date from rows ordered by scheduled time."""
    selected = []
    dates_seen = set()

    for row in rows:
        date = row["flight_date"]
        if date not in dates_seen:
            selected.append(row)
            dates_seen.add(date)

    return selected


def dominant_movement(rows):
    """Keep the most frequently observed movement, preferring departures on a tie."""
    counts = {"D": 0, "A": 0}
    for row in rows:
        counts[row["movement"]] += 1

    movement = "D"
    if counts["A"] > counts["D"]:
        movement = "A"

    selected = []
    for row in rows:
        if row["movement"] == movement:
            selected.append(row)
    return selected


def observation_route(row):
    """Return an origin-destination pair for a departure or arrival row."""
    if row["movement"] == "D":
        return row["airport_iata"], row["counterpart_iata"]
    return row["counterpart_iata"], row["airport_iata"]


def recurring_observation_routes(rows):
    """Remove one-date route anomalies when the number has recurring routes."""
    route_counts = {}

    for row in rows:
        route = observation_route(row)
        route_counts[route] = route_counts.get(route, 0) + 1

    if not route_counts or max(route_counts.values()) == 1:
        return rows

    selected = []
    for row in rows:
        route = observation_route(row)
        if route_counts[route] > 1:
            selected.append(row)

    return selected


def get_route_observations(db, origin, destination, start_date):
    # Prefer a departure observed at the requested origin
    departures = db.execute(
        base_observation_query()
        + """
        WHERE f.flight_date >= ?
          AND f.movement = 'D'
          AND observed.iata = ?
          AND counterpart.iata = ?
        ORDER BY f.flight_date
        """,
        start_date,
        origin,
        destination,
    )
    if departures:
        return departures

    # International origins may only appear as an arrival at the destination
    return db.execute(
        base_observation_query()
        + """
        WHERE f.flight_date >= ?
          AND f.movement = 'A'
          AND counterpart.iata = ?
          AND observed.iata = ?
        ORDER BY f.flight_date
        """,
        start_date,
        origin,
        destination,
    )


def get_airline_observations(db, airline_code, start_date):
    return db.execute(
        base_observation_query()
        + """
        JOIN airlines AS airline ON airline.id = f.airline_id
        WHERE UPPER(airline.iata) = ?
          AND f.flight_date >= ?
          AND f.movement = 'D'
        ORDER BY f.flight_date
        """,
        airline_code,
        start_date,
    )


# Report calculations
def median(values):
    """Return the middle value of a sorted list."""
    if not values:
        return None

    ordered = sorted(values)
    middle = len(ordered) // 2

    if len(ordered) % 2 == 1:
        return ordered[middle]

    return (ordered[middle - 1] + ordered[middle]) / 2


def format_percentage(value):
    """Format a rate without rounding a positive value down to zero."""
    if 0 < value < 0.1:
        return "<0.1%"
    return f"{value:.1f}%"


def performance_label(on_time_rate, usable_observations):
    """Return the translation key and color used for a performance result."""
    if usable_observations < 10:
        return "insufficient_data", "neutral"
    if on_time_rate >= 80:
        return "usually_near_schedule", "good"
    if on_time_rate >= 65:
        return "mixed_performance", "warning"
    return "often_late", "bad"


def calculate_metrics(rows, on_time_limit_seconds=DEPARTURE_ON_TIME_LIMIT_SECONDS):
    """Calculate all report metrics with explicit, explainable rules."""
    # Count each source status before calculating percentages
    scheduled = 0
    cancelled = 0
    diverted = 0
    on_time = 0
    delays = []

    for row in rows:
        status = (row.get("status_en") or "").upper()

        if status == "NO OPERA":
            continue

        scheduled += 1

        if status == "CANCELLED":
            cancelled += 1
            continue

        # A diversion did not complete the scheduled movement as planned. It is
        # assessed as outside the timing threshold even when the source happens to
        # provide an event time, but that time is not used as a route delay.
        if status == "DIVERTED":
            diverted += 1
            continue

        delay = row.get("delay_seconds")
        if delay is None:
            continue

        # Long positive delays can be genuine and remain in the result. Very large
        # negative values are normally a stale or mismatched date in the source, not
        # a flight that operated many hours early.
        if delay < -MAX_VALID_EARLY_SECONDS:
            continue

        delays.append(delay)
        if delay <= on_time_limit_seconds:
            on_time += 1

    # A diverted flight is usable, but it is outside the on-time threshold
    usable = len(delays) + diverted
    on_time_rate = 0
    if usable:
        on_time_rate = on_time * 100 / usable

    # Cancellation and diversion rates use all scheduled observations
    cancellation_rate = 0
    diversion_rate = 0
    if scheduled:
        cancellation_rate = cancelled * 100 / scheduled
        diversion_rate = diverted * 100 / scheduled

    median_delay = None
    if delays:
        median_delay = median(delays) / 60

    label_key, tone = performance_label(on_time_rate, usable)

    return {
        "observations": len(rows),
        "usable": usable,
        "cancelled": cancelled,
        "diverted": diverted,
        "on_time_rate": round(on_time_rate, 1),
        "on_time_rate_display": format_percentage(on_time_rate),
        "cancellation_rate_display": format_percentage(cancellation_rate),
        "diversion_rate_display": format_percentage(diversion_rate),
        "median_delay": round(median_delay, 1)
        if median_delay is not None
        else None,
        "label_key": label_key,
        "tone": tone,
    }


# Extra summaries shown below the main performance result
def route_pairs(rows):
    """Build origin-destination pairs from the observed movement."""
    pairs = set()
    for row in rows:
        origin, destination = observation_route(row)

        if valid_iata_code(origin) and valid_iata_code(destination):
            pairs.add((origin, destination))

    labels = []
    for origin, destination in sorted(pairs):
        labels.append(origin + " → " + destination)
    return labels


def invalid_route_count(rows):
    """Count observations whose origin or destination has no valid IATA code."""
    invalid = 0
    for row in rows:
        origin, destination = observation_route(row)
        if not valid_iata_code(origin) or not valid_iata_code(destination):
            invalid += 1
    return invalid


def monthly_trend(rows, on_time_limit_seconds):
    """Group observations by month for simple CSS charts."""
    groups = {}

    for row in rows:
        month = row["flight_date"][:7]
        if month not in groups:
            groups[month] = []
        groups[month].append(row)

    result = []
    for month in sorted(groups):
        metrics = calculate_metrics(groups[month], on_time_limit_seconds)
        result.append(
            {
                "month": month,
                "on_time_rate": metrics["on_time_rate"],
                "usable": metrics["usable"],
            }
        )
    return result


def aircraft_summary(rows, limit=4):
    """Summarize aircraft models recorded with a group of observations.

    Equipment is descriptive context only: aircraft assignments can change between
    flights, so the result deliberately describes recorded observations rather than
    a future flight's assigned aircraft.
    """
    counts = {}
    identified = 0

    # Ignore empty or ambiguous model names before counting them
    for row in rows:
        model = normalize_aircraft_model(row.get("aircraft_model"))
        if not model:
            continue
        identified += 1
        counts[model] = counts.get(model, 0) + 1

    models = []
    for model, records in sorted(
        counts.items(), key=lambda item: (-item[1], item[0])
    )[:limit]:
        share = records * 100 / identified
        models.append(
            {
                "model": model,
                "records": records,
                "share": round(share, 1),
            }
        )

    return {
        "identified": identified,
        "models": models,
    }


def normalize_aircraft_model(model):
    """Return a trustworthy aircraft model name or None for malformed values.

    The source sometimes concatenates model names without a separator. Exact repeated
    names can be safely collapsed; combinations of different models are discarded
    because selecting one would misrepresent the source data.
    """
    if not model or not model.strip():
        return None

    model = model.strip()
    starts = []

    # Find where each possible aircraft name begins
    for index in range(len(model)):
        for prefix in AIRCRAFT_MODEL_PREFIXES:
            if model.startswith(prefix, index):
                starts.append(index)
                break

    if len(starts) < 2:
        return model

    parts = []
    for index in range(len(starts)):
        start = starts[index]
        if index + 1 < len(starts):
            end = starts[index + 1]
        else:
            end = len(model)
        parts.append(model[start:end].strip())

    if len(set(parts)) == 1:
        return parts[0]
    return None


def build_report(rows):
    # Arrivals and departures share a template but use their own threshold
    movement = "D"
    if rows:
        movement = rows[0]["movement"]

    if movement == "A":
        threshold_seconds = ARRIVAL_ON_TIME_LIMIT_SECONDS
    else:
        threshold_seconds = DEPARTURE_ON_TIME_LIMIT_SECONDS

    return {
        "total_observations": len(rows),
        "performance": calculate_metrics(rows, threshold_seconds),
        "movement": movement,
        "threshold_minutes": threshold_seconds // 60,
        "trend": monthly_trend(rows, threshold_seconds),
        "routes": route_pairs(rows),
        "invalid_route_observations": invalid_route_count(rows),
        "aircraft": aircraft_summary(rows),
    }
