import pandas as pd


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
        except:
            return None

    return series.apply(convert)


def parse_date(series: pd.Series) -> pd.Series:
    """
    Parse date values to datetime.date.
    - Valid values -> datetime.date
    - Invalid values -> None
    """
    return pd.to_datetime(series, errors='coerce').dt.date
