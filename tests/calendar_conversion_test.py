import unittest
from datetime import date, timedelta
from abugida import CalendarConverter


class TestConvertCalendar(unittest.TestCase):
    def setUp(self):
        self.convert = CalendarConverter().convert
        # Expected pairs cross-checked against ICU's Ethiopic calendar (Amete Mihret era)
        self.test_cases = [
            ("2017-03-11", "2024-11-20"),
            ("1993-10-13", "2001-06-20"),
            ("1860-08-06", "1868-04-13"),
            ("2012-09-11", "2020-05-19"),
            ("2015-13-06", "2023-09-11"),  # Pagume 6 of a leap year
            ("2016-13-05", "2024-09-10"),  # last day of a common year
            ("2017-04-29", "2025-01-07"),  # Genna
            ("2017-04-30", "2025-01-08"),  # 30th day of a month
            ("2018-13-05", "2026-09-10"),
            ("2019-01-01", "2026-09-11"),
            ("1892-06-22", "1900-03-01"),  # after the Gregorian 1900 non-leap day
            ("2092-13-05", "2100-09-11"),  # New Year shifts to Sept 12 after 2100
            ("2093-01-01", "2100-09-12"),
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

    def test_pagume_6_only_in_leap_years(self):
        # Ethiopian leap years are the years with year % 4 == 3
        self.assertEqual(self.convert("2011-13-06", "EC", "GC"), "2019-09-11")
        for ec_date in ["2016-13-06", "2017-13-06", "2018-13-06"]:
            with self.subTest(ec_date=ec_date):
                with self.assertRaises(ValueError):
                    self.convert(ec_date, "EC", "GC")

    def test_consecutive_days_round_trip(self):
        # Every Gregorian day maps to the Ethiopian day after the previous one, and back
        day = date(1900, 1, 1)
        previous = self.convert(day.isoformat(), "GC", "EC")
        while day < date(2100, 12, 31):
            day += timedelta(days=1)
            ec_date = self.convert(day.isoformat(), "GC", "EC")
            self.assertEqual(ec_date, self._next_ec_day(previous), day.isoformat())
            self.assertEqual(self.convert(ec_date, "EC", "GC"), day.isoformat())
            previous = ec_date

    def _next_ec_day(self, ec_date):
        year, month, day = map(int, ec_date.split("-"))
        month_length = 30 if month != 13 else (6 if year % 4 == 3 else 5)
        if day < month_length:
            day += 1
        elif month < 13:
            month, day = month + 1, 1
        else:
            year, month, day = year + 1, 1, 1
        return f"{year:04d}-{month:02d}-{day:02d}"


if __name__ == "__main__":
    unittest.main()
