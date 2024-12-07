def count_leap_years(year, calendar_system):
    if calendar_system == "EC":
        return year // 4
    elif calendar_system == "GC":
        return (year // 4) - (year // 100) + (year // 400)
    else:
        raise ValueError("Invalid calendar system")


def is_leap_year(year, calendar_system):
    if calendar_system == "EC":
        return year % 4 == 0
    elif calendar_system == "GC":
        return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
    else:
        raise ValueError("Invalid calendar system")


def is_date_valid(date, calendar_system):
    from datetime import datetime

    if calendar_system == "EC":
        year, month, day = map(int, date.split("-"))
        pagume_day_count = 6 if is_leap_year(year, calendar_system) else 5
        return (
            year > 0
            and 1 <= month <= 13
            and 1 <= day <= (30 if month != 13 else pagume_day_count)
        )
    elif calendar_system == "GC":
        try:
            datetime.strptime(date, "%Y-%m-%d")
            return True
        except ValueError:
            return False


def get_absolute_day_count(date_str, calendar_system):
    """
    Expects date to be provided in the format YYYY-MM-DD.
    Returns the number of days that have passed since the beginning of the calendar system.
    """
    from datetime import date

    if calendar_system == "EC":
        year, month, day = map(int, date_str.split("-"))
        if is_date_valid(date_str, calendar_system):
            return (
                (year * 365 + count_leap_years(year, calendar_system))
                + ((month - 1) * 30)
                + day
            )
        return ValueError("Invalid Date in the Ethiopian Calendar")
    elif calendar_system == "GC":
        return date.fromisoformat(date_str).toordinal()


def get_date_from_absolute_day_count(day_count, calendar_system):
    """
    Given the number of days that have passed since the beginning of the calendar system,
    returns the date in the format YYYY-MM-DD.
    """
    if calendar_system == "EC":
        # 365 * 4 = 1460
        # Ethiopian calendar adds a leap day every 1460 days
        day_count -= day_count // 1460

        year = day_count // 365
        day_count -= year * 365
        month = day_count // 30
        day_count -= month * 30
        day = day_count

        month += 1

        return f"{year:04d}-{month:02d}-{day:02d}"
    elif calendar_system == "GC":
        from datetime import date

        return date.fromordinal(day_count).isoformat()
    else:
        raise ValueError("Invalid calendar system")


def convert_calendar(date, from_calendar, to_calendar):
    """
    Converts a date from one calendar system to another.
    """
    if not is_date_valid(date, from_calendar):
        raise ValueError("Invalid date")

    if [from_calendar, to_calendar] != [
        "EC",
        "GC",
    ] and [
        from_calendar,
        to_calendar,
    ] != [
        "GC",
        "EC",
    ]:
        raise ValueError("Invalid calendar systems provided")

    day_count = get_absolute_day_count(date, from_calendar)

    EC_GC_DAY_DIFFERENCE = 2430
    if from_calendar == "EC":
        day_count += EC_GC_DAY_DIFFERENCE
    else:
        day_count -= EC_GC_DAY_DIFFERENCE

    return get_date_from_absolute_day_count(day_count, to_calendar)
