"""Database queries and schedule-performance calculations for A Tiempo?.

Developed with assistance from OpenAI Codex.
"""

from datetime import datetime, timedelta


VALID_PERIODS = {"90", "365", "all"}
MAX_VALID_DELAY_SECONDS = 6 * 60 * 60
DEPARTURE_ON_TIME_LIMIT_SECONDS = 30 * 60
ARRIVAL_ON_TIME_LIMIT_SECONDS = 15 * 60


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
            COUNT(*) AS flights,
            COUNT(DISTINCT flight_date) AS days,
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
        WHERE movement = 'D'
        """
    )
    first_date, last_date = get_dataset_dates(db)
    overview = rows[0]
    overview["first_date"] = first_date
    overview["last_date"] = last_date
    overview["first_date_label"] = format_date(first_date)
    overview["last_date_label"] = format_date(last_date)
    return overview


def format_date(value):
    """Format an ISO date for the compact home-page data snapshot."""
    date = datetime.strptime(value, "%Y-%m-%d")
    return str(date.day) + date.strftime(" %b %Y")


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


def base_observation_query():
    """Shared SELECT used by the three report searches."""
    return """
        SELECT
            f.flight_date,
            f.delay_seconds,
            f.movement,
            f.flight_number,
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


def median(values):
    """Return the middle value of a sorted list."""
    if not values:
        return None

    ordered = sorted(values)
    middle = len(ordered) // 2

    if len(ordered) % 2 == 1:
        return ordered[middle]

    return (ordered[middle - 1] + ordered[middle]) / 2


def performance_label(on_time_rate, usable_observations, threshold_minutes):
    if usable_observations < 10:
        return "Insufficient data", "neutral"
    if on_time_rate >= 80:
        return "Often near schedule", "good"
    if on_time_rate >= 65:
        return "Mixed timing", "warning"
    return "Often more than " + str(threshold_minutes) + " min late", "bad"


def calculate_metrics(rows, on_time_limit_seconds=DEPARTURE_ON_TIME_LIMIT_SECONDS):
    """Calculate all report metrics with explicit, explainable rules."""
    scheduled = 0
    cancelled = 0
    not_operating = 0
    excluded_outliers = 0
    on_time = 0
    delays = []

    for row in rows:
        status = row.get("status_en")

        if status == "NO OPERA":
            not_operating += 1
            continue

        scheduled += 1

        if status == "Cancelled":
            cancelled += 1
            continue

        delay = row.get("delay_seconds")
        if delay is None:
            continue

        if abs(delay) > MAX_VALID_DELAY_SECONDS:
            excluded_outliers += 1
            continue

        delays.append(delay)
        if delay <= on_time_limit_seconds:
            on_time += 1

    usable = len(delays)
    on_time_rate = 0
    if usable:
        on_time_rate = on_time * 100 / usable

    cancellation_rate = 0
    if scheduled:
        cancellation_rate = cancelled * 100 / scheduled

    average_delay = None
    median_delay = None
    if delays:
        average_delay = sum(delays) / len(delays) / 60
        median_delay = median(delays) / 60

    threshold_minutes = on_time_limit_seconds // 60
    label, tone = performance_label(on_time_rate, usable, threshold_minutes)

    return {
        "observations": len(rows),
        "scheduled": scheduled,
        "usable": usable,
        "cancelled": cancelled,
        "not_operating": not_operating,
        "excluded_outliers": excluded_outliers,
        "on_time": on_time,
        "on_time_rate": round(on_time_rate, 1),
        "cancellation_rate": round(cancellation_rate, 1),
        "average_delay": round(average_delay, 1)
        if average_delay is not None
        else None,
        "median_delay": round(median_delay, 1)
        if median_delay is not None
        else None,
        "label": label,
        "tone": tone,
    }


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
                "bar_width": metrics["on_time_rate"],
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

    for row in rows:
        model = row.get("aircraft_model")
        if not model or not model.strip():
            continue
        model = model.strip()
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
        "missing": len(rows) - identified,
        "models": models,
    }


def build_report(rows):
    movement = "D"
    if rows:
        movement = rows[0]["movement"]

    if movement == "A":
        threshold_seconds = ARRIVAL_ON_TIME_LIMIT_SECONDS
        movement_name = "Arrivals"
        movement_label = "arrival"
        event_verb = "landed"
        scheduled_code = "STA"
        actual_code = "ATA"
    else:
        threshold_seconds = DEPARTURE_ON_TIME_LIMIT_SECONDS
        movement_name = "Departures"
        movement_label = "departure"
        event_verb = "took off"
        scheduled_code = "STD"
        actual_code = "ATD"

    return {
        "total_observations": len(rows),
        "performance": calculate_metrics(rows, threshold_seconds),
        "movement": movement,
        "movement_name": movement_name,
        "movement_label": movement_label,
        "event_verb": event_verb,
        "threshold_minutes": threshold_seconds // 60,
        "scheduled_code": scheduled_code,
        "actual_code": actual_code,
        "trend": monthly_trend(rows, threshold_seconds),
        "routes": route_pairs(rows),
        "invalid_route_observations": invalid_route_count(rows),
        "aircraft": aircraft_summary(rows),
    }
