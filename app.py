"""Flask entry point for A Tiempo?.

Developed with assistance from OpenAI Codex.
"""

from pathlib import Path
from urllib.parse import urlencode

from cs50 import SQL
from flask import Flask, render_template, request, url_for

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
    normalize_flight_number,
    normalize_period,
)
from localization import (
    format_date,
    format_number,
    format_numeric_text,
    normalize_language,
    translate,
)
app = Flask(__name__)

PROJECT_DIRECTORY = Path(__file__).resolve().parent
DATABASE_PATH = PROJECT_DIRECTORY / "database" / "flights.db"
db = SQL("sqlite:///" + str(DATABASE_PATH))


def current_language():
    return normalize_language(request.args.get("lang", "en"))


def localized_url_for(endpoint, **values):
    if current_language() == "es":
        values.setdefault("lang", "es")
    return url_for(endpoint, **values)


def language_url(language):
    values = request.args.to_dict(flat=True)
    if normalize_language(language) == "es":
        values["lang"] = "es"
    else:
        values.pop("lang", None)
    query = urlencode(values)
    return request.path + ("?" + query if query else "")


@app.context_processor
def inject_localization():
    language = current_language()
    return {
        "lang": language,
        "t": lambda key, **values: translate(key, language, **values),
        "lurl": localized_url_for,
        "language_url": language_url,
        "number": lambda value: format_number(value, language),
        "numeric": lambda value: format_numeric_text(value, language),
    }


def render_error(message_key, status=400):
    message = translate(message_key, current_language())
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
        return render_error("error_enter_flight")

    start_date, end_date = get_start_date(db, period)
    rows = get_flight_observations(db, compact, start_date)
    if not rows:
        return render_error("error_no_flight", 404)

    context = report_context(rows, period)
    if context["report"]["movement"] == "A":
        description_key = "flight_arrival_description"
    else:
        description_key = "flight_departure_description"
    context.update(
        {
            "title": display_flight_number(compact),
            "eyebrow": translate("flight_history", current_language()),
            "description": translate(description_key, current_language()),
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
        return render_error("error_iata")
    if origin == destination:
        return render_error("error_same_airport")

    start_date, end_date = get_start_date(db, period)
    rows = get_route_observations(db, origin, destination, start_date)
    if not rows:
        return render_error("error_no_route", 404)

    context = report_context(rows, period)
    if context["report"]["movement"] == "A":
        description_key = "route_arrival_description"
    else:
        description_key = "route_departure_description"
    context.update(
        {
            "title": origin + " → " + destination,
            "eyebrow": translate("route_history", current_language()),
            "description": translate(description_key, current_language()),
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
        return render_error("error_airline")

    start_date, end_date = get_start_date(db, period)
    rows = get_airline_observations(db, code, start_date)
    if not rows:
        return render_error("error_no_airline", 404)

    airline_name = code
    for airline in get_airlines(db):
        if airline["iata"].upper() == code:
            airline_name = airline["name"]
            break

    context = report_context(rows, period)
    context.update(
        {
            "title": code + " · " + airline_name.title(),
            "eyebrow": translate("airline_history", current_language()),
            "description": translate("airline_description", current_language()),
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
            error = translate("error_compare_minimum", current_language())
        else:
            for item in items:
                result = comparison_result(kind, item, start_date)
                if result is None:
                    error = translate("error_compare_invalid", current_language())
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
        first_date=format_date(first_date, current_language()),
        last_date=format_date(last_date, current_language()),
    )


@app.errorhandler(404)
def not_found(error):
    return render_error("error_not_found", 404)


if __name__ == "__main__":
    app.run()
