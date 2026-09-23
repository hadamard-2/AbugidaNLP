from datetime import date, datetime


class CalendarConverter:
    """
    A class to handle calendar conversion between Ethiopian Calendar (EC) and Gregorian Calendar (GC).

    Both calendars are converted through the Julian Day Number (JDN), using the Beyene-Kudlek
    algorithm for the Ethiopian side (B. Beyene and M. Kudlek, "Calendars in Ethiopia",
    International Conference of Ethiopian Studies XV).

    Attributes:
        JD_EPOCH_OFFSET_AMETE_MIHRET (int): Beyene-Kudlek JDN offset for the Amete Mihret era;
            Meskerem 1 of year 1 falls 365 days after it, on JDN 1724221.
        JDN_ORDINAL_OFFSET (int): Difference between a JDN and Python's proleptic Gregorian
            ordinal (0001-01-01 is ordinal 1 and JDN 1721426).
    """

    JD_EPOCH_OFFSET_AMETE_MIHRET = 1723856
    JDN_ORDINAL_OFFSET = 1721425

    def convert(self, date_str: str, from_calendar: str, to_calendar: str) -> str:
        """
        Convert a date from one calendar system to another.

        Args:
            date_str (str): The date to be converted, formatted as "YYYY-MM-DD".
            from_calendar (str): The source calendar system, either "EC" (Ethiopian) or "GC" (Gregorian).
            to_calendar (str): The target calendar system, either "EC" (Ethiopian) or "GC" (Gregorian).

        Returns:
            str: The converted date in the format "YYYY-MM-DD" for the target calendar system.

        Raises:
            ValueError: If the `date_str` is invalid for the source calendar system.
            ValueError: If the `from_calendar` or `to_calendar` arguments are not "EC" or "GC".
            ValueError: If the calendar conversion between the specified systems is unsupported.
            ValueError: If the calculated date for the target calendar system is invalid (e.g., negative or zero days).
        """
        if not self._is_date_valid(date_str, from_calendar):
            raise ValueError(
                "Invalid date format or value for the source calendar system"
            )

        if [from_calendar, to_calendar] not in [["EC", "GC"], ["GC", "EC"]]:
            raise ValueError("Unsupported calendar conversion")

        jdn = self._date_to_jdn(date_str, from_calendar)
        return self._jdn_to_date(jdn, to_calendar)

    def _is_date_valid(self, date_str: str, calendar_system: str) -> bool:
        if calendar_system == "EC":
            year, month, day = map(int, date_str.split("-"))
            pagume_day_count = 6 if self._is_leap_year(year, calendar_system) else 5
            return (
                year > 0
                and 1 <= month <= 13
                and 1 <= day <= (30 if month != 13 else pagume_day_count)
            )
        elif calendar_system == "GC":
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                return True
            except ValueError:
                return False
        else:
            raise ValueError("Invalid calendar system")

    def _date_to_jdn(self, date_str: str, calendar_system: str) -> int:
        if calendar_system == "EC":
            year, month, day = map(int, date_str.split("-"))
            return (
                (self.JD_EPOCH_OFFSET_AMETE_MIHRET + 365)
                + 365 * (year - 1)
                + year // 4
                + 30 * month
                + day
                - 31
            )
        elif calendar_system == "GC":
            return date.fromisoformat(date_str).toordinal() + self.JDN_ORDINAL_OFFSET
        else:
            raise ValueError("Invalid calendar system")

    def _jdn_to_date(self, jdn: int, calendar_system: str) -> str:
        if calendar_system == "EC":
            days = jdn - self.JD_EPOCH_OFFSET_AMETE_MIHRET
            r = days % 1461
            n = r % 365 + 365 * (r // 1460)
            year = 4 * (days // 1461) + r // 365 - r // 1460
            month = n // 30 + 1
            day = n % 30 + 1
            if year < 1:
                raise ValueError("Invalid date for the target calendar system")
            return f"{year:04d}-{month:02d}-{day:02d}"
        elif calendar_system == "GC":
            ordinal = jdn - self.JDN_ORDINAL_OFFSET
            if ordinal < 1:
                raise ValueError("Invalid date for the target calendar system")
            return date.fromordinal(ordinal).isoformat()
        else:
            raise ValueError("Invalid calendar system")

    def _is_leap_year(self, year: int, calendar_system: str) -> bool:
        if calendar_system == "EC":
            return year % 4 == 3
        elif calendar_system == "GC":
            return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
        else:
            raise ValueError("Invalid calendar system")
