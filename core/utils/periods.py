def next_month_period(year: int, month: int) -> tuple[int, int]:
    month += 1
    if month > 12:
        return year + 1, 1
    return year, month


def generate_monthly_periods(start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
    periods = []
    year, month = start
    while (year, month) <= end:
        periods.append((year, month))
        year, month = next_month_period(year, month)
    return periods
