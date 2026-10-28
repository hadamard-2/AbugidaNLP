import unittest

from abugida import NumberWordConverter
from abugida.number_words import components


class TestNumberWordConverterApi(unittest.TestCase):
    def setUp(self):
        self.converter = NumberWordConverter()

    def test_unknown_language(self):
        with self.assertRaises(ValueError):
            self.converter.to_words(1, "xx")

    def test_unknown_mode(self):
        with self.assertRaises(ValueError):
            self.converter.to_words(1, "am", to="roman")

    def test_unimplemented_language(self):
        with self.assertRaises(NotImplementedError):
            self.converter.to_words(1, "om")

    def test_unknown_mode_precedes_unimplemented_language(self):
        with self.assertRaises(ValueError):
            self.converter.to_words(1, "om", to="roman")

    def test_components(self):
        self.assertEqual(components(2026), [(2, 1000), (20, 1), (6, 1)])
        self.assertEqual(components(615), [(6, 100), (15, 1)])
        self.assertEqual(components(0), [(0, 1)])
        self.assertEqual(components(10500), [(10, 1000), (5, 100)])


if __name__ == "__main__":
    unittest.main()
