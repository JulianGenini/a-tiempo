"""Flask entry point for A Tiempo?.

Developed with assistance from OpenAI Codex.
"""

from pathlib import Path

from cs50 import SQL
from flask import Flask, render_template, request

from analytics import (
    build_report,
    display_flight_number,
    get_airline_observations,
    get_airlines,
    get_airports,
    get_flight_observations,
    get_overview,
    get_route_observations,
    get_start_date,
    format_date,
    normalize_flight_number,
    normalize_period,
)
app = Flask(__name__)

PROJECT_DIRECTORY = Path(__file__).resolve().parent
DATABASE_PATH = PROJECT_DIRECTORY / "database" / "flights.db"
db = SQL("sqlite:///" + str(DATABASE_PATH))


def render_error(message, status=400):
    return render_template("error.html", message=message), status


def valid_iata(value):
    return len(value) == 3 and value.isalpha()


def report_context(rows, period):
    start_date, end_date = get_start_date(db, period)
    return {
        "report": build_report(rows),
        "period": period,
        "start_date": start_date,
        "end_date": end_date,
    }


@app.route("/flight")
def flight_report():
    number = request.args.get("number", "")
    period = normalize_period(request.args.get("period", "365"))
    compact = normalize_flight_number(number)

    if not compact:
        return render_error("Enter a flight number, such as AR1400.")

    start_date, end_date = get_start_date(db, period)
    rows = get_flight_observations(db, compact, start_date)
    if not rows:
        return render_error("No historical observations match that flight.", 404)

    context = report_context(rows, period)
    if context["report"]["movement"] == "A":
        description = "See how reliably this inbound service landed compared with its scheduled arrival time."
    else:
        description = "See how often this service departed close to its scheduled time."
    context.update(
        {
            "title": display_flight_number(compact),
            "eyebrow": "Flight history",
            "description": description,
            "form_action": "flight_report",
            "hidden_fields": {"number": display_flight_number(compact)},
        }
    )
    return render_template("report.html", **context)


@app.route("/route")
def route_report():
    origin = request.args.get("origin", "").strip().upper()
    destination = request.args.get("destination", "").strip().upper()
    period = normalize_period(request.args.get("period", "365"))

    if not valid_iata(origin) or not valid_iata(destination):
        return render_error("Origin and destination must be three-letter IATA codes.")
    if origin == destination:
        return render_error("Origin and destination must be different.")

    start_date, end_date = get_start_date(db, period)
    rows = get_route_observations(db, origin, destination, start_date)
    if not rows:
        return render_error("No historical observations match that route.", 404)

    context = report_context(rows, period)
    if context["report"]["movement"] == "A":
        description = "See arrival performance for this international inbound route."
    else:
        description = "See departure performance for flights from this origin to this destination."
    context.update(
        {
            "title": origin + " → " + destination,
            "eyebrow": "Route history",
            "description": description,
            "form_action": "route_report",
            "hidden_fields": {
                "origin": origin,
                "destination": destination,
            },
        }
    )
    return render_template("report.html", **context)


@app.route("/airline")
def airline_report():
    code = request.args.get("code", "").strip().upper()
    period = normalize_period(request.args.get("period", "365"))

    if not code or len(code) > 3:
        return render_error("Enter a valid airline IATA code.")

    start_date, end_date = get_start_date(db, period)
    rows = get_airline_observations(db, code, start_date)
    if not rows:
        return render_error("No historical observations match that airline.", 404)

    airline_name = code
    for airline in get_airlines(db):
        if airline["iata"].upper() == code:
            airline_name = airline["name"]
            break

    context = report_context(rows, period)
    context.update(
        {
            "title": code + " · " + airline_name.title(),
            "eyebrow": "Airline history",
            "description": "See departure performance across this airline's flights recorded in the database.",
            "form_action": "airline_report",
            "hidden_fields": {"code": code},
        }
    )
    return render_template("report.html", **context)


def parse_route_item(value):
    cleaned = value.upper().replace("/", "-").replace(" ", "")
    parts = cleaned.split("-")
    if len(parts) != 2:
        return None
    if not valid_iata(parts[0]) or not valid_iata(parts[1]):
        return None
    return parts[0], parts[1]


def comparison_result(kind, item, start_date):
    if kind == "flight":
        compact = normalize_flight_number(item)
        if not compact:
            return None
        rows = get_flight_observations(db, compact, start_date)
        title = display_flight_number(compact)
    elif kind == "airline":
        code = item.strip().upper()
        if not code or len(code) > 3:
            return None
        rows = get_airline_observations(db, code, start_date)
        title = code
    else:
        route = parse_route_item(item)
        if route is None:
            return None
        origin, destination = route
        rows = get_route_observations(db, origin, destination, start_date)
        title = origin + " → " + destination

    if not rows:
        return None
    return {
        "title": title,
        "route": route if kind == "route" else None,
        "report": build_report(rows),
    }


@app.route("/compare")
def compare():
    kind = request.args.get("kind", "flight")
    period = normalize_period(request.args.get("period", "365"))
    if kind not in {"flight", "route", "airline"}:
        kind = "flight"

    items = []
    for name in ("item1", "item2", "item3"):
        value = request.args.get(name, "").strip()
        if value:
            items.append(value)

    results = []
    error = None
    start_date, end_date = get_start_date(db, period)

    if items:
        if len(items) < 2:
            error = "Enter at least two items to compare."
        else:
            for item in items:
                result = comparison_result(kind, item, start_date)
                if result is None:
                    error = "One or more comparison items are invalid or have no data."
                    results = []
                    break
                results.append(result)

    movements = []
    for result in results:
        movement = result["report"]["movement"]
        if movement not in movements:
            movements.append(movement)
    mixed_movements = len(movements) > 1

    return render_template(
        "compare.html",
        kind=kind,
        period=period,
        items=items,
        results=results,
        error=error,
        mixed_movements=mixed_movements,
        start_date=start_date,
        end_date=end_date,
    )


@app.route("/")
def home():
    panel = request.args.get("panel", "flight")
    if panel not in {"flight", "route", "airline"}:
        panel = "flight"
    return render_template(
        "home.html",
        panel=panel,
        overview=get_overview(db),
        airports=get_airports(db),
        airlines=get_airlines(db),
    )


@app.route("/methodology")
def methodology():
    first_date, last_date = get_start_date(db, "all")
    return render_template(
        "methodology.html",
        first_date=format_date(first_date),
        last_date=format_date(last_date),
    )


@app.errorhandler(404)
def not_found(error):
    return render_error("The requested page does not exist.", 404)


if __name__ == "__main__":
    app.run()
