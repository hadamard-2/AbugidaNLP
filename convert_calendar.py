from datetime import date, datetime


class CalendarConverter:
    """
    A class to handle calendar conversion between Ethiopian Calendar (EC) and Gregorian Calendar (GC).
    
    Attributes:
        EC_GC_DAY_DIFFERENCE (int): The constant difference in days between the Ethiopian Calendar
            and the Gregorian Calendar. Specifically, the Ethiopian calendar lags 2430 days behind 
            the Gregorian calendar.
    """

    EC_GC_DAY_DIFFERENCE = 2430

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

        day_count = self._get_absolute_day_count(date_str, from_calendar)

        if from_calendar == "EC":
            day_count += self.EC_GC_DAY_DIFFERENCE
        else:
            day_count -= self.EC_GC_DAY_DIFFERENCE

        if day_count < 1:
            raise ValueError("Invalid date for the target calendar system")

        return self._absolute_day_count_to_date(day_count, to_calendar)

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

    def _get_absolute_day_count(self, date_str: str, calendar_system: str) -> int:
        if calendar_system == "EC":
            year, month, day = map(int, date_str.split("-"))
            if self._is_date_valid(date_str, calendar_system):
                return (
                    (year * 365 + self._count_leap_years(year, calendar_system))
                    + ((month - 1) * 30)
                    + day
                )
            raise ValueError("Invalid date in the Ethiopian Calendar")
        elif calendar_system == "GC":
            return date.fromisoformat(date_str).toordinal()
        else:
            raise ValueError("Invalid calendar system")

    def _absolute_day_count_to_date(self, day_count: int, calendar_system: str) -> str:
        if calendar_system == "EC":
            day_count -= day_count // 1460

            year = day_count // 365
            day_count -= year * 365
            month = day_count // 30
            day_count -= month * 30
            day = day_count

            month += 1
            return f"{year:04d}-{month:02d}-{day:02d}"
        elif calendar_system == "GC":
            return date.fromordinal(day_count).isoformat()
        else:
            raise ValueError("Invalid calendar system")

    def _count_leap_years(self, year: int, calendar_system: str) -> int:
        if calendar_system == "EC":
            return year // 4
        elif calendar_system == "GC":
            return (year // 4) - (year // 100) + (year // 400)
        else:
            raise ValueError("Invalid calendar system")

    def _is_leap_year(self, year: int, calendar_system: str) -> bool:
        if calendar_system == "EC":
            return year % 4 == 0
        elif calendar_system == "GC":
            return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
        else:
            raise ValueError("Invalid calendar system")
