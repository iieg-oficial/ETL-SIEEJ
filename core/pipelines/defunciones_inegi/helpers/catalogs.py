"""Normalización de los CSV de `catalogos/` a registros (clave, descripcion)."""

from __future__ import annotations

import pandas as pd

from core.pipelines.defunciones_inegi.constants import (
    CAPITULO_CLAVE_FACTOR,
    DISTRITO_MAX_CLAVE,
    DISTRITO_MIN_CLAVE,
    ENTIDAD_OAXACA,
    PRESERVED_TERMS,
    CLAVE_ALIASES,
    DESCRIPCION_ALIASES,
    PAIS_MAX_CLAVE,
    PAIS_MIN_CLAVE,
    RAZON_MATERNA_EMPTY_CLAVE,
    RAZON_MATERNA_EMPTY_KEY,
)
from core.utils.clean import strip_text, to_nullable_int
from core.utils.geo import localidad_code
from core.utils.logger import get_console_logger

logger = get_console_logger(__name__)


def _pick_column(df: pd.DataFrame, aliases: tuple[str, ...]) -> str:
    """INEGI alterna CVE/cve/clave y DESCRIP/descrip entre ediciones."""
    lowered = {str(col).strip().lower(): col for col in df.columns}
    for alias in aliases:
        if alias in lowered:
            return lowered[alias]
    raise KeyError(f"Ninguna de {aliases} está en {list(df.columns)}")


def _clean(series: pd.Series) -> pd.Series:
    return strip_text(series.astype(str))


def _clean_key(series: pd.Series) -> pd.Series:
    """Las ediciones 2017-2019 dejan tabuladores dentro de las comillas."""
    return _clean(series).str.replace(r"\s+", "", regex=True)


def canonical_text_key(series: pd.Series) -> pd.Series:
    """Quita el cero a la izquierda de las claves alfanuméricas.

    `grupo_lista_mexicana` publica el catálogo como `1` y los hechos como `01`
    en las ediciones 2017-2021: sin canonizar, el join se pierde en silencio.
    Las claves que empiezan por letra (`E49`, `A000`) no se tocan.
    """
    stripped = series.astype(str).str.strip().str.lstrip("0")
    return stripped.where(stripped != "", "0")


def sentence_case(series: pd.Series) -> pd.Series:
    """Sólo la primera letra en mayúscula, preservando siglas y nombres propios."""
    normalized = series.str.replace(r"\s+", " ", regex=True).str.strip()
    normalized = normalized.str[0].str.upper() + normalized.str[1:].str.lower()
    for term in PRESERVED_TERMS:
        normalized = normalized.str.replace(term, term, case=False, regex=True)
    return normalized


def catalog_records(df: pd.DataFrame, numeric_key: bool = True, to_sentence_case: bool = False) -> list[dict]:
    """Registros (clave, descripcion) de un catálogo de dominio cerrado."""
    clave = _clean(df[_pick_column(df, CLAVE_ALIASES)])
    descripcion = _clean(df[_pick_column(df, DESCRIPCION_ALIASES)])

    frame = pd.DataFrame({"clave": clave, "descripcion": descripcion})
    frame["clave"] = to_nullable_int(frame["clave"]) if numeric_key else canonical_text_key(frame["clave"])
    if to_sentence_case:
        frame["descripcion"] = sentence_case(frame["descripcion"])
    frame = frame.dropna(subset=["clave", "descripcion"])
    frame = frame[frame["descripcion"] != ""]
    frame = frame.drop_duplicates(subset=["clave"], keep="first")
    return frame.to_dict("records")


def razon_materna_records(df: pd.DataFrame) -> list[dict]:
    """La clave de "no contribuye" viene como la palabra `Vacio`, no como un número."""
    clave = _clean(df[_pick_column(df, CLAVE_ALIASES)])
    descripcion = _clean(df[_pick_column(df, DESCRIPCION_ALIASES)])

    frame = pd.DataFrame({"clave": clave, "descripcion": descripcion})
    empty = frame["clave"].str.lower() == RAZON_MATERNA_EMPTY_KEY
    frame.loc[empty, "clave"] = str(RAZON_MATERNA_EMPTY_CLAVE)
    frame["clave"] = to_nullable_int(frame["clave"])
    return frame.dropna(subset=["clave"]).drop_duplicates(subset=["clave"]).to_dict("records")


def capitulo_grupo_records(df: pd.DataFrame) -> list[dict]:
    """(CAP, GPO, DESCRIP), con GPO vacío = total del capítulo.

    La edición 2017 publica una sola clave `CVE` = capítulo * 100 + grupo, con
    grupo 0 para el total; se descompone para que ambas formas convivan.
    """
    lowered = {str(col).strip().lower(): col for col in df.columns}
    descripcion = _clean(df[_pick_column(df, DESCRIPCION_ALIASES)])

    if "cap" in lowered:
        capitulo = to_nullable_int(_clean_key(df[lowered["cap"]]))
        grupo = to_nullable_int(_clean_key(df[lowered["gpo"]]))
    else:
        clave = to_nullable_int(_clean_key(df[_pick_column(df, CLAVE_ALIASES)]))
        capitulo = (clave // CAPITULO_CLAVE_FACTOR).astype("Int64")
        grupo = (clave % CAPITULO_CLAVE_FACTOR).astype("Int64")
        grupo = grupo.where(grupo != 0)

    frame = pd.DataFrame({"capitulo": capitulo, "grupo": grupo, "descripcion": descripcion})
    frame = frame.dropna(subset=["capitulo"])
    frame = frame[frame["descripcion"] != ""]
    frame = frame.drop_duplicates(subset=["capitulo", "grupo"], keep="first")
    return frame.astype(object).where(frame.notna(), None).to_dict("records")


def pais_records(df: pd.DataFrame) -> list[dict]:
    """Sólo el rango de países: las entidades federativas viven en cvegeo_states."""
    records = catalog_records(df)
    frame = pd.DataFrame(records)
    if frame.empty:
        return []
    within_range = frame["clave"].between(PAIS_MIN_CLAVE, PAIS_MAX_CLAVE)
    frame = frame[within_range].rename(columns={"descripcion": "nombre_pais"})
    return frame.to_dict("records")


def distrito_oaxaca_records(df: pd.DataFrame) -> list[dict]:
    """Los 30 distritos de Oaxaca, que viajan en el catálogo de localidades.

    Son filas con `cve_loc` en cero, así que `localidad_records` las descarta:
    un distrito no es una localidad. Sin este catálogo, `dis_re_oax` queda como
    un entero sin significado.
    """
    lowered = {str(col).strip().lower(): col for col in df.columns}
    frame = pd.DataFrame(
        {
            "cve_ent": to_nullable_int(_clean_key(df[lowered["cve_ent"]])),
            "clave": to_nullable_int(_clean_key(df[lowered["cve_mun"]])),
            "descripcion": _clean(df[_pick_column(df, DESCRIPCION_ALIASES)]),
        }
    )
    frame = frame[
        (frame["cve_ent"] == ENTIDAD_OAXACA)
        & frame["clave"].between(DISTRITO_MIN_CLAVE, DISTRITO_MAX_CLAVE)
        & (frame["descripcion"] != "")
    ]
    frame = frame.drop_duplicates(subset=["clave"], keep="first")
    logger.info(f"[catalogs] distritos de Oaxaca: {len(frame)}")
    return frame[["clave", "descripcion"]].to_dict("records")


def localidad_records(df: pd.DataFrame) -> list[dict]:
    """Sólo el nivel localidad: entidad y municipio se resuelven contra cvegeo.

    `cvegeo` se deriva siempre de las tres claves: sólo la edición 2024 lo
    publica como columna propia.
    """
    lowered = {str(col).strip().lower(): col for col in df.columns}
    frame = pd.DataFrame(
        {
            "cve_ent": to_nullable_int(_clean_key(df[lowered["cve_ent"]])),
            "cve_mun": to_nullable_int(_clean_key(df[lowered["cve_mun"]])),
            "cve_loc": to_nullable_int(_clean_key(df[lowered["cve_loc"]])),
            "localidad": _clean(df[_pick_column(df, DESCRIPCION_ALIASES)]),
        }
    )
    frame = frame.dropna(subset=["cve_ent", "cve_mun", "cve_loc", "localidad"])
    frame = frame[(frame["cve_loc"] != 0) & (frame["localidad"] != "")]

    frame["cvegeo"] = [
        localidad_code(ent, mun, loc)
        for ent, mun, loc in zip(frame["cve_ent"], frame["cve_mun"], frame["cve_loc"], strict=True)
    ]
    frame = frame.dropna(subset=["cvegeo"]).drop_duplicates(subset=["cvegeo"], keep="first")
    logger.info(f"[catalogs] localidades: {len(frame)}")
    return frame[["cvegeo", "cve_ent", "cve_mun", "cve_loc", "localidad"]].to_dict("records")
