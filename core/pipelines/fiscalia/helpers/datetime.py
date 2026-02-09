import pandas as pd


def parse_hora(series: pd.Series) -> pd.Series:
    """
    Convierte valores de hora a formato 'HH:MM'.
    - Valores válidos '%H:%M' -> 'HH:MM'
    - Valores inválidos (decimales, 'N.D.', etc.) -> None
    """
    def convert(val):
        if pd.isna(val):
            return None
        try:
            # Intentar parsear como hora
            parsed = pd.to_datetime(str(val), format='%H:%M', errors='raise')
            return parsed.strftime('%H:%M')
        except:
            return None

    return series.apply(convert)


def parse_fecha(series: pd.Series) -> pd.Series:
    """
    Convierte valores de fecha a formato DATE.
    - Valores válidos -> datetime.date
    - Valores inválidos -> None
    """
    return pd.to_datetime(series, errors='coerce').dt.date
