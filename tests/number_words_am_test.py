import unittest
from decimal import Decimal

from abugida import NumberWordConverter
from abugida.number_words import amharic


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
            (Decimal("1E+2"), "አንድ መቶ"),
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
        self.assertEqual(split("3.050"), (False, 3, "05"))
        self.assertEqual(split(7), (False, 7, ""))
        self.assertEqual(split("2.0"), (False, 2, ""))


if __name__ == "__main__":
    unittest.main()
