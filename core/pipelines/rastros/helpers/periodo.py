from __future__ import annotations

import pandas as pd

from core.utils.logger import get_console_logger

PERIODO_FORMAT = "%Y%m"
logger = get_console_logger(__name__)


def build_fecha(anio: pd.Series, mes: pd.Series) -> pd.Series:
    """Combine ANIO and ID_MES into the first day of the reference month.

    ID_MES ships padded with tabs in the source, hence the strip. Unparseable
    periods become NaT so the caller can drop them.
    """
    periodo = anio.str.strip() + mes.str.strip()
    fecha = pd.to_datetime(periodo, format=PERIODO_FORMAT, errors="coerce")

    invalid = int(fecha.isna().sum())
    if invalid:
        logger.warning(f"{invalid:,} rows with an unreadable period (ANIO/ID_MES), they will be dropped")

    return fecha
