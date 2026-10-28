import random
import unittest
from unittest import mock
from decimal import Decimal

from abugida import NumberWordConverter
from abugida.number_words import amharic, tables


class TestAmharicCardinal(unittest.TestCase):
    CASES = [
        (0, "ዜሮ"), (1, "አንድ"), (10, "አሥር"), (11, "አሥራ አንድ"), (16, "አሥራ ስድስት"),
        (20, "ሃያ"), (21, "ሃያ አንድ"), (50, "ሃምሳ"), (60, "ስድሳ"), (99, "ዘጠና ዘጠኝ"),
        (100, "አንድ መቶ"), (101, "አንድ መቶ አንድ"), (125, "አንድ መቶ ሃያ አምስት"),
        (1000, "አንድ ሺህ"), (1500, "አንድ ሺህ አምስት መቶ"), (2015, "ሁለት ሺህ አሥራ አምስት"),
        (2026, "ሁለት ሺህ ሃያ ስድስት"), (10500, "አሥር ሺህ አምስት መቶ"),
        (10**6, "አንድ ሚሊዮን"), (21_000, "ሃያ አንድ ሺህ"), (125_000, "አንድ መቶ ሃያ አምስት ሺህ"),
    ]

    def setUp(self):
        self.converter = NumberWordConverter()

    def test_cardinals(self):
        for number, words in self.CASES:
            with self.subTest(number=number):
                self.assertEqual(self.converter.to_words(number, "am"), words)

    def test_bounds(self):
        top = self.converter.to_words(10**15 - 1, "am")
        self.assertTrue(top.startswith("ዘጠኝ መቶ ዘጠና ዘጠኝ ትሪሊዮን"))
        with self.assertRaises(OverflowError):
            self.converter.to_words(10**15, "am")


class TestAmharicFormats(unittest.TestCase):
    ORDINALS = [
        (1, "አንደኛ"), (3, "ሦስተኛ"), (10, "አሥረኛ"), (11, "አሥራ አንደኛ"), (20, "ሃያኛ"),
        (21, "ሃያ አንደኛ"), (100, "መቶኛ"), (1000, "ሺህኛ"), (10**6, "ሚሊዮንኛ"),
        (101, "አንድ መቶ አንደኛ"), (200, "ሁለት መቶኛ"), (2015, "ሁለት ሺህ አሥራ አምስተኛ"),
    ]

    def setUp(self):
        self.converter = NumberWordConverter()

    def test_ordinals(self):
        for number, words in self.ORDINALS:
            with self.subTest(number=number):
                self.assertEqual(self.converter.to_words(number, "am", to="ordinal"), words)
                self.assertEqual(amharic.ordinal(number), words)
                self.assertEqual(amharic.ordinal(number, "f"), words)

    def test_ordinal_num(self):
        self.assertEqual(self.converter.to_words(3, "am", to="ordinal_num"), "3ኛ")
        self.assertEqual(amharic.ordinal_num(2015), "2015ኛ")

    def test_ordinal_rejects(self):
        for bad in (0, -1, 2.5):
            for mode in ("ordinal", "ordinal_num"):
                with self.subTest(bad=bad, mode=mode):
                    with self.assertRaises(TypeError):
                        self.converter.to_words(bad, "am", to=mode)
            with self.subTest(bad=bad, fn="module"):
                with self.assertRaises(TypeError):
                    amharic.ordinal(bad)
                with self.assertRaises(TypeError):
                    amharic.ordinal_num(bad)

    def test_year(self):
        self.assertEqual(self.converter.to_words(2015, "am", to="year"), "ሁለት ሺህ አሥራ አምስት")
        self.assertEqual(self.converter.to_words(-44, "am", to="year"), "ኔጌቲቭ አርባ አራት")

    def test_negative_and_decimal(self):
        cases = [
            (-2.5, "ኔጌቲቭ ሁለት ነጥብ አምስት"), (Decimal("3.05"), "ሦስት ነጥብ ዜሮ አምስት"),
            ("2.0", "ሁለት"), (-7, "ኔጌቲቭ ሰባት"), (2.0, "ሁለት"), ("-0.5", "ኔጌቲቭ ዜሮ ነጥብ አምስት"),
            (Decimal("1E+2"), "አንድ መቶ"), (Decimal("3.50"), "ሦስት ነጥብ አምስት ዜሮ"),
            ("2.10", "ሁለት ነጥብ አንድ ዜሮ"), (Decimal("3.500"), "ሦስት ነጥብ አምስት ዜሮ ዜሮ"),
            (2.10, "ሁለት ነጥብ አንድ"), (0.05, "ዜሮ ነጥብ ዜሮ አምስት"),
        ]
        for value, words in cases:
            with self.subTest(value=value):
                self.assertEqual(self.converter.to_words(value, "am"), words)

    def test_invalid_input(self):
        for bad in ("abc", "", float("nan"), float("inf")):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    self.converter.to_words(bad, "am")
        for bad in (None, [1], True, 1 + 2j):
            with self.subTest(bad=bad):
                with self.assertRaises(TypeError):
                    self.converter.to_words(bad, "am")

    def test_overflow_with_modes(self):
        with self.assertRaises(OverflowError):
            self.converter.to_words(-(10**15), "am")
        with self.assertRaises(OverflowError):
            self.converter.to_words("1e999999999999", "am")
        with self.assertRaises(OverflowError):
            self.converter.to_words(10**15, "am", to="ordinal")
        with self.assertRaises(OverflowError):
            self.converter.to_words(10**15, "am", to="currency", currency="ETB")

    def test_currency(self):
        cases = [
            (12.5, "ETB", "አሥራ ሁለት ብር ከ ሃምሳ ሳንቲም"), (1, "USD", "አንድ ዶላር"),
            (0.5, "ETB", "ሃምሳ ሳንቲም"), (2.005, "ETB", "ሁለት ብር ከ አንድ ሳንቲም"),
            (0, "ETB", "ዜሮ ብር"), (-1.5, "ETB", "ኔጌቲቭ አንድ ብር ከ ሃምሳ ሳንቲም"),
            ("3.999", "ETB", "አራት ብር"),
        ]
        for value, code, words in cases:
            with self.subTest(value=value, code=code):
                self.assertEqual(
                    self.converter.to_words(value, "am", to="currency", currency=code), words
                )

    def test_currency_rejects(self):
        for code in ("EUR", None):
            with self.subTest(code=code):
                with self.assertRaises(ValueError):
                    self.converter.to_words(1, "am", to="currency", currency=code)

    def test_module_contract(self):
        self.assertEqual(amharic.NEGATIVE, "ኔጌቲቭ")
        self.assertEqual(amharic.POINT, "ነጥብ")
        self.assertEqual(amharic.ZERO, "ዜሮ")
        self.assertEqual(amharic.currency(2, 50, "ETB"), "ሁለት ብር ከ ሃምሳ ሳንቲም")

    def test_split_decimal(self):
        split = NumberWordConverter._split_decimal
        self.assertEqual(split(-2.5), (True, 2, "5"))
        self.assertEqual(split("3.050"), (False, 3, "050"))
        self.assertEqual(split(Decimal("3.500")), (False, 3, "500"))
        self.assertEqual(split(2.10), (False, 2, "1"))
        self.assertEqual(split(7), (False, 7, ""))
        self.assertEqual(split("2.0"), (False, 2, ""))


class TestAmharicToNumber(unittest.TestCase):
    def setUp(self):
        self.converter = NumberWordConverter()

    def parse(self, text, to="cardinal"):
        return self.converter.to_number(text, "am", to)

    def test_round_trip_cardinal(self):
        numbers = list(range(0, 10001)) + [random.Random(0).randrange(10**15) for _ in range(300)]
        for n in numbers:
            words = self.converter.to_words(n, "am")
            self.assertEqual(self.parse(words), n, words)

    def test_round_trip_modes(self):
        for n in range(1, 2001):
            for mode in ("ordinal", "ordinal_num"):
                words = self.converter.to_words(n, "am", mode)
                self.assertEqual(self.parse(words, mode), n, words)
        for n in range(1, 3001):
            self.assertEqual(self.parse(self.converter.to_words(n, "am", "year"), "year"), n)
        for whole in range(0, 301):
            for cents in (0, 1, 50, 99):
                if whole == 0 and cents == 0:
                    continue
                amount = Decimal(f"{whole}.{cents:02d}")
                words = self.converter.to_words(amount, "am", "currency", currency="ETB")
                self.assertEqual(self.parse(words, "currency"), (amount, "ETB"), words)

    def test_accepts(self):
        cases = [
            ("ሺ አምስት መቶ", 1500), ("መቶ", 100), ("ሺህ", 1000), ("ሚሊዮን", 10**6),
            ("ሃያ አምስት", 25), ("አምሳ", 50), ("ስልሳ", 60), ("ባዶ", 0), ("አንዲት", 1),
            ("ሲቀነስ አምስት", -5), ("አሉታዊ አምስት", -5), ("  አንድ መቶ  ", 100),
        ]
        for text, value in cases:
            with self.subTest(text=text):
                self.assertEqual(self.parse(text), value)
        for text, value in [("መጀመሪያ", 1), ("ሺኛ", 1000), ("መቶ አንደኛ", 101)]:
            with self.subTest(text=text):
                self.assertEqual(self.parse(text, "ordinal"), value)

    def test_mixed_digits_and_words(self):
        self.assertEqual(self.parse("3 ሚሊዮን"), 3000000)
        self.assertEqual(self.parse("1.5 ሚሊዮን"), 1500000)
        self.assertEqual(self.parse("2 ሺህ 500"), 2500)
        for text in ("1.5", "1.5 መቶ", "1.0005 ሺህ", "ሃያ 1.5 ሺህ"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.parse(text)

    def test_homophone_spellings(self):
        for text, value in [("አስራ ስድስት", 16), ("ኃምሳ", 50), ("ሀምሳ", 50), ("ሠላሳ", 30), ("ሰላሳ", 30)]:
            with self.subTest(text=text):
                self.assertEqual(self.parse(text), value)

    def test_rejects_non_numbers(self):
        for text in ("አምስት ስድስት", "ሃያ ሠላሳ", "ሺህ ሺህ", "መቶ ሺህ መቶ ሺህ", "ቤት", "", "   ",
                     "ሺህ ሺ", "አንድ ሺህ አንድ ሚሊዮን", "ዜሮ አምስት", "አምስት ዜሮ", "ዜሮ ሺህ",
                     "መቶ መቶ", "ሲቀነስ", "ነጥብ አምስት", "አምስት ነጥብ", "አምስት ብር"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.parse(text)
        for text, mode in (("አምስት", "ordinal"), ("አምስተኛ", "cardinal"), ("አምስተኛ አምስተኛ", "ordinal"),
                           ("0ኛ", "ordinal_num"), ("3", "ordinal_num"), ("ብር", "currency"),
                           ("አምስት ሳንቲም ብር", "currency"), ("ሃያ ብር ከ", "currency"), ("አምስት ብር አምስት ብር", "currency")):
            with self.subTest(text=text, mode=mode), self.assertRaises(ValueError):
                self.parse(text, mode)
        with self.assertRaises(ValueError):
            self.converter.to_number("አምስት", "am", "bogus")
        with self.assertRaises(ValueError):
            self.converter.to_number("አምስት", "xx")

    def test_decimal_and_currency_parse(self):
        self.assertEqual(self.parse("ኔጌቲቭ ሁለት ነጥብ አምስት"), Decimal("-2.5"))
        self.assertEqual(self.parse("አንድ ነጥብ ዜሮ አምስት"), Decimal("1.05"))
        with self.assertRaises(ValueError):
            self.parse("አንድ ነጥብ አሥር")
        cases = [
            ("አሥራ ሁለት ብር ከ ሃምሳ ሳንቲም", (Decimal("12.50"), "ETB")),
            ("ሃምሳ ሳንቲም", (Decimal("0.50"), "ETB")),
            ("አንድ ዶላር", (Decimal("1.00"), "USD")),
            ("ኔጌቲቭ አንድ ዶላር ከ አምስት ሳንቲም", (Decimal("-1.05"), "USD")),
        ]
        for text, value in cases:
            with self.subTest(text=text):
                self.assertEqual(self.parse(text, "currency"), value)

    def test_overflow_parse(self):
        with self.assertRaises(OverflowError):
            self.parse("አንድ ሺህ ትሪሊዮን")
        with self.assertRaises(OverflowError):
            self.parse("አንድ ሚሊዮን ቢሊዮን")
        self.assertEqual(self.parse("ዘጠኝ መቶ ዘጠና ዘጠኝ ትሪሊዮን"), 999 * 10**12)

    def test_ordinal_num_parse(self):
        self.assertEqual(self.parse("3ኛ", "ordinal_num"), 3)

    def test_scale_product_only_for_single_scale_group(self):
        self.assertEqual(self.parse("ሺህ ሚሊዮን"), 10**9)
        self.assertEqual(self.parse("አንድ ሺህ ሚሊዮን"), 10**9)
        for text in ("አንድ ሚሊዮን ሺህ ሚሊዮን", "ሺህ ሚሊዮን ቢሊዮን"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.parse(text)

    def test_lenient_ten_then_unit(self):
        self.assertEqual(self.parse("አሥር አንድ"), 11)

    def test_lexicon_conflict_is_detected(self):
        self.assertEqual(amharic._build_lexicon(), amharic._LEXICON)
        with mock.patch.dict(tables.AM["accept"], {"ሃያ": "አንድ"}):
            with self.assertRaises(ValueError):
                amharic._build_lexicon()


if __name__ == "__main__":
    unittest.main()
