import random
import unittest
from decimal import Decimal
from unittest import mock

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


class TestOromoToNumber(unittest.TestCase):
    def setUp(self):
        self.converter = NumberWordConverter()

    def parse(self, text, to="cardinal"):
        return self.converter.to_number(text, "om", to)

    def test_round_trip(self):
        rng = random.Random(0)
        numbers = list(range(0, 20001)) + [rng.randrange(10**12) for _ in range(300)]
        for n in numbers:
            words = self.converter.to_words(n, "om")
            self.assertEqual(self.parse(words), n, words)
        for n in range(1, 2001):
            for mode in ("ordinal", "ordinal_num"):
                words = self.converter.to_words(n, "om", mode)
                self.assertEqual(self.parse(words, mode), n, words)
        for n in range(1, 3001):
            self.assertEqual(self.parse(self.converter.to_words(n, "om", "year"), "year"), n)
        for code in ("ETB", "USD"):
            for whole in range(0, 301):
                for cents in (0, 1, 50, 99):
                    if whole == 0 and cents == 0:
                        continue
                    amount = Decimal(f"{whole}.{cents:02d}")
                    words = self.converter.to_words(amount, "om", "currency", currency=code)
                    self.assertEqual(self.parse(words, "currency"), (amount, code), words)

    def test_accepts(self):
        cases = [
            ("kuma fi dhibba shan", 1500), ("kuma tokkoo fi dhibba shan", 1500),
            ("kuma tokko, dhibba shan", 1500), ("digdama tokko", 21), ("digdama fi tokko", 21),
            ("digdamii tokko", 21), ("kudhatokko", 11), ("kudha-tokko", 11), ("kudhan fi tokko", 11),
            ("jaha", 6), ("jaa", 6), ("duwwaa", 0), ("miliyoona", 10**6), ("hir'uu shan", -5),
            ("minus shan", -5), ("lama tuqaa shan", Decimal("2.5")), ("lama qabxii shan", Decimal("2.5")),
            ("Kuma Lamaa fi Kudha Shan", 2015), ("dhibba fi shan", 105), ("kudha shan", 15),
        ]
        for text, value in cases:
            with self.subTest(text=text):
                self.assertEqual(self.parse(text), value)

    def test_dropped_tokko_reads_greedily(self):
        # A multiplier is read greedily, so a dropped "tokko" is taken as part of the multiplier.
        # This is also the default form of 500 000, so the default reading wins.
        self.assertEqual(self.parse("kuma dhibba lama soddomii afur"), 234_000)
        self.assertEqual(self.parse("kuma dhibba shan"), 500_000)
        self.assertEqual(self.converter.to_words(500_000, "om"), "kuma dhibba shan")

    def test_tens_and_digit_after_fi_are_not_a_multiplier(self):
        # A multiplier never splits its tens and units with "fi": 21 000 is "kuma digdamii tokko",
        # so "kuma digdama fi tokko" is 20 001 and "kuma kudhan fi tokko" is 10 001
        for n in (*range(10_001, 10_010), 20_001, 30_005, 10_000_001, 820_006, 220_001):
            with self.subTest(n=n):
                self.assertEqual(self.parse(self.converter.to_words(n, "om")), n)
        self.assertEqual(self.parse("kuma digdama fi tokko"), 20_001)
        self.assertEqual(self.parse("kuma digdamii tokko"), 21_000)
        self.assertEqual(self.parse("kuma digdama tokko"), 21_000)
        self.assertEqual(self.parse("kuma dhibba tokko fi digdamii shan"), 125_000)
        self.assertEqual(self.parse("digdama fi tokko"), 21)

    def test_colliding_default_forms_read_greedily(self):
        # A scale group of exact hundreds followed by a part below 100 is written the same as a
        # larger multiplier: 900 046 and 946 000 are both "kuma dhibba sagal fi afurtamii ja'a"
        self.assertEqual(self.converter.to_words(900_046, "om"), self.converter.to_words(946_000, "om"))
        self.assertEqual(self.parse("kuma dhibba sagal fi afurtamii ja'a"), 946_000)
        self.assertEqual(self.converter.to_words(100_025, "om"), self.converter.to_words(125_000, "om"))
        self.assertEqual(self.parse(self.converter.to_words(100_025, "om")), 125_000)

    def test_reversed_order_fallback(self):
        self.assertEqual(self.parse("lama kuma"), 2000)
        self.assertEqual(self.parse("shan dhibba"), 500)
        self.assertEqual(self.parse("kuma lama dhibba shan"), 2500)

    def test_year_two_part(self):
        self.assertEqual(self.parse("digdamii kudha shan", "year"), 2015)
        self.assertEqual(self.parse("bara kuma lama fi kudha shan", "year"), 2015)
        self.assertEqual(self.parse("kudha sagal digdamii shan", "year"), 1925)
        with self.assertRaises(ValueError):
            self.parse("digdamii kudha shan")
        with self.assertRaises(ValueError):
            self.parse("bara kuma lama")

    def test_ordinal_accepts(self):
        for text, value in [
            ("lammaffaa", 2), ("afraffaa", 4), ("kudhaffaa", 10), ("dhibbaffaa", 100), ("kumaffaa", 1000),
            ("miiliyoonaffaa", 10**6), ("biiliyoonaffaa", 10**9), ("saddeetaffaa", 8), ("sagalaffaa", 9),
            ("kuma lama fi kudha shanaffaa", 2015), ("digdamii tokkoffaa", 21), ("jahaffaa", 6),
        ]:
            with self.subTest(text=text):
                self.assertEqual(self.parse(text, "ordinal"), value)
        self.assertEqual(self.parse("3ffaa", "ordinal_num"), 3)
        for text in ("lama", "0ffaa"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.parse(text, "ordinal" if text == "lama" else "ordinal_num")

    def test_currency_accepts(self):
        self.assertEqual(self.parse("qarshii shantama", "currency"), (Decimal("50.00"), "ETB"))
        self.assertEqual(self.parse("kudha lama birrii shantama saantima", "currency"), (Decimal("12.50"), "ETB"))
        self.assertEqual(self.parse("lama yuuroo", "currency"), (Decimal("2.00"), "EUR"))
        self.assertEqual(self.parse("shantama saantima", "currency"), (Decimal("0.50"), "ETB"))

    def test_rejects_non_numbers(self):
        for text in ("shan ja'a", "digdama soddoma", "manna", "fi lama", "lama fi", "kuma fi fi lama",
                     "kuma kuma", "kudha kudha", "dhibba dhibba", "zeeroo kuma", "kuma zeeroo"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.parse(text)

    def test_missing_amount_has_a_clear_error(self):
        for text, to in (("tuqaa shan", "cardinal"), ("seentii", "currency")):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, "No number words"):
                self.parse(text, to)

    def test_overflow(self):
        with self.assertRaises(OverflowError):
            self.parse("kuma biiliyoona")
        self.assertEqual(self.parse(self.converter.to_words(10**12 - 1, "om")), 10**12 - 1)

    def test_lexicon_is_consistent(self):
        self.assertEqual(oromo._build_lexicon(), oromo._LEXICON)
        with mock.patch.dict(tables.OM["accept"], {"lama": "tokko"}):
            with self.assertRaises(ValueError):
                oromo._build_lexicon()


if __name__ == "__main__":
    unittest.main()
