import unittest

from abugida import NumberWordConverter
from abugida.number_words import oromo, tables


class TestOromoToWords(unittest.TestCase):
    CASES = [
        (0, "zeeroo"), (6, "ja'a"), (11, "kudha tokko"), (19, "kudha sagal"), (20, "digdama"),
        (21, "digdamii tokko"), (99, "sagaltamii sagal"), (100, "dhibba tokko"), (200, "dhibba lama"),
        (101, "dhibba tokko fi tokko"), (125, "dhibba tokko fi digdamii shan"), (1000, "kuma tokko"),
        (1500, "kuma tokko fi dhibba shan"), (2015, "kuma lama fi kudha shan"),
        (2026, "kuma lama fi digdamii ja'a"), (5000, "kuma shan"),
        (5327, "kuma shan dhibba sadii fi digdamii torba"), (10**6, "miiliyoona tokko"),
        (125_000, "kuma dhibba tokko fi digdamii shan"),
        (1125, "kuma tokko dhibba tokko fi digdamii shan"),
    ]

    def setUp(self):
        self.converter = NumberWordConverter()

    def test_cardinals(self):
        for number, words in self.CASES:
            with self.subTest(number=number):
                self.assertEqual(self.converter.to_words(number, "om"), words)

    def test_year_is_cardinal(self):
        self.assertEqual(self.converter.to_words(2015, "om", to="year"), "kuma lama fi kudha shan")

    def test_ordinals(self):
        cases = {
            1: "tokkoffaa", 2: "lamaffaa", 3: "sadaffaa", 4: "arfaffaa", 5: "shanaffaa",
            10: "kurnaffaa", 100: "dhibbaffaa", 21: "digdamii tokkoffaa", 15: "kudha shanaffaa",
        }
        for number, words in cases.items():
            with self.subTest(number=number):
                self.assertEqual(self.converter.to_words(number, "om", to="ordinal"), words)

    def test_ordinal_errors(self):
        with self.assertRaises(TypeError):
            self.converter.to_words(0, "om", to="ordinal")

    def test_ordinal_num(self):
        self.assertEqual(self.converter.to_words(3, "om", to="ordinal_num"), "3ffaa")

    def test_negative_decimal(self):
        self.assertEqual(self.converter.to_words(-2.5, "om"), "negaatiivii lama tuqaa shan")

    def test_currency(self):
        self.assertEqual(self.converter.to_words(12.5, "om", to="currency", currency="ETB"),
                         "kudha lama qarshii shantama saantima")
        self.assertEqual(self.converter.to_words(1, "om", to="currency", currency="USD"), "tokko doolaara")
        self.assertEqual(self.converter.to_words(0.5, "om", to="currency", currency="USD"), "shantama seentii")
        self.assertEqual(self.converter.to_words(2, "om", to="currency", currency="EUR"), "lama yuuroo")

    def test_currency_errors(self):
        with self.assertRaises(ValueError):
            self.converter.to_words(1, "om", to="currency", currency="ERN")
        with self.assertRaises(ValueError):
            self.converter.to_words(2.5, "om", to="currency", currency="EUR")

    def test_bounds(self):
        self.assertTrue(self.converter.to_words(10**12 - 1, "om").startswith("biiliyoona dhibba sagal fi sagaltamii sagal miiliyoona"))
        with self.assertRaises(OverflowError):
            self.converter.to_words(10**12, "om")
        self.assertEqual(oromo.MAXVAL, 10**12)

    def test_accept_tables_do_not_shadow_default_words(self):
        defaults = set(tables.OM["digits"]) | set(tables.OM["tens"].values()) | set(tables.OM["scales"].values())
        self.assertFalse(defaults & set(tables.OM["accept"]))


if __name__ == "__main__":
    unittest.main()
