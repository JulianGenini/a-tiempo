"""Unit tests for the project's schedule-performance calculations.

Developed with assistance from OpenAI Codex.
"""

import unittest

from analytics import (
    aircraft_summary,
    build_report,
    calculate_metrics,
    display_flight_number,
    median,
    normalize_flight_number,
)


class AnalyticsTests(unittest.TestCase):
    def test_normalizes_flight_number(self):
        self.assertEqual(normalize_flight_number(" ar  1400 "), "AR1400")
        self.assertEqual(display_flight_number("AR1400"), "AR 1400")

    def test_median_for_odd_and_even_lists(self):
        self.assertEqual(median([3, 1, 2]), 2)
        self.assertEqual(median([4, 1, 2, 3]), 2.5)
        self.assertIsNone(median([]))

    def test_calculates_status_and_delay_rules(self):
        rows = [
            {"status_en": "Landed", "delay_seconds": 0},
            {"status_en": "Landed", "delay_seconds": 900},
            {"status_en": "Landed", "delay_seconds": 901},
            {"status_en": "Cancelled", "delay_seconds": None},
            {"status_en": "NO OPERA", "delay_seconds": None},
            {"status_en": "Landed", "delay_seconds": 7 * 60 * 60},
            {"status_en": "Landed", "delay_seconds": None},
        ]

        metrics = calculate_metrics(rows)

        self.assertEqual(metrics["observations"], 7)
        self.assertEqual(metrics["scheduled"], 6)
        self.assertEqual(metrics["cancelled"], 1)
        self.assertEqual(metrics["not_operating"], 1)
        self.assertEqual(metrics["excluded_outliers"], 1)
        self.assertEqual(metrics["usable"], 3)
        self.assertEqual(metrics["on_time"], 2)
        self.assertEqual(metrics["on_time_rate"], 66.7)
        self.assertEqual(metrics["cancellation_rate"], 16.7)
        self.assertEqual(metrics["median_delay"], 15.0)

    def test_separates_departures_and_arrivals(self):
        rows = [
            {
                "flight_date": "2026-01-01",
                "movement": "D",
                "status_en": "Took off",
                "delay_seconds": 0,
                "airport_iata": "AEP",
                "counterpart_iata": "COR",
            },
            {
                "flight_date": "2026-01-01",
                "movement": "A",
                "status_en": "Landed",
                "delay_seconds": 1800,
                "airport_iata": "COR",
                "counterpart_iata": "AEP",
            },
        ]

        report = build_report(rows)

        self.assertEqual(report["departure"]["on_time_rate"], 100.0)
        self.assertEqual(report["arrival"]["on_time_rate"], 0.0)
        self.assertEqual(report["routes"], ["AEP → COR"])

    def test_summarizes_common_historical_aircraft(self):
        summary = aircraft_summary(
            [
                {"aircraft_model": "Airbus A320"},
                {"aircraft_model": "Airbus A320"},
                {"aircraft_model": "Embraer 190/195"},
                {"aircraft_model": None},
            ]
        )

        self.assertEqual(summary["identified"], 3)
        self.assertEqual(summary["missing"], 1)
        self.assertEqual(summary["models"][0]["model"], "Airbus A320")
        self.assertEqual(summary["models"][0]["records"], 2)
        self.assertEqual(summary["models"][0]["share"], 66.7)


if __name__ == "__main__":
    unittest.main()
