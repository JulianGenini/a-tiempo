"""English and Spanish interface text for A Tiempo?.

Developed with assistance from OpenAI Codex.
"""

from datetime import datetime


# The language selector only accepts these two codes
SUPPORTED_LANGUAGES = {"en", "es"}


# Each key keeps the English and Spanish version of the same interface text
TEXT = {
    "meta_description": {
        "en": "Explore historical flight performance observed at Argentine airports.",
        "es": "Explorá el desempeño histórico de vuelos observados en aeropuertos argentinos.",
    },
    "skip_content": {"en": "Skip to content", "es": "Saltar al contenido"},
    "main_navigation": {"en": "Main navigation", "es": "Navegación principal"},
    "brand_home": {"en": "A Tiempo? home", "es": "Inicio de A Tiempo?"},
    "brand_tagline": {"en": "Airports movements explorer", "es": "Explorador de movimientos aeroportuarios"},
    "open_navigation": {"en": "Open navigation", "es": "Abrir navegación"},
    "home_nav": {"en": "Home", "es": "Inicio"},
    "compare_nav": {"en": "Compare", "es": "Comparar"},
    "methodology_nav": {"en": "How it works", "es": "Cómo funciona"},
    "language_selector": {"en": "Language", "es": "Idioma"},
    "dataset_title": {
        "en": "Argentina-only historical dataset:",
        "es": "Base de datos limitada a Argentina:",
    },
    "dataset_text": {
        "en": "movements observed at Argentine airports, from December 23, 2024 through July 29, 2026.",
        "es": "movimientos observados en aeropuertos argentinos, desde el 23 de diciembre de 2024 al 29 de julio de 2026.",
    },
    "footer_description": {
        "en": "A CS50x final project for exploring flights, routes, and punctuality through historical records from Argentine airports.",
        "es": "Un proyecto final de CS50x para explorar vuelos, rutas y puntualidad a partir de registros históricos de aeropuertos argentinos.",
    },
    "footer_notice": {
        "en": "For current flight information, always check with the airline or airport.",
        "es": "Para información sobre tu vuelo, consultá siempre a la aerolínea o al aeropuerto.",
    },
    "footer_credit": {"en": "Created by Julian Genini", "es": "Creado por Julian Genini"},
    "home_title": {"en": "Home", "es": "Inicio"},
    "hero_eyebrow": {
        "en": "Historical movements observed at Argentine airports",
        "es": "Movimientos históricos observados en aeropuertos argentinos",
    },
    "hero_title": {
        "en": "Compare flights. Plan better.",
        "es": "Compará vuelos. Planeá mejor.",
    },
    "hero_description": {
        "en": "See historical takeoff or landing delays, cancellations, schedules and the aircraft commonly recorded for each service.",
        "es": "Consultá demoras históricas de despegue o aterrizaje, cancelaciones, horarios y las aeronaves registradas con mayor frecuencia para cada servicio.",
    },
    "search_database": {"en": "Search the database", "es": "Buscar en la base de datos"},
    "database_summary": {"en": "Database summary", "es": "Resumen de la base de datos"},
    "built_from_history": {"en": "Based on historical airport movements", "es": "Basado en historial de movimientos aeroportuarios"},
    "movements_count": {"en": "recorded movements", "es": "movimientos registrados"},
    "airports_connected": {"en": "airports connected", "es": "aeropuertos conectados"},
    "airlines_represented": {"en": "airlines represented", "es": "aerolíneas representadas"},
    "search": {"en": "Search", "es": "Buscar"},
    "choose_search": {"en": "Choose how you want to search", "es": "Elegí cómo querés buscar"},
    "flight_number": {"en": "Flight number", "es": "Número de vuelo"},
    "route": {"en": "Route", "es": "Ruta"},
    "airline": {"en": "Airline", "es": "Aerolínea"},
    "lookup_flight": {"en": "Look up a flight", "es": "Buscá un vuelo"},
    "lookup_flight_help": {
        "en": "Enter the airline code and flight number to view its history.",
        "es": "Ingresá el código de la aerolínea y el número de vuelo para ver su historial.",
    },
    "view_history": {"en": "View history", "es": "Ver historial"},
    "try_example": {"en": "Try an example:", "es": "Probá un ejemplo:"},
    "select_direction": {"en": "Select a direction", "es": "Elegí un sentido"},
    "direction_help": {
        "en": "A → B and B → A are treated as different routes.",
        "es": "A → B y B → A se consideran rutas diferentes.",
    },
    "origin": {"en": "Origin", "es": "Origen"},
    "destination": {"en": "Destination", "es": "Destino"},
    "choose_airport": {"en": "Choose airport", "es": "Elegí un aeropuerto"},
    "unknown": {"en": "Unknown", "es": "Desconocido"},
    "view_airline": {"en": "View airline activity", "es": "Consultá la actividad de una aerolínea"},
    "view_airline_help": {
        "en": "This includes all recorded departures for the selected airline during the chosen period.",
        "es": "Incluye todas las partidas registradas para la aerolínea durante el período elegido.",
    },
    "choose_airline": {"en": "Choose airline", "es": "Elegí una aerolínea"},
    "arrival_based": {"en": "Arrival-based", "es": "Basado en llegadas"},
    "departure_not_covered": {
        "en": "departure not covered by dataset",
        "es": "partida no cubierta por la base de datos",
    },
    "performance_result": {"en": "Punctuality summary", "es": "Resumen de puntualidad"},
    "observed_performance": {"en": "Observed punctuality", "es": "Puntualidad observada"},
    "usually_near_schedule": {"en": "Usually near schedule", "es": "Generalmente cerca del horario"},
    "mixed_performance": {"en": "Mixed punctuality", "es": "Puntualidad irregular"},
    "often_late": {
        "en": "Often more than {minutes} minutes late",
        "es": "Frecuentemente más de {minutes} minutos tarde",
    },
    "insufficient_data": {"en": "Insufficient data", "es": "Datos insuficientes"},
    "departures": {"en": "Departures", "es": "Partidas"},
    "arrivals": {"en": "Arrivals", "es": "Llegadas"},
    "no_departures": {
        "en": "No departures were recorded for this search.",
        "es": "No se registraron partidas para esta búsqueda.",
    },
    "no_arrivals": {
        "en": "No arrivals were recorded for this search.",
        "es": "No se registraron llegadas para esta búsqueda.",
    },
    "departed_within": {
        "en": "took off within {minutes} minutes of schedule",
        "es": "despegó dentro de los {minutes} minutos del horario previsto",
    },
    "arrived_within": {
        "en": "landed within {minutes} minutes of schedule",
        "es": "aterrizó dentro de los {minutes} minutos del horario previsto",
    },
    "flights_analysed": {"en": "Flights analysed", "es": "Vuelos analizados"},
    "cancelled": {"en": "Cancelled", "es": "Cancelados"},
    "diverted": {"en": "Diverted", "es": "Desviados"},
    "none_recorded": {"en": "None recorded", "es": "Ninguno registrado"},
    "typical_departure": {"en": "Typical departure", "es": "Partida típica"},
    "typical_arrival": {"en": "Typical arrival", "es": "Llegada típica"},
    "minutes_late": {"en": "{value} min late", "es": "{value} min tarde"},
    "minutes_early": {"en": "{value} min early", "es": "{value} min antes"},
    "on_schedule": {"en": "On schedule", "es": "En horario"},
    "calculation_note": {
        "en": "Calculated from movements with valid timing data, including recorded diversions.",
        "es": "El cálculo se basa en movimientos con datos horarios válidos e incluye desvíos registrados.",
    },
    "read_methodology": {"en": "Read Methodology", "es": "Leer la metodología"},
    "dates_to_include": {"en": "Dates to include", "es": "Fechas a incluir"},
    "last_90_days": {"en": "Last 90 days in database", "es": "Últimos 90 días de la base de datos"},
    "last_365_days": {"en": "Last 365 days in database", "es": "Últimos 365 días de la base de datos"},
    "every_date": {"en": "Every stored date", "es": "Todas las fechas guardadas"},
    "update": {"en": "Update", "es": "Actualizar"},
    "departure_observations": {
        "en": "departure observations found",
        "es": "movimientos de partida registrados",
    },
    "departure_observation": {
        "en": "departure observation found",
        "es": "movimiento de partida registrado",
    },
    "arrival_observations": {
        "en": "arrival observations found",
        "es": "movimientos de llegada registrados",
    },
    "arrival_observation": {
        "en": "arrival observation found",
        "es": "movimiento de llegada registrado",
    },
    "route_coverage": {"en": "Route coverage", "es": "Cobertura de rutas"},
    "route_recorded": {"en": "{count} route recorded", "es": "{count} ruta registrada"},
    "routes_recorded": {"en": "{count} routes recorded", "es": "{count} rutas registradas"},
    "browse_routes": {"en": "Browse routes", "es": "Ver rutas"},
    "invalid_counterpart_one": {
        "en": "record has no valid counterpart IATA code",
        "es": "registro no tiene un código IATA de contraparte válido",
    },
    "invalid_counterpart_many": {
        "en": "records have no valid counterpart IATA code",
        "es": "registros no tienen un código IATA de contraparte válido",
    },
    "all_routes": {"en": "All recorded routes", "es": "Todas las rutas registradas"},
    "unique_direction": {"en": "{count} unique direction in this report.", "es": "{count} sentido único en este informe."},
    "unique_directions": {"en": "{count} unique directions in this report.", "es": "{count} sentidos únicos en este informe."},
    "close_route_list": {"en": "Close route list", "es": "Cerrar lista de rutas"},
    "month_by_month": {"en": "Month by month", "es": "Mes a mes"},
    "performance_over_time": {"en": "Did punctuality change over time?", "es": "¿Cambió la puntualidad con el tiempo?"},
    "longer_bar": {
        "en": "A longer bar means more flights were within {minutes} minutes of schedule.",
        "es": "Una barra más larga indica que más vuelos estuvieron dentro de los {minutes} minutos del horario.",
    },
    "view_details": {"en": "View details", "es": "Ver detalles"},
    "month": {"en": "Month", "es": "Mes"},
    "within_minutes": {"en": "Within {minutes} min", "es": "Dentro de {minutes} min"},
    "sample_size": {"en": "Sample size", "es": "Tamaño de muestra"},
    "flight": {"en": "flight", "es": "vuelo"},
    "flights": {"en": "flights", "es": "vuelos"},
    "no_monthly_history": {
        "en": "There is not enough information to build a monthly history.",
        "es": "No hay información suficiente para construir un historial mensual.",
    },
    "aircraft_context": {"en": "Aircraft data", "es": "Datos de aeronaves"},
    "common_aircraft": {"en": "Commonly recorded aircraft", "es": "Aeronaves registradas con mayor frecuencia"},
    "equipment_context": {
        "en": "Equipment can change. This is historical context, not the aircraft assigned to a future flight.",
        "es": "El equipo puede cambiar. Este es un contexto histórico, no la aeronave asignada a un vuelo futuro.",
    },
    "aircraft_available": {
        "en": "Aircraft data available for",
        "es": "Datos de aeronaves disponibles para",
    },
    "of_flight": {"en": "of {count} flight", "es": "de {count} vuelo"},
    "of_flights": {"en": "of {count} flights", "es": "de {count} vuelos"},
    "historical_record": {"en": "{count} historical record", "es": "{count} registro histórico"},
    "historical_records": {"en": "{count} historical records", "es": "{count} registros históricos"},
    "of_identified_aircraft": {"en": "of identified aircraft records", "es": "de los registros con aeronave identificada"},
    "no_aircraft": {
        "en": "No aircraft model was recorded for this search.",
        "es": "No se registró ningún modelo de aeronave para esta búsqueda.",
    },
    "compare_title": {"en": "Compare", "es": "Comparar"},
    "compare_same_period": {"en": "Compare the same period", "es": "Compará el mismo período"},
    "compare_heading": {"en": "Compare punctuality.", "es": "Compará la puntualidad."},
    "compare_description": {
        "en": "Compare the historical on-time performance of up to three flights, routes, or airlines.",
        "es": "Compará la puntualidad histórica de hasta tres vuelos, rutas o aerolíneas.",
    },
    "what_comparing": {"en": "What are you comparing?", "es": "¿Qué querés comparar?"},
    "flight_plural": {"en": "Flights", "es": "Vuelos"},
    "route_plural": {"en": "Routes", "es": "Rutas"},
    "airline_plural": {"en": "Airlines", "es": "Aerolíneas"},
    "choice": {"en": "Choice {number}", "es": "Opción {number}"},
    "optional": {"en": "optional", "es": "opcional"},
    "compare_hint_flight": {"en": "Example: AR 1458", "es": "Ejemplo: AR 1458"},
    "compare_hint_route": {
        "en": "Use ORIGIN-DESTINATION, for example AEP-COR.",
        "es": "Usá ORIGEN-DESTINO, por ejemplo AEP-COR.",
    },
    "compare_hint_airline": {
        "en": "Use an airline IATA code, for example AR.",
        "es": "Usá el código IATA de una aerolínea, por ejemplo AR.",
    },
    "compare_button": {"en": "Compare", "es": "Comparar"},
    "comparison_result": {"en": "Comparison result", "es": "Resultado de la comparación"},
    "within_schedule": {
        "en": "within {minutes} minutes of schedule",
        "es": "dentro de los {minutes} minutos del horario",
    },
    "mixed_comparison": {
        "en": "These results use different observed events. Departures compare takeoff with schedule, while international arrivals compare landing with schedule when their origin is outside the Argentine airport dataset. Both use a 30-minute threshold.",
        "es": "Estos resultados usan diferentes eventos observados. Las partidas comparan real del despegue con el horario previsto, mientras que las llegadas internacionales comparan el horario de aterrizaje con el horario previsto cuando su origen está fuera de la base de datos de aeropuertos argentinos. Ambas usan un margen de 30 minutos.",
    },
    "item": {"en": "Item", "es": "Elemento"},
    "on_time": {"en": "On time", "es": "Dentro del margen"},
    "typical_difference": {"en": "Typical difference", "es": "Diferencia típica"},
    "methodology_title": {"en": "Methodology", "es": "Metodología"},
    "error_title": {"en": "Unable to complete request", "es": "No se pudo completar la solicitud"},
    "request_not_completed": {"en": "Request not completed", "es": "Solicitud no completada"},
    "return_home": {"en": "Return home", "es": "Volver al inicio"},
    "error_enter_flight": {
        "en": "Enter a flight number, such as AR1400.",
        "es": "Ingresá un número de vuelo, por ejemplo AR1400.",
    },
    "error_no_flight": {
        "en": "No historical observations match that flight.",
        "es": "No hay observaciones históricas para ese vuelo.",
    },
    "error_iata": {
        "en": "Origin and destination must be three-letter IATA codes.",
        "es": "El origen y el destino deben ser códigos IATA de tres letras.",
    },
    "error_same_airport": {
        "en": "Origin and destination must be different.",
        "es": "El origen y el destino deben ser diferentes.",
    },
    "error_no_route": {
        "en": "No historical observations match that route.",
        "es": "No hay observaciones históricas para esa ruta.",
    },
    "error_airline": {
        "en": "Enter a valid airline IATA code.",
        "es": "Ingresá un código IATA de aerolínea válido.",
    },
    "error_no_airline": {
        "en": "No historical observations match that airline.",
        "es": "No hay observaciones históricas para esa aerolínea.",
    },
    "error_compare_minimum": {
        "en": "Enter at least two items to compare.",
        "es": "Ingresá al menos dos elementos para comparar.",
    },
    "error_compare_invalid": {
        "en": "One or more comparison items are invalid or have no data.",
        "es": "Uno o más elementos son inválidos o no tienen datos.",
    },
    "error_not_found": {
        "en": "The requested page does not exist.",
        "es": "La página solicitada no existe.",
    },
    "flight_history": {"en": "Flight history", "es": "Historial del vuelo"},
    "route_history": {"en": "Route history", "es": "Historial de la ruta"},
    "airline_history": {"en": "Airline history", "es": "Historial de la aerolínea"},
    "flight_arrival_description": {
        "en": "See how reliably this inbound service landed compared with its scheduled arrival time.",
        "es": "Consultá con qué regularidad este servicio entrante aterrizó respecto de su horario previsto de llegada.",
    },
    "flight_departure_description": {
        "en": "See how often this service departed close to its scheduled time.",
        "es": "Consultá con qué frecuencia este servicio despegó cerca de su horario previsto.",
    },
    "route_arrival_description": {
        "en": "See arrival performance for this international inbound route.",
        "es": "Consultá la puntualidad de llegada de esta ruta internacional entrante.",
    },
    "route_departure_description": {
        "en": "See departure performance for flights from this origin to this destination.",
        "es": "Consultá la puntualidad de las partidas entre este origen y este destino.",
    },
    "airline_description": {
        "en": "See departure performance across this airline's flights recorded in the database.",
        "es": "Consultá la puntualidad de las partidas de esta aerolínea registradas en la base de datos.",
    },
}


# strftime does not translate month names, so Spanish months are stored here
SPANISH_MONTHS = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)


def normalize_language(value):
    """Return a supported language code, defaulting to English."""
    if value in SUPPORTED_LANGUAGES:
        return value
    return "en"


def translate(key, language="en", **values):
    """Return translated interface text and interpolate named values."""
    language = normalize_language(language)
    text = TEXT[key][language]
    return text.format(**values)


def format_date(value, language="en"):
    """Format an ISO date in the selected interface language."""
    date = datetime.strptime(value, "%Y-%m-%d")
    if normalize_language(language) == "es":
        return f"{date.day} de {SPANISH_MONTHS[date.month - 1]} de {date.year}"
    return str(date.day) + date.strftime(" %b %Y")


def format_number(value, language="en"):
    """Format an integer with the locale's thousands separator."""
    result = f"{value:,}"
    if normalize_language(language) == "es":
        return result.replace(",", ".")
    return result


def format_numeric_text(value, language="en"):
    """Use a decimal comma for preformatted Spanish percentages and values."""
    result = str(value)
    if normalize_language(language) == "es":
        return result.replace(".", ",")
    return result
