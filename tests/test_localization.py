"""Unit tests for the bilingual interface helpers.

Developed with assistance from OpenAI Codex.
"""

import unittest

from localization import (
    format_date,
    format_number,
    format_numeric_text,
    normalize_language,
    translate,
)


class LocalizationTests(unittest.TestCase):
    def test_normalizes_supported_languages(self):
        self.assertEqual(normalize_language("es"), "es")
        self.assertEqual(normalize_language("en"), "en")
        self.assertEqual(normalize_language("fr"), "en")
        self.assertEqual(normalize_language(None), "en")

    def test_translates_and_interpolates_text(self):
        self.assertEqual(translate("home_nav", "en"), "Home")
        self.assertEqual(translate("home_nav", "es"), "Inicio")
        self.assertEqual(
            translate("often_late", "es", minutes=30),
            "Frecuentemente más de 30 minutos tarde",
        )

    def test_formats_dates_and_numbers_for_each_language(self):
        self.assertEqual(format_date("2026-07-29", "en"), "29 Jul 2026")
        self.assertEqual(
            format_date("2026-07-29", "es"), "29 de julio de 2026"
        )
        self.assertEqual(format_number(417278, "en"), "417,278")
        self.assertEqual(format_number(417278, "es"), "417.278")
        self.assertEqual(format_numeric_text("80.4%", "es"), "80,4%")


if __name__ == "__main__":
    unittest.main()
