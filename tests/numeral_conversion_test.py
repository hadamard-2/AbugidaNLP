import unittest
from abugida import NumeralConverter


class TestConvertNumeral(unittest.TestCase):
    def setUp(self):
        self.convert = NumeralConverter().convert

        self.test_cases = [
            (7654321, "፯፻፷፭፼፵፫፻፳፩"),
            (7650021, "፯፻፷፭፼፳፩"),
            (7650121, "፯፻፷፭፼፻፳፩"),
            (20242, "፪፼፪፻፵፪"),
        ]

    def test_gz_to_ha(self):
        for ha_num, gz_num in self.test_cases:
            with self.subTest(gz_num=gz_num):
                result = self.convert(gz_num, "gz", "ha")
                self.assertEqual(result, ha_num)

    def test_ha_to_gz(self):
        for ha_num, gz_num in self.test_cases:
            with self.subTest(ha_num=ha_num):
                result = self.convert(ha_num, "ha", "gz")
                self.assertEqual(result, gz_num)


if __name__ == "__main__":
    unittest.main()
