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
        self.assertIn(b"Know your flight before you fly.", response.data)
        self.assertIn(b"aircraft that usually operates them", response.data)
        self.assertIn(b"flights arriving in or departing from Argentina", response.data)
        self.assertIn(b"Argentina-only historical dataset", response.data)
        self.assertIn(b"Choose how you want to search", response.data)
        self.assertIn(b"Built from airport history", response.data)
        self.assertIn(b"417K", response.data)
        self.assertIn(b"164", response.data)
        self.assertIn(b"62", response.data)
        self.assertNotIn(b'id="compare-panel"', response.data)
        self.assertIn(b">Compare</a>", response.data)
        self.assertIn(b"December 23, 2024 through July 29, 2026", response.data)

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
        response = self.client.get("/flight?number=AR+1458&period=90")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Flight history", response.data)
        self.assertIn(b"Commonly recorded aircraft", response.data)
        self.assertIn(b"Embraer 190/195", response.data)

    def test_route_report(self):
        response = self.client.get(
            "/route?origin=AEP&destination=COR&period=365"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AEP", response.data)
        self.assertIn(b"COR", response.data)

    def test_airline_report(self):
        response = self.client.get("/airline?code=AR&period=90")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Airline history", response.data)

    def test_rejects_invalid_route(self):
        response = self.client.get("/route?origin=AEP&destination=AEP")
        self.assertEqual(response.status_code, 400)

    def test_methodology_explains_off_block_limitation(self):
        response = self.client.get("/methodology")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"269,377", response.data)
        self.assertIn(b"departure records", response.data)
        self.assertIn(b"AOBT", response.data)

    def test_comparison(self):
        response = self.client.get(
            "/compare?kind=route&item1=AEP-COR&item2=AEP-MDZ&period=90"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Comparison result", response.data)

if __name__ == "__main__":
    unittest.main()
