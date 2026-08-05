"""Integration tests for Flask routes using the included database.

Developed with assistance from OpenAI Codex.
"""

import unittest

from app import app


class AppTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Compare flights. Plan better.", response.data)
        self.assertIn(b"aircraft", response.data)
        self.assertIn(b"movements observed at Argentine airports", response.data)
        self.assertIn(b"Argentina-only historical dataset", response.data)
        self.assertIn(b"Choose how you want to search", response.data)
        self.assertIn(b"Based on historical airport movements", response.data)
        self.assertIn(b"417K", response.data)
        self.assertIn(b"recorded movements", response.data)
        self.assertIn(b"164", response.data)
        self.assertIn(b"62", response.data)
        self.assertNotIn(b'id="compare-panel"', response.data)
        self.assertIn(b">Compare</a>", response.data)
        self.assertIn(b"December 23, 2024 through July 29, 2026", response.data)

    def test_spanish_home_preserves_language_in_navigation_and_forms(self):
        response = self.client.get("/?lang=es")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<html lang="es">', response.data)
        self.assertIn("Compará vuelos. Planeá mejor.".encode(), response.data)
        self.assertIn("Elegí cómo querés buscar".encode(), response.data)
        self.assertIn("417K".encode(), response.data)
        self.assertIn("movimientos registrados".encode(), response.data)
        self.assertIn(b'href="/compare?lang=es"', response.data)
        self.assertIn(b'href="/methodology?lang=es"', response.data)
        self.assertEqual(
            response.data.count(b'<input type="hidden" name="lang" value="es">'),
            3,
        )

    def test_unknown_language_falls_back_to_english(self):
        response = self.client.get("/?lang=fr")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<html lang="en">', response.data)
        self.assertIn(b"Compare flights. Plan better.", response.data)
        self.assertNotIn("Conocé tu vuelo".encode(), response.data)

    def test_local_bootstrap_files(self):
        with self.client.get("/static/vendor/bootstrap.min.css") as css_response:
            self.assertEqual(css_response.status_code, 200)
            self.assertIn(b"Bootstrap", css_response.data[:200])
        with self.client.get("/static/vendor/bootstrap.bundle.min.js") as js_response:
            self.assertEqual(js_response.status_code, 200)
        with self.client.get("/static/favicon.svg") as favicon_response:
            self.assertEqual(favicon_response.status_code, 200)
            self.assertIn(b"f1c84b", favicon_response.data)

    def test_flight_report(self):
        response = self.client.get("/flight?number=AR+1458&period=365")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Flight history", response.data)
        self.assertIn(b"<strong>113</strong>", response.data)
        self.assertIn(b"departure observations found", response.data)
        self.assertIn(b"2 routes recorded", response.data)
        self.assertNotIn(b"Arrivals", response.data)
        self.assertIn(b"Commonly recorded aircraft", response.data)
        self.assertIn(b"Embraer 190/195", response.data)

    def test_spanish_flight_report_translates_dynamic_results(self):
        response = self.client.get(
            "/flight?number=AR+1458&period=365&lang=es"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Historial del vuelo".encode(), response.data)
        self.assertIn("Partidas".encode(), response.data)
        self.assertIn("Vuelos analizados".encode(), response.data)
        self.assertIn("Partida típica".encode(), response.data)
        self.assertIn(b"80,4%", response.data)
        self.assertIn(b'name="lang" value="es"', response.data)
        self.assertIn(b'href="/methodology?lang=es"', response.data)

    def test_flight_identity_stays_stable_across_periods(self):
        expected_observations = {"90": 7, "365": 49}

        for period, observations in expected_observations.items():
            with self.subTest(period=period):
                response = self.client.get(
                    "/flight?number=5U401&period=" + period
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn(b"Arrivals", response.data)
                self.assertNotIn(b"Departures", response.data)
                self.assertIn(
                    b"<strong>" + str(observations).encode() + b"</strong>",
                    response.data,
                )
                self.assertIn(b"arrival observations found", response.data)

    def test_route_report(self):
        response = self.client.get(
            "/route?origin=AEP&destination=COR&period=365"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AEP", response.data)
        self.assertIn(b"COR", response.data)

    def test_international_inbound_route_uses_arrival(self):
        response = self.client.get(
            "/route?origin=SCL&destination=AEP&period=365"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Arrivals", response.data)
        self.assertIn(b"landed within 30 minutes", response.data)
        self.assertIn(b"SCL", response.data)
        self.assertIn(b"AEP", response.data)

    def test_airline_report(self):
        response = self.client.get("/airline?code=AR&period=90")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Airline history", response.data)

    def test_placeholder_airport_is_not_displayed_as_route(self):
        response = self.client.get("/airline?code=KE&period=365")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"EZE \xe2\x86\x92 --I", response.data)
        self.assertIn(b"no valid counterpart IATA code", response.data)

    def test_rejects_invalid_route(self):
        response = self.client.get("/route?origin=AEP&destination=AEP")
        self.assertEqual(response.status_code, 400)

    def test_methodology_explains_off_block_limitation(self):
        response = self.client.get("/methodology")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"417,278", response.data)
        self.assertIn(b"airport observations", response.data)
        self.assertIn(b"AOBT", response.data)
        self.assertIn(b"diverted", response.data.lower())
        self.assertIn(b"https://failbondi.fail/api/dump", response.data)

    def test_spanish_methodology_uses_localized_dates_and_content(self):
        response = self.client.get("/methodology?lang=es")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Cómo funciona".encode(), response.data)
        self.assertIn(b"417.278", response.data)
        self.assertIn("23 de diciembre de 2024".encode(), response.data)
        self.assertIn("¿Qué se está midiendo?".encode(), response.data)
        self.assertIn(b"AOBT", response.data)

    def test_comparison(self):
        response = self.client.get(
            "/compare?kind=route&item1=AEP-COR&item2=AEP-MDZ&period=90"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Comparison result", response.data)
        self.assertIn(b"Typical difference", response.data)
        self.assertIn(b"Flights analysed", response.data)
        self.assertNotIn(b"Observed event", response.data)
        self.assertNotIn(b"different observed events", response.data)

    def test_spanish_comparison_and_validation_message(self):
        response = self.client.get(
            "/compare?kind=route&item1=AEP-COR&item2=AEP-MDZ&period=90&lang=es"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Resultado de la comparación".encode(), response.data)
        self.assertIn("Diferencia típica".encode(), response.data)
        self.assertIn("Vuelos analizados".encode(), response.data)
        self.assertIn(b'name="lang" value="es"', response.data)

        invalid = self.client.get("/compare?item1=AR1458&lang=es")
        self.assertEqual(invalid.status_code, 200)
        self.assertIn(
            "Ingresá al menos dos elementos para comparar.".encode(),
            invalid.data,
        )

    def test_spanish_errors_keep_language(self):
        response = self.client.get(
            "/route?origin=AEP&destination=AEP&lang=es"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "El origen y el destino deben ser diferentes.".encode(),
            response.data,
        )
        self.assertIn(b'href="/?lang=es"', response.data)

        not_found = self.client.get("/missing?lang=es")
        self.assertEqual(not_found.status_code, 404)
        self.assertIn("La página solicitada no existe.".encode(), not_found.data)

    def test_mixed_comparison_explains_departure_and_arrival_events(self):
        response = self.client.get(
            "/compare?kind=flight&item1=AR1458&item2=BA249&period=365"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"different observed events", response.data)
        self.assertIn(b"Departures", response.data)
        self.assertIn(b"international arrivals", response.data)
        self.assertIn(b"Both use a 30-minute threshold", response.data)

if __name__ == "__main__":
    unittest.main()
