"""Normalización del CSV de hechos: renombres, fechas, edad y centinelas."""

from __future__ import annotations

import pandas as pd

from core.pipelines.defunciones_inegi.constants import (
    DATE_PARTS,
    DAY_SENTINEL,
    EDAD_SENTINELS,
    EDAD_UNIT_DIVISOR,
    ENTIDAD_MAX_CLAVE,
    HOUR_SENTINEL,
    LUGAR_NACIMIENTO_COLUMN,
    MINUTE_SENTINEL,
    MONTH_SENTINEL,
    NUMERIC_SENTINELS,
    PAIS_SENTINELS,
    RENAME_HEADER,
    TIME_COLUMN,
    TIME_PARTS,
    YEAR_SENTINEL,
)
from core.utils.clean import to_nullable_int as to_int
from core.utils.normalize import lowercase_headers

EDAD_COLUMN = "edad"
CAPITULO_COLUMN = "capitulo"
GRUPO_COLUMN = "grupo"


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Nemónicos INEGI a nombres propios."""
    lowercase_headers(df)
    return df.rename(columns=RENAME_HEADER)


def build_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Colapsa día/mes/año en una fecha. Un centinela en cualquier parte anula la fecha."""
    for target, (day_col, month_col, year_col) in DATE_PARTS.items():
        if not {day_col, month_col, year_col} <= set(df.columns):
            df[target] = pd.NaT
            continue

        day, month, year = (to_int(df[col]) for col in (day_col, month_col, year_col))
        valid = (day != DAY_SENTINEL) & (month != MONTH_SENTINEL) & (year != YEAR_SENTINEL)
        valid &= day.notna() & month.notna() & year.notna()

        # Se arma como texto porque `to_datetime` sobre columnas Int64 revienta
        # con NA. `coerce` además descarta fechas imposibles (31 de febrero).
        stamps = (
            year.astype(str).str.zfill(4) + "-" + month.astype(str).str.zfill(2) + "-" + day.astype(str).str.zfill(2)
        ).where(valid)
        df[target] = pd.to_datetime(stamps, format="%Y-%m-%d", errors="coerce").dt.date

    return df.drop(columns=[col for parts in DATE_PARTS.values() for col in parts], errors="ignore")


def build_time(df: pd.DataFrame) -> pd.DataFrame:
    """Hora y minuto se guardan como un solo TIME; 99 en cualquiera lo anula."""
    hour_col, minute_col = TIME_PARTS
    if not {hour_col, minute_col} <= set(df.columns):
        df[TIME_COLUMN] = None
        return df

    hour, minute = to_int(df[hour_col]), to_int(df[minute_col])
    valid = (hour != HOUR_SENTINEL) & (minute != MINUTE_SENTINEL) & hour.notna() & minute.notna()
    stamps = (hour.astype(str).str.zfill(2) + ":" + minute.astype(str).str.zfill(2)).where(valid)
    df[TIME_COLUMN] = pd.to_datetime(stamps, format="%H:%M", errors="coerce").dt.time

    return df.drop(columns=[hour_col, minute_col], errors="ignore")


def split_edad(df: pd.DataFrame) -> pd.DataFrame:
    """`edad` codifica unidad + cantidad: 4023 son 23 años, 1002 son dos horas."""
    if EDAD_COLUMN not in df.columns:
        df["edad_unidad"] = pd.NA
        df["edad_cantidad"] = pd.NA
        return df

    edad = to_int(df[EDAD_COLUMN])
    df["edad_unidad"] = (edad // EDAD_UNIT_DIVISOR).astype("Int64")
    cantidad = (edad % EDAD_UNIT_DIVISOR).astype("Int64")
    df["edad_cantidad"] = cantidad.where(~edad.isin(EDAD_SENTINELS))
    return df.drop(columns=[EDAD_COLUMN], errors="ignore")


def split_lugar_nacimiento(df: pd.DataFrame) -> pd.DataFrame:
    """`ent_nac` mezcla entidad federativa y país; los centinelas ya los cubre `nacionalidad`."""
    if LUGAR_NACIMIENTO_COLUMN not in df.columns:
        df["entidad_nacimiento_id"] = pd.NA
        df["pais_nacimiento"] = pd.NA
        return df

    lugar = to_int(df[LUGAR_NACIMIENTO_COLUMN])
    is_sentinel = lugar.isin(PAIS_SENTINELS)
    df["entidad_nacimiento_id"] = lugar.where((lugar <= ENTIDAD_MAX_CLAVE) & ~is_sentinel)
    df["pais_nacimiento"] = lugar.where((lugar > ENTIDAD_MAX_CLAVE) & ~is_sentinel)
    return df.drop(columns=[LUGAR_NACIMIENTO_COLUMN], errors="ignore")


def apply_numeric_sentinels(df: pd.DataFrame) -> pd.DataFrame:
    """Semanas de gestación y peso traen "no aplica"/"no especificado" como número."""
    for column, sentinels in NUMERIC_SENTINELS.items():
        if column not in df.columns:
            df[column] = pd.NA
            continue
        values = to_int(df[column])
        df[column] = values.where(~values.isin(sentinels))
    return df


def normalize_facts(df: pd.DataFrame) -> pd.DataFrame:
    """Pipeline completo de un lote del CSV de hechos."""
    df = rename_columns(df)
    df = build_dates(df)
    df = build_time(df)
    df = split_edad(df)
    df = split_lugar_nacimiento(df)
    return apply_numeric_sentinels(df)
