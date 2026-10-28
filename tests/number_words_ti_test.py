import unittest

from abugida import NumberWordConverter
from abugida.number_words import tables


class TestTigrinyaCardinal(unittest.TestCase):
    CASES = [
        (0, "ባዶ"), (5, "ሓሙሽተ"), (6, "ሽዱሽተ"), (12, "ዓሰርተ ክልተ"), (20, "ዕስራ"),
        (21, "ዕስራን ሓደን"), (35, "ሰላሳን ሓሙሽተን"), (99, "ተስዓን ትሽዓተን"),
        (100, "ሚእቲ"), (101, "ሚእትን ሓደን"), (125, "ሚእትን ዕስራን ሓሙሽተን"), (200, "ክልተ ሚእቲ"),
        (615, "ሽዱሽተ ሚእትን ዓሰርተ ሓሙሽተን"), (812, "ሸሞንተ ሚእትን ዓሰርተ ክልተን"),
        (1000, "ሺሕ"), (1500, "ሺሕን ሓሙሽተ ሚእትን"), (2015, "ክልተ ሺሕን ዓሰርተ ሓሙሽተን"),
        (2025, "ክልተ ሺሕን ዕስራን ሓሙሽተን"), (2026, "ክልተ ሺሕን ዕስራን ሽዱሽተን"), (5000, "ሓሙሽተ ሺሕ"),
        (21_000, "ዕስራን ሓደን ሺሕ"), (21_005, "ዕስራን ሓደን ሺሕን ሓሙሽተን"),
        (10**6, "ሚልዮን"), (1_500_000, "ሚልዮንን ሓሙሽተ ሚእቲ ሺሕን"), (10**9, "ቢልዮን"),
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
                        "ሱሳ", "ቴስዓ", "ሽሕ", "ሺ", "ሚሊዮን", "ቢሊዮን", "ኣሉታዊ", "ሚነስ", "ኔጌቲቭ", "ሰንት",
                        "አርባዕተ", "አርብዓ", "አሉታ"):
            self.assertIn(variant, accept)


class TestTigrinyaFormats(unittest.TestCase):
    def setUp(self):
        self.converter = NumberWordConverter()

    def test_ordinals(self):
        for number, words, gender in [
            (1, "ቀዳማይ", "m"), (3, "ሳልሳይ", "m"), (10, "ዓስራይ", "m"), (3, "ሳልሰይቲ", "f"),
            (11, "መበል ዓሰርተ ሓደ", "m"), (21, "መበል ዕስራን ሓደን", "m"), (100, "መበል ሚእቲ", "m"),
        ]:
            with self.subTest(number=number, gender=gender):
                self.assertEqual(self.converter.to_words(number, "ti", "ordinal", gender=gender), words)

    def test_ordinal_num(self):
        for number, words, gender in [
            (1, "1ይ", "m"), (10, "10ይ", "m"), (3, "3ይቲ", "f"), (11, "መበል 11", "m"), (100, "መበል 100", "m"),
        ]:
            with self.subTest(number=number, gender=gender):
                self.assertEqual(self.converter.to_words(number, "ti", "ordinal_num", gender=gender), words)

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


if __name__ == "__main__":
    unittest.main()
