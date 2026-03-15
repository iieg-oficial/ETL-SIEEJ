import pandas as pd
from datetime import date

def parse_hour(series: pd.Series) -> pd.Series:
    """
    Parse time values to 'HH:MM' format.
    - Valid '%H:%M' values -> 'HH:MM'
    - Invalid values (decimals, 'N.D.', etc.) -> None
    """
    def convert(val):
        if pd.isna(val):
            return None
        try:
            parsed = pd.to_datetime(str(val), format='%H:%M', errors='raise')
            return parsed.strftime('%H:%M')
        except ValueError:
            return None

    return series.apply(convert)


def parse_date(series: pd.Series, dayfirst: bool = False) -> pd.Series:
    """
    Parse date values to datetime.date.
    - Valid values -> datetime.date
    - Invalid values -> None
    """
    return pd.to_datetime(series, dayfirst=dayfirst, errors='coerce').dt.date


def parse_month_year(val) -> 'date | None':
    if pd.isna(val) or val is None:
        return None
    val = str(val).strip()
    if not val:
        return None
    try:
        parts = val.split("/")
        if len(parts) == 2:
            month, year = int(parts[0]), int(parts[1])
            return date(year, month, 1)
    except (ValueError, IndexError):
        pass
    return None
