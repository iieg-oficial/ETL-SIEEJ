"""Normalización de los XLSX de catálogo de SINAC a registros (clave, descripcion)."""

from __future__ import annotations

import pandas as pd

from core.pipelines.nacimientos_dgis.attributes import NacimientosDgisTables as T
from core.pipelines.nacimientos_dgis.constants import (
    ACRONYM_MAX_LEN,
    CLAVE_ALIASES,
    DESCRIPCION_ALIASES,
    DESCRIPCION_OVERRIDES,
    ENTIDAD_KEY_ALIASES,
    HEADER_SCAN_ROWS,
    LOCALIDAD_CLAVE_ALIASES,
    LOWERCASE_CONNECTORS,
    LOCALIDAD_ENTIDAD_FACTOR,
    LOCALIDAD_MUNICIPIO_FACTOR,
    MUNICIPIO_CLAVE_ALIASES,
    MUNICIPIO_FACTOR,
    MUNICIPIO_KEY_ALIASES,
    PRESERVED_TERMS,
    PROPER_NOUN_TABLES,
    TEXT_KEY_TABLES,
)
import re

from core.constants.accent_mappings import ACCENT_MAP
from core.utils.clean import strip_text, to_nullable_int
from core.utils.logger import get_console_logger

logger = get_console_logger(__name__)

# Catálogos cuya clave es compuesta: SINAC publica municipio y localidad por
# entidad, así que la clave del archivo no es única por sí sola.
COMPOSITE_CATALOGS = frozenset({T.CAT_MUNICIPIO, T.CAT_LOCALIDAD})


def find_header_row(raw: pd.DataFrame) -> int:
    """Fila del encabezado real.

    Los XLSX chicos traen filas en blanco y el nombre del catálogo antes de
    `Clave | Descripción`; los grandes ya traen el encabezado en la primera.
    """
    for position in range(min(HEADER_SCAN_ROWS, len(raw))):
        values = {str(value).strip().lower() for value in raw.iloc[position]}
        if values & set(CLAVE_ALIASES):
            return position
    raise KeyError(f"Ninguna de {CLAVE_ALIASES} aparece en las primeras {HEADER_SCAN_ROWS} filas")


def read_catalog(source) -> pd.DataFrame:
    """XLSX de catálogo a DataFrame con el encabezado ya puesto."""
    raw = pd.read_excel(source, header=None, dtype=str)
    header_row = find_header_row(raw)

    frame = raw.iloc[header_row + 1 :].copy()
    frame.columns = [str(value).strip().lower() for value in raw.iloc[header_row]]
    # Las columnas vacías a la izquierda llegan como "nan".
    return frame.loc[:, [column for column in frame.columns if column != "nan"]]


CONSONANTS = "bcdfghjklmnpqrstvwxyz"

# Un conector va entre espacios; una inicial va pegada a un punto, asi que la
# "A" de "A.C." no entra aqui.
CONNECTOR_RE = re.compile(rf"(?<= )({'|'.join(LOWERCASE_CONNECTORS)})(?= )", re.IGNORECASE)

# Siglas con vocal: hay que enumerarlas.
PRESERVED_RE = re.compile(rf"\b({'|'.join(PRESERVED_TERMS)})\b", re.IGNORECASE)

# Siglas sin vocal: una palabra espanola de dos a seis letras siempre tiene
# vocal, asi que lo que no la tiene es sigla. Cubre la cola larga (HGZ, CSS,
# CMF) que ninguna lista enumerada alcanza en 58 mil nombres de unidad.
ACRONYM_RE = re.compile(rf"\b([{CONSONANTS}]{{2,{ACRONYM_MAX_LEN}}})\b", re.IGNORECASE)


def _upper(match: re.Match) -> str:
    return match.group(0).upper()


def _lower(match: re.Match) -> str:
    return match.group(0).lower()


def normalize_descripcion(series: pd.Series, table: str) -> pd.Series:
    """SINAC publica todo en MAYUSCULAS; el repo no las quiere asi.

    Los nombres propios van en `title()` y las descripciones con solo la
    primera letra en mayuscula, segun `.claude/rules/databases.md`. A los
    nombres propios se les restituyen los acentos antes de cambiar la caja:
    el catalogo publica "TLAHUAC" y `ACCENT_MAP` trabaja en mayusculas.

    Todo va vectorizado: `cat_localidad` trae 351 mil filas y aplicar los 465
    patrones de acento fila por fila tarda minutos.
    """
    cased = series.str.replace(r"\s+", " ", regex=True).str.strip()

    if table in PROPER_NOUN_TABLES:
        for pattern, replacement in ACCENT_MAP.items():
            cased = cased.str.replace(pattern, replacement, regex=True)
        cased = cased.str.title().str.replace(CONNECTOR_RE, _lower, regex=True)
    else:
        cased = cased.str.lower().str.capitalize()

    cased = cased.str.replace(PRESERVED_RE, _upper, regex=True)
    return cased.str.replace(ACRONYM_RE, _upper, regex=True)


def _pick_column(df: pd.DataFrame, aliases: tuple[str, ...]) -> str:
    for alias in aliases:
        if alias in df.columns:
            return alias
    raise KeyError(f"Ninguna de {aliases} está en {list(df.columns)}")


def _composite_clave(df: pd.DataFrame, table: str) -> pd.Series:
    """Clave geográfica compuesta, con la misma forma que el `cve_geo` del pipeline."""
    entidad = to_nullable_int(df[_pick_column(df, ENTIDAD_KEY_ALIASES)])

    if table == T.CAT_MUNICIPIO:
        municipio = to_nullable_int(df[_pick_column(df, MUNICIPIO_CLAVE_ALIASES)])
        return entidad * MUNICIPIO_FACTOR + municipio

    municipio = to_nullable_int(df[_pick_column(df, MUNICIPIO_KEY_ALIASES)])
    localidad = to_nullable_int(df[_pick_column(df, LOCALIDAD_CLAVE_ALIASES)])
    return entidad * LOCALIDAD_ENTIDAD_FACTOR + municipio * LOCALIDAD_MUNICIPIO_FACTOR + localidad


def catalog_records(df: pd.DataFrame, table: str) -> list[dict]:
    """Registros (clave, descripcion) de un catálogo ya leído."""
    aliases = (*DESCRIPCION_OVERRIDES.get(table, ()), *DESCRIPCION_ALIASES)
    descripcion = strip_text(df[_pick_column(df, aliases)].astype(str))

    if table in COMPOSITE_CATALOGS:
        clave = _composite_clave(df, table)
    elif table in TEXT_KEY_TABLES:
        clave = strip_text(df[_pick_column(df, CLAVE_ALIASES)].astype(str)).str.upper()
    else:
        clave = to_nullable_int(df[_pick_column(df, CLAVE_ALIASES)])

    frame = pd.DataFrame({"clave": clave, "descripcion": descripcion})
    frame = frame.dropna(subset=["clave", "descripcion"])
    frame = frame[(frame["descripcion"] != "") & (frame["descripcion"].str.lower() != "nan")]
    if table in TEXT_KEY_TABLES:
        frame = frame[frame["clave"] != ""]

    frame["descripcion"] = normalize_descripcion(frame["descripcion"], table)
    frame = frame.drop_duplicates(subset=["clave"], keep="first")
    logger.info(f"[catalogs] {table}: {len(frame)} claves")
    return frame.to_dict("records")
