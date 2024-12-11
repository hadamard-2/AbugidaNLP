import unittest
from abugida import CalendarConverter


class TestConvertCalendar(unittest.TestCase):
    def setUp(self):
        self.convert = CalendarConverter().convert
        self.test_cases = [
            ("2017-03-11", "2024-11-20"),
            ("1993-10-13", "2001-06-20"),
            ("1860-08-06", "1868-04-13"),
            ("2012-09-11", "2020-05-19"),
        ]

    def test_ec_to_gc(self):
        for ec_date, gc_date in self.test_cases:
            with self.subTest(ec_date=ec_date):
                result = self.convert(ec_date, "EC", "GC")
                self.assertEqual(result, gc_date)

    def test_gc_to_ec(self):
        for ec_date, gc_date in self.test_cases:
            with self.subTest(gc_date=gc_date):
                result = self.convert(gc_date, "GC", "EC")
                self.assertEqual(result, ec_date)


if __name__ == "__main__":
    unittest.main()
