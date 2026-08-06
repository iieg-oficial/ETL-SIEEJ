from __future__ import annotations

import pandas as pd

from core.utils.logger import get_console_logger

PERIODO_FORMAT = "%Y%m"

logger = get_console_logger(__name__)


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


def build_fecha(anio: pd.Series, mes: pd.Series) -> pd.Series:
    """Combine a year and a month column into the first day of the reference month.

    Sources disagree on how they ship the period: ESGRM publishes both fields as
    text and pads the month with tabs, EMEC publishes them as integers with no
    padding. Both are accepted here so the callers do not each reinvent the cast.

    Unparseable periods become NaT so the caller can drop them instead of losing
    the whole edition to a raise.
    """
    periodo = _period_part(anio, width=4) + _period_part(mes, width=2)
    fecha = pd.to_datetime(periodo, format=PERIODO_FORMAT, errors="coerce")

    invalid = int(fecha.isna().sum())
    if invalid:
        logger.warning(f"{invalid:,} rows with an unreadable period (year/month), they will be dropped")

    return fecha


def _period_part(values: pd.Series, width: int) -> pd.Series:
    """Render a year or month column as a fixed-width string.

    Numeric columns are zero padded ( 5 -> "05"); text columns only get their
    surrounding whitespace stripped, since padding a string such as "basura"
    would hide a bad value instead of turning it into NaT.
    """
    if pd.api.types.is_numeric_dtype(values):
        numeric = pd.to_numeric(values, errors="coerce").astype("Int64")
        return numeric.astype(str).str.zfill(width)

    return values.astype(str).str.strip()
