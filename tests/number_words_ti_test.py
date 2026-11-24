import random
import unittest
from decimal import Decimal
from unittest import mock

from abugida import NumberWordConverter
from abugida.number_words import tables, tigrinya


class TestTigrinyaCardinal(unittest.TestCase):
    CASES = [
        (0, "ባዶ"), (5, "ሓሙሽተ"), (6, "ሽዱሽተ"), (12, "ዓሰርተ ክልተ"), (20, "ዕስራ"),
        (21, "ዕስራን ሓደን"), (35, "ሰላሳን ሓሙሽተን"), (99, "ተስዓን ትሽዓተን"),
        (100, "ሓደ ሚእቲ"), (101, "ሓደ ሚእትን ሓደን"), (125, "ሓደ ሚእትን ዕስራን ሓሙሽተን"), (200, "ክልተ ሚእቲ"),
        (615, "ሽዱሽተ ሚእትን ዓሰርተ ሓሙሽተን"), (812, "ሸሞንተ ሚእትን ዓሰርተ ክልተን"),
        (1000, "ሓደ ሽሕ"), (1500, "ሓደ ሽሕን ሓሙሽተ ሚእትን"), (2015, "ክልተ ሽሕን ዓሰርተ ሓሙሽተን"),
        (2025, "ክልተ ሽሕን ዕስራን ሓሙሽተን"), (2026, "ክልተ ሽሕን ዕስራን ሽዱሽተን"), (5000, "ሓሙሽተ ሽሕ"),
        (21_000, "ዕስራን ሓደን ሽሕ"), (21_005, "ዕስራን ሓደን ሽሕን ሓሙሽተን"), (100_000, "ሓደ ሚእቲ ሽሕ"),
        (10**6, "ሓደ ሚልዮን"), (1_500_000, "ሓደ ሚልዮንን ሓሙሽተ ሚእቲ ሽሕን"), (10**9, "ሓደ ቢልዮን"),
    ]

    def setUp(self):
        self.converter = NumberWordConverter()

    def test_cardinals(self):
        for number, words in self.CASES:
            with self.subTest(number=number):
                self.assertEqual(self.converter.to_words(number, "ti"), words)

    def test_bounds(self):
        self.assertTrue(self.converter.to_words(10**12 - 1, "ti"))
        with self.assertRaises(OverflowError):
            self.converter.to_words(10**12, "ti")

    def test_gender_on_cardinal_ignored(self):
        self.assertEqual(self.converter.to_words(1, "ti", gender="f"), "ሓደ")

    def test_accept_table(self):
        accept = tables.TI["accept"]
        for variant in ("ዜሮ", "ሓንቲ", "ሽድሽተ", "ሸድሽተ", "ሾብዓተ", "ሾሞንተ", "ተሽዓተ", "ትሻዓተ", "እስራ",
                        "ሱሳ", "ቴስዓ", "ሺሕ", "ሺ", "ሳድሳይ", "ሳድሰይቲ", "ሚሊዮን", "ቢሊዮን", "ኣሉታዊ", "ኔጌቲቭ", "ነገቲቭ", "ማይነስ", "ሰንት",
                        "አርባዕተ", "አርብዓ"):
            self.assertIn(variant, accept)


class TestTigrinyaFormats(unittest.TestCase):
    def setUp(self):
        self.converter = NumberWordConverter()

    def test_ordinals(self):
        for number, words, gender in [
            (1, "ቀዳማይ", "m"), (3, "ሳልሳይ", "m"), (10, "ዓስራይ", "m"), (3, "ሳልሰይቲ", "f"),
            (6, "ሻድሻይ", "m"), (6, "ሻድሸይቲ", "f"), (7, "ሻብዓይ", "m"), (7, "ሻብዐይቲ", "f"),
            (8, "ሻምናይ", "m"), (8, "ሻምነይቲ", "f"), (9, "ታሽዓይ", "m"), (9, "ታሽዐይቲ", "f"),
            (11, "መበል ዓሰርተ ሓደ", "m"), (21, "መበል ዕስራን ሓደን", "m"), (100, "መበል ሓደ ሚእቲ", "m"),
        ]:
            with self.subTest(number=number, gender=gender):
                self.assertEqual(self.converter.to_words(number, "ti", "ordinal", gender=gender), words)

    def test_ordinal_num(self):
        for number, words, gender in [
            (1, "1ይ", "m"), (10, "10ይ", "m"), (3, "3ይቲ", "f"), (11, "መበል 11", "m"), (100, "መበል 100", "m"),
            (10**20, f"መበል {10**20}", "m"),
        ]:
            with self.subTest(number=number, gender=gender):
                self.assertEqual(self.converter.to_words(number, "ti", "ordinal_num", gender=gender), words)

    def test_without_explicit_one(self):
        for number, mode, words in [
            (100, "cardinal", "ሚእቲ"), (101, "cardinal", "ሚእትን ሓደን"), (199, "cardinal", "ሚእትን ተስዓን ትሽዓተን"),
            (200, "cardinal", "ክልተ ሚእቲ"), (1000, "cardinal", "ሓደ ሽሕ"),
            (1100, "cardinal", "ሓደ ሽሕን ሓደ ሚእትን"), (100_000, "cardinal", "ሓደ ሚእቲ ሽሕ"),
            (100, "ordinal", "መበል ሚእቲ"), (1000, "ordinal", "መበል ሓደ ሽሕ"),
        ]:
            with self.subTest(number=number, mode=mode):
                self.assertEqual(self.converter.to_words(number, "ti", mode, explicit_one=False), words)
        for n in range(100, 200):
            words = self.converter.to_words(n, "ti", explicit_one=False)
            self.assertEqual(self.converter.to_number(words, "ti"), n, words)

    def test_negative_decimal(self):
        self.assertEqual(self.converter.to_words(-2.5, "ti"), "ኣሉታ ክልተ ነጥቢ ሓሙሽተ")
        self.assertEqual(self.converter.to_words(0.05, "ti"), "ባዶ ነጥቢ ባዶ ሓሙሽተ")

    def test_currency(self):
        for value, code, words in [
            (12.5, "ETB", "ዓሰርተ ክልተ ብር ሓምሳ ሳንቲም"),
            (21.25, "ETB", "ዕስራን ሓደን ብር ዕስራን ሓሙሽተን ሳንቲም"),
            (3, "ERN", "ሰለስተ ናቕፋ"), (1.5, "USD", "ሓደ ዶላር ሓምሳ ሳንቲም"), (2, "EUR", "ክልተ ዩሮ"),
        ]:
            with self.subTest(value=value, code=code):
                self.assertEqual(self.converter.to_words(value, "ti", "currency", currency=code), words)
        with self.assertRaises(ValueError):
            self.converter.to_words(1, "ti", "currency", currency="GBP")


class TestTigrinyaToNumber(unittest.TestCase):
    def setUp(self):
        self.converter = NumberWordConverter()

    def parse(self, text, to="cardinal"):
        return self.converter.to_number(text, "ti", to)

    def test_round_trip(self):
        rng = random.Random(0)
        numbers = list(range(0, 10001)) + [rng.randrange(10**12) for _ in range(300)]
        for n in numbers:
            words = self.converter.to_words(n, "ti")
            self.assertEqual(self.parse(words), n, words)
        for n in range(1, 2001):
            for gender in ("m", "f"):
                for mode in ("ordinal", "ordinal_num"):
                    words = self.converter.to_words(n, "ti", mode, gender=gender)
                    self.assertEqual(self.parse(words, mode), n, words)
        for n in range(1, 3001):
            self.assertEqual(self.parse(self.converter.to_words(n, "ti", "year"), "year"), n)
        for whole in range(0, 301):
            for cents in (0, 1, 50, 99):
                if whole == 0 and cents == 0:
                    continue
                amount = Decimal(f"{whole}.{cents:02d}")
                words = self.converter.to_words(amount, "ti", "currency", currency="ETB")
                self.assertEqual(self.parse(words, "currency"), (amount, "ETB"), words)

    def test_accepts_conjunction_patterns(self):
        for text in ("ሺሕን ሓሙሽተ ሚእትን", "ሓደ ሺሕን ሓሙሽተ ሚእትን", "ሽሕን ሓሙሽተ ሚእቲ", "ሽሕ ሓሙሽተ ሚእቲ",
                     "ሽሕ ን ሓሙሽተ ሚእቲ", "ዓሰርተ ሓሙሽተ ሚእቲ", "ሺ ሓሙሽተ ሚእቲ"):
            with self.subTest(text=text):
                self.assertEqual(self.parse(text), 1500)
        for text in ("ዕስራን ሓሙሽተን", "ዕስራን ሓሙሽተ", "ዕስራ ሓሙሽተን", "ዕስራ ሓሙሽተ", "ዕስራ ን ሓሙሽተ"):
            with self.subTest(text=text):
                self.assertEqual(self.parse(text), 25)

    def test_accepts_words(self):
        for text, value in [
            ("ዜሮ", 0), ("ሓንቲ", 1), ("ሽድሽተ", 6), ("ሾብዓተ", 7), ("ሱሳ", 60), ("ቴስዓ", 90), ("እስራ", 20),
            ("አርባዕተ", 4), ("ሓደ ሚልዮን", 10**6), ("ሚሊዮን", 10**6), ("ነገቲቭ ሓሙሽተ", -5),
            ("ማይነስ ሓሙሽተ", -5),
            ("ኣሉታዊ ሓሙሽተ", -5), ("አርብዓ", 40), ("ሚልዮንን ሓደ", 10**6 + 1), ("ሺሕ", 1000),
            ("ክልተ ሺሕን ዓሰርተ ሓሙሽተን", 2015),
        ]:
            with self.subTest(text=text):
                self.assertEqual(self.parse(text), value)

    def test_ordinal_accepts(self):
        self.assertEqual(self.parse("መበል ሓደ", "ordinal"), 1)
        self.assertEqual(self.parse("መበል ቀዳማይ", "ordinal"), 1)
        self.assertEqual(self.parse("ቀዳመይቲ", "ordinal"), 1)
        self.assertEqual(self.parse("መበል ዓሰርተ ሓደ", "ordinal"), 11)
        self.assertEqual(self.parse("ሳድሳይ", "ordinal"), 6)
        self.assertEqual(self.parse("ሳድሰይቲ", "ordinal"), 6)
        for text, value in [
            ("ሳብዓይ", 7), ("ሳብዐይቲ", 7), ("ሻውዓይ", 7), ("ሻውዐይቲ", 7), ("ሻብዓይቲ", 7),
            ("ሳምናይ", 8), ("ሳምነይቲ", 8), ("ሻሙናይ", 8),
            ("ታስዓይ", 9), ("ታስዐይቲ", 9), ("ታሽዓይቲ", 9), ("መበል ሻብዓይ", 7),
        ]:
            with self.subTest(text=text):
                self.assertEqual(self.parse(text, "ordinal"), value)
        self.assertEqual(self.parse("መበል ሚእቲ", "ordinal"), 100)
        for text, value in [("3-ይ", 3), ("3ይ", 3), ("3ይቲ", 3), ("3-ይቲ", 3), ("መበል 11", 11),
                            (f"መበል {10**20}", 10**20)]:
            with self.subTest(text=text):
                self.assertEqual(self.parse(text, "ordinal_num"), value)

    def test_ordinal_rejects(self):
        for text in ("ሓደ", "ሓሙሽተ ቀዳማይ", "መበል", "መበል ቀዳማይ ሓደ", "ቀዳማይ ቀዳማይ", "ኣሉታ ቀዳማይ", "መበል ባዶ"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.parse(text, "ordinal")
        for text in ("3", "0ይ", "ይ", "መበል", "መበል 0", "3ይ 4ይ", "ሳልሳይ"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.parse(text, "ordinal_num")
        with self.assertRaises(ValueError):
            self.parse("ቀዳማይ")

    def test_currency_accepts(self):
        for text in ("ዓሰርተ ክልተ ብርን ሓምሳ ሳንቲምን", "ዓሰርተ ክልተ ብር ምስ ሓምሳ ሰንት",
                     "ዓሰርተ ክልተ ብር ሓምሳ ሳንቲም ጥራይ", "ዓሰርተ ክልተ ብር ሓምሳ ሳንቲም ጥራሕ"):
            with self.subTest(text=text):
                self.assertEqual(self.parse(text, "currency"), (Decimal("12.50"), "ETB"))
        self.assertEqual(self.parse("ሰለስተ ናቕፋ", "currency"), (Decimal("3.00"), "ERN"))
        self.assertEqual(self.parse("ሓምሳ ሳንቲም", "currency"), (Decimal("0.50"), "ETB"))
        self.assertEqual(self.parse("ኣሉታ ሓደ ዶላር", "currency"), (Decimal("-1.00"), "USD"))

    def test_currency_words_only_skipped_in_currency_mode(self):
        for text in ("ሓደ ምስ ክልተ", "ሓደ ጥራይ"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.parse(text)

    def test_conjunction_stripping(self):
        self.assertEqual(self.parse("ክልተ ሚእትን"), 200)
        self.assertEqual(self.parse("ሚልዮን"), 10**6)
        self.assertEqual(self.parse("ክልተ ሚልዮን"), 2 * 10**6)
        for text in ("ን", "ን ን", "ሓደ ናቕፋ", "ብርን"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.parse(text)

    def test_decimals(self):
        self.assertEqual(self.parse("ኣሉታ ክልተ ነጥቢ ሓሙሽተ"), Decimal("-2.5"))
        self.assertEqual(self.parse("ባዶ ነጥቢ ባዶ ሓሙሽተ"), Decimal("0.05"))

    def test_rejects_non_numbers(self):
        for text in ("ሓሙሽተ ሽዱሽተ", "ዕስራ ሰላሳ", "ዓሰርተን ሓሙሽተን ሓሙሽተ", "ቤት", "ሚእቲን ሚእቲ", "ዕስራን ሓደን ሓደን",
                     "አሉታ ሓሙሽተ", "ሚነስ ሓሙሽተ"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.parse(text)

    def test_overflow(self):
        with self.assertRaises(OverflowError):
            self.parse("ሺሕ ቢልዮን")

    def test_lexicon_is_consistent(self):
        self.assertEqual(tigrinya._build_lexicon(), tigrinya._LEXICON)
        with mock.patch.dict(tables.TI["accept"], {"ዕስራ": "ሓደ"}):
            with self.assertRaises(ValueError):
                tigrinya._build_lexicon()

    def test_unsupported_mode(self):
        with self.assertRaises(ValueError):
            self.converter.to_number("ሓደ", "ti", "bogus")


if __name__ == "__main__":
    unittest.main()
