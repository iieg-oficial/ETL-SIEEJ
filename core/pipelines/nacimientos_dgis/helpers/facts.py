"""Normalización del CSV de SINAC: renombres, booleanos, centinelas y claves geográficas."""

from __future__ import annotations

import pandas as pd

from core.pipelines.nacimientos_dgis.constants import (
    COMPOSITE_GEO,
    DIAGNOSTICO_NINGUNA,
    ENTIDAD_SOURCE,
    INTEGER_COLUMNS,
    INTERVAL_COLUMNS,
    LOCALIDAD_ENTIDAD_FACTOR,
    LOCALIDAD_MUNICIPIO_FACTOR,
    MUNICIPIO_FACTOR,
    NUMERIC_SENTINELS,
    RENAME_HEADER,
    SI_NO_COLUMNS,
    TIME_COLUMNS,
    TIME_SENTINEL,
)
from core.utils.clean import strip_text, to_nullable_int as to_int

CLUES_LENGTH = 11
MINUTES_PER_HOUR = 60
DIAGNOSTICO_COLUMNS = ("diagnostico_1", "diagnostico_2")


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Nemónicos SINAC a nombres propios."""
    return df.rename(columns=RENAME_HEADER)


def apply_si_no(df: pd.DataFrame) -> pd.DataFrame:
    """Deja la clave SI/NO cruda para que el load la resuelva contra `cat_si_no`.

    El dominio tiene cinco valores (0 no especificado, 1 sí, 2 no, 8 no aplica,
    9 se ignora). Un `boolean` metería los tres negativos en el mismo NULL y
    esa diferencia no se recupera después.
    """
    for column in SI_NO_COLUMNS:
        df[column] = to_int(df[column]) if column in df.columns else pd.NA
    return df


def apply_numeric_sentinels(df: pd.DataFrame) -> pd.DataFrame:
    """Peso, talla, gestación y conteos traen "no especificado" como número."""
    for column, sentinels in NUMERIC_SENTINELS.items():
        if column not in df.columns:
            df[column] = pd.NA
            continue
        values = to_int(df[column])
        df[column] = values.where(~values.isin(sentinels))
    return df


def build_times(df: pd.DataFrame) -> pd.DataFrame:
    """`HH:MM`, con `99:99` como "no especificado"."""
    for column in TIME_COLUMNS:
        if column not in df.columns:
            df[column] = None
            continue
        stamps = strip_text(df[column].astype(str))
        stamps = stamps.where(stamps != TIME_SENTINEL)
        df[column] = pd.to_datetime(stamps, format="%H:%M", errors="coerce").dt.time
    return df


def build_intervals(df: pd.DataFrame) -> pd.DataFrame:
    """El tiempo de traslado viaja como `HH:MM`; se guarda en minutos.

    Un entero de minutos se agrega y se compara sin ambigüedad, que es lo que
    se le va a pedir. Guardar el texto original obligaría a parsear en cada
    consulta.
    """
    for column in INTERVAL_COLUMNS:
        target = f"{column}_minutos"
        if column not in df.columns:
            df[target] = pd.NA
            continue
        parts = strip_text(df[column].astype(str)).str.extract(r"^(\d{1,3}):(\d{2})$")
        hours, minutes = to_int(parts[0]), to_int(parts[1])
        df[target] = (hours * MINUTES_PER_HOUR + minutes).where(minutes < MINUTES_PER_HOUR)
        df = df.drop(columns=[column])
    return df


def build_diagnosticos(df: pd.DataFrame) -> pd.DataFrame:
    """`0000` es "ninguna aparente": ausencia de anomalía, no una anomalía."""
    for column in DIAGNOSTICO_COLUMNS:
        if column not in df.columns:
            df[column] = pd.NA
            continue
        codes = strip_text(df[column].astype(str)).str.upper()
        df[column] = codes.where((codes != DIAGNOSTICO_NINGUNA) & (codes != "") & (codes.str.lower() != "nan"))
    return df


def build_clues(df: pd.DataFrame) -> pd.DataFrame:
    """La CLUES son 11 caracteres; lo que no los mide es un centinela, no una clave."""
    column = "establecimiento_salud"
    if column not in df.columns:
        df[column] = pd.NA
        return df
    codes = strip_text(df[column].astype(str)).str.upper()
    df[column] = codes.where(codes.str.len() == CLUES_LENGTH)
    return df


def build_composite_geo(df: pd.DataFrame) -> pd.DataFrame:
    """Municipio y localidad sólo son únicos junto con su entidad."""
    for target, source in ENTIDAD_SOURCE.items():
        df[target] = to_int(df[source]) if source in df.columns else pd.NA

    for target, (entidad_col, municipio_col, localidad_col) in COMPOSITE_GEO.items():
        sources = [entidad_col, municipio_col, *([localidad_col] if localidad_col else [])]
        if not set(sources) <= set(df.columns):
            df[target] = pd.NA
            continue

        entidad = to_int(df[entidad_col])
        municipio = to_int(df[municipio_col])
        if localidad_col is None:
            df[target] = entidad * MUNICIPIO_FACTOR + municipio
            continue

        localidad = to_int(df[localidad_col])
        df[target] = entidad * LOCALIDAD_ENTIDAD_FACTOR + municipio * LOCALIDAD_MUNICIPIO_FACTOR + localidad

    return df


def cast_integers(df: pd.DataFrame) -> pd.DataFrame:
    """Entero nullable donde el destino es entero.

    Una columna con nulos llega como float y el COPY escribiría "23.0", que
    `smallint` rechaza. El error sale hasta la carga, no en el transform.
    """
    for column in INTEGER_COLUMNS:
        if column in df.columns:
            df[column] = to_int(df[column])
    return df


def normalize_certificates(df: pd.DataFrame) -> pd.DataFrame:
    """Pipeline completo del microdato de un año, ya filtrado a Jalisco."""
    df = build_composite_geo(df.copy())
    df = rename_columns(df)
    df = apply_si_no(df)
    df = apply_numeric_sentinels(df)
    df = build_times(df)
    df = build_intervals(df)
    df = build_diagnosticos(df)
    df = build_clues(df)
    return cast_integers(df)
