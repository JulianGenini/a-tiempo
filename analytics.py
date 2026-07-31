"""Database queries and schedule-performance calculations for A Tiempo?.

Developed with assistance from OpenAI Codex.
"""

from datetime import datetime, timedelta


VALID_PERIODS = {"90", "365", "all"}
MAX_VALID_DELAY_SECONDS = 6 * 60 * 60
ON_TIME_LIMIT_SECONDS = 15 * 60


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
    compact = normalize_flight_number(flight_number)
    return db.execute(
        base_observation_query()
        + """
        WHERE REPLACE(UPPER(f.flight_number), ' ', '') = ?
          AND f.flight_date >= ?
        ORDER BY f.flight_date
        """,
        compact,
        start_date,
    )


def get_route_observations(db, origin, destination, start_date):
    return db.execute(
        base_observation_query()
        + """
        WHERE f.flight_date >= ?
          AND (
              (
                  f.movement = 'D'
                  AND observed.iata = ?
                  AND counterpart.iata = ?
              )
              OR
              (
                  f.movement = 'A'
                  AND counterpart.iata = ?
                  AND observed.iata = ?
              )
          )
        ORDER BY f.flight_date
        """,
        start_date,
        origin,
        destination,
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


def performance_label(on_time_rate, usable_observations):
    if usable_observations < 10:
        return "Insufficient data", "neutral"
    if on_time_rate >= 80:
        return "Often near schedule", "good"
    if on_time_rate >= 65:
        return "Mixed timing", "warning"
    return "Often more than 15 min late", "bad"


def calculate_metrics(rows):
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
        if delay <= ON_TIME_LIMIT_SECONDS:
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

    label, tone = performance_label(on_time_rate, usable)

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


def movement_rows(rows, movement):
    selected = []
    for row in rows:
        if row["movement"] == movement:
            selected.append(row)
    return selected


def route_pairs(rows):
    """Build origin-destination pairs without mixing arrivals and departures."""
    pairs = set()
    for row in rows:
        if row["movement"] == "D":
            origin = row["airport_iata"]
            destination = row["counterpart_iata"]
        else:
            origin = row["counterpart_iata"]
            destination = row["airport_iata"]

        if origin and destination:
            pairs.add((origin, destination))

    labels = []
    for origin, destination in sorted(pairs):
        labels.append(origin + " → " + destination)
    return labels


def monthly_trend(rows):
    """Group observations by month and movement for simple CSS charts."""
    groups = {}

    for row in rows:
        month = row["flight_date"][:7]
        key = (month, row["movement"])
        if key not in groups:
            groups[key] = []
        groups[key].append(row)

    result = []
    for key in sorted(groups):
        month, movement = key
        metrics = calculate_metrics(groups[key])
        result.append(
            {
                "month": month,
                "movement": movement,
                "movement_label": "Departures"
                if movement == "D"
                else "Arrivals",
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
    departures = movement_rows(rows, "D")
    arrivals = movement_rows(rows, "A")
    return {
        "total_observations": len(rows),
        "departure": calculate_metrics(departures),
        "arrival": calculate_metrics(arrivals),
        "trend": monthly_trend(rows),
        "routes": route_pairs(rows),
        "aircraft": aircraft_summary(rows),
    }
