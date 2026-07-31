"""Unit tests for the project's schedule-performance calculations.

Developed with assistance from OpenAI Codex.
"""

import unittest

from analytics import (
    aircraft_summary,
    build_report,
    calculate_metrics,
    display_flight_number,
    dominant_movement,
    first_observation_each_day,
    median,
    normalize_flight_number,
    recurring_observation_routes,
    route_pairs,
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
            {"status_en": "Took off", "delay_seconds": 0},
            {"status_en": "Took off", "delay_seconds": 1800},
            {"status_en": "Took off", "delay_seconds": 1801},
            {"status_en": "Cancelled", "delay_seconds": None},
            {"status_en": "NO OPERA", "delay_seconds": None},
            {"status_en": "Took off", "delay_seconds": 7 * 60 * 60},
            {"status_en": "Took off", "delay_seconds": None},
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
        self.assertEqual(metrics["median_delay"], 30.0)

    def test_keeps_first_ordered_departure_for_each_date(self):
        rows = [
            {"flight_date": "2026-01-01", "name": "first"},
            {"flight_date": "2026-01-01", "name": "later rotation event"},
            {"flight_date": "2026-01-02", "name": "next day"},
        ]

        selected = first_observation_each_day(rows)

        self.assertEqual(len(selected), 2)
        self.assertEqual(selected[0]["name"], "first")
        self.assertEqual(selected[1]["name"], "next day")

    def test_builds_departure_only_report(self):
        rows = [
            {
                "flight_date": "2026-01-01",
                "movement": "D",
                "status_en": "Took off",
                "delay_seconds": 0,
                "airport_iata": "AEP",
                "counterpart_iata": "COR",
            },
        ]

        report = build_report(rows)

        self.assertEqual(report["performance"]["on_time_rate"], 100.0)
        self.assertEqual(report["threshold_minutes"], 30)
        self.assertEqual(report["routes"], ["AEP → COR"])

    def test_builds_arrival_report_with_fifteen_minute_threshold(self):
        rows = [
            {
                "flight_date": "2026-01-01",
                "movement": "A",
                "status_en": "Landed",
                "delay_seconds": 16 * 60,
                "airport_iata": "AEP",
                "counterpart_iata": "SCL",
            }
        ]

        report = build_report(rows)

        self.assertEqual(report["movement_name"], "Arrivals")
        self.assertEqual(report["threshold_minutes"], 15)
        self.assertEqual(report["performance"]["on_time_rate"], 0.0)
        self.assertEqual(report["routes"], ["SCL → AEP"])

    def test_removes_one_date_route_anomalies_when_routes_recur(self):
        rows = [
            {"movement": "D", "airport_iata": "AEP", "counterpart_iata": "IRJ"},
            {"movement": "D", "airport_iata": "AEP", "counterpart_iata": "IRJ"},
            {"movement": "D", "airport_iata": "CTC", "counterpart_iata": "AEP"},
        ]

        selected = recurring_observation_routes(rows)

        self.assertEqual(len(selected), 2)
        self.assertTrue(all(row["airport_iata"] == "AEP" for row in selected))

    def test_keeps_a_single_available_route_observation(self):
        rows = [
            {"movement": "D", "airport_iata": "AEP", "counterpart_iata": "IRJ"}
        ]

        self.assertEqual(recurring_observation_routes(rows), rows)

    def test_selects_the_dominant_observed_movement(self):
        rows = [
            {"movement": "A"},
            {"movement": "A"},
            {"movement": "D"},
        ]

        selected = dominant_movement(rows)

        self.assertEqual(len(selected), 2)
        self.assertTrue(all(row["movement"] == "A" for row in selected))

    def test_excludes_placeholder_airport_codes_from_routes(self):
        rows = [
            {
                "movement": "D",
                "airport_iata": "EZE",
                "counterpart_iata": "--I",
            }
        ]

        self.assertEqual(route_pairs(rows), [])

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
