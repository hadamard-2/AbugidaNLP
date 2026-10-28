import unittest

from abugida import NumberWordConverter


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


if __name__ == "__main__":
    unittest.main()
