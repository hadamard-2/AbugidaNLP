import unittest
from abugida import NumeralConverter


class TestConvertNumeral(unittest.TestCase):
    def setUp(self):
        self.convert = NumeralConverter().convert

        # Canonical forms, cross-checked against ICU's CLDR "%ethiopic" rule set
        self.test_cases = [
            (1, "፩"),
            (99, "፺፱"),
            (100, "፻"),
            (101, "፻፩"),
            (200, "፪፻"),
            (1000, "፲፻"),
            (10000, "፼"),
            (10001, "፼፩"),
            (10100, "፼፻"),
            (20000, "፪፼"),
            (100000, "፲፼"),
            (1000000, "፻፼"),
            (1000021, "፻፼፳፩"),
            (7000021, "፯፻፼፳፩"),
            (7654321, "፯፻፷፭፼፵፫፻፳፩"),
            (7650021, "፯፻፷፭፼፳፩"),
            (7650121, "፯፻፷፭፼፻፳፩"),
            (20242, "፪፼፪፻፵፪"),
            (99999999, "፺፱፻፺፱፼፺፱፻፺፱"),
            (100000000, "፼፼"),
            (100000005, "፼፼፭"),
            (100000100, "፼፼፻"),
            (100010000, "፼፩፼"),
            (123456789, "፼፳፫፻፵፭፼፷፯፻፹፱"),
            (200000000, "፪፼፼"),
            (1000000000000, "፼፼፼"),
            (1000000000100, "፼፼፼፻"),
            (1000000010000, "፼፼፼፩፼"),
            (1000100000001, "፼፩፼፼፩"),
            (50000000000000, "፶፼፼፼"),
            (100000000010000, "፻፼፼፼፩፼"),
            (9999000000009999, "፺፱፻፺፱፼፼፼፺፱፻፺፱"),
            (10000000100000000, "፼፼፼፼፩፼፼"),
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

    def test_gz_to_ha_accepts_explicit_one(self):
        cases = [
            ("፩፻", 100),
            ("፩፻፩", 101),
            ("፩፼", 10000),
            ("፩፼፩፻", 10100),
            ("፩፻፼", 1000000),
            ("፩፼፼", 100000000),
            ("፩፼፩፼", 100010000),
        ]
        for gz_num, ha_num in cases:
            with self.subTest(gz_num=gz_num):
                self.assertEqual(self.convert(gz_num, "gz", "ha"), ha_num)

    def test_gz_to_ha_rejects_malformed(self):
        for gz_num in ["፩፩", "፲፲", "፩፲", "፻፻", "፼፻፻", "፪፻፫፻", "፲፻፻"]:
            with self.subTest(gz_num=gz_num):
                with self.assertRaises(ValueError):
                    self.convert(gz_num, "gz", "ha")

    def test_round_trip_is_one_to_one(self):
        seen = {}
        for ha_num in range(1, 200001):
            gz_num = self.convert(ha_num, "ha", "gz")
            self.assertNotIn(gz_num, seen, (ha_num, seen.get(gz_num)))
            seen[gz_num] = ha_num
            self.assertEqual(self.convert(gz_num, "gz", "ha"), ha_num, gz_num)


if __name__ == "__main__":
    unittest.main()
