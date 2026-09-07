from __future__ import annotations

import csv
import io
import re
import zipfile
from datetime import date
from pathlib import Path

import pandas as pd

from core.pipelines.defunciones_inegi.attributes import DefuncionesInegiTables
from core.pipelines.defunciones_inegi.config import settings
from core.pipelines.defunciones_inegi.constants import (
    CATALOG_ALIAS_OVERRIDES,
    FACT_MEMBER_DIR,
    FACT_MEMBER_EXCLUDE,
    LEGACY_CATALOG_ALIASES,
    SOURCE_ENCODINGS,
    ZIP_CONTENT_TYPES,
)
from core.utils.files import read_csv_from_zip
from core.utils.http import http_get
from core.utils.logger import get_console_logger
from core.utils.normalize import strip_accents
from core.utils.zip_members import resolve_member

logger = get_console_logger(__name__)


def _is_zip_response(response) -> bool:
    """INEGI responde 200 con la página de error cuando el año no existe."""
    content_type = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
    return content_type in ZIP_CONTENT_TYPES


def edition_url(year: int) -> str | None:
    """Primera plantilla de nombre que devuelve un ZIP real para ese año."""
    for template in settings.source_url_templates:
        url = settings.edition_url(year, template)
        response = http_get(url, timeout=settings.DOWNLOAD_TIMEOUT)
        if response.ok and _is_zip_response(response):
            return url
    return None


def available_editions(since_year: int | None = None, until_year: int | None = None) -> dict[int, str]:
    """Ediciones publicadas, de la más antigua a la más reciente."""
    start = max(since_year or settings.BACKFILL_MIN_YEAR, settings.BACKFILL_MIN_YEAR)
    end = until_year or date.today().year
    editions = {}
    for year in range(start, end + 1):
        url = edition_url(year)
        if url:
            editions[year] = url
            logger.info(f"[source] {year}: {url.rsplit('/', 1)[-1]}")
        else:
            logger.warning(f"[source] {year}: sin publicar")
    return editions


def download_edition(year: int, url: str, work_dir: Path) -> Path:
    """Descarga la edición una sola vez; en re-corridas reusa el ZIP en disco."""
    target = work_dir / f"edr_{year}.zip"
    if target.exists():
        logger.info(f"[source] {year}: reusando {target}")
        return target

    logger.info(f"[source] {year}: descargando {url}")
    response = http_get(url, timeout=settings.DOWNLOAD_TIMEOUT)
    response.raise_for_status()
    target.write_bytes(response.content)
    return target


_YEAR_SUFFIX = re.compile(r"[_]?\d{4}$")


def catalog_aliases(table: str) -> tuple[str, ...]:
    """Nombres posibles del CSV que alimenta *table*, del vigente al legado."""
    aliases = (CATALOG_ALIAS_OVERRIDES.get(table) or DefuncionesInegiTables(table).catalog_alias,)
    legacy = LEGACY_CATALOG_ALIASES.get(table)
    return (*aliases, legacy) if legacy else aliases


def _member_pattern(aliases: tuple[str, ...]) -> re.Pattern[str]:
    """Patrón anclado al nombre completo: buscar por subcadena hace que
    `localidad` capture `entidad_municipio_localidad_2024`."""
    options = "|".join(re.escape(alias) for alias in aliases)
    return re.compile(rf"(?:^|/)(?:{options})(?:_?\d{{4}})?\.csv$", re.IGNORECASE)


def find_member(archive: zipfile.ZipFile, member_dir: str, aliases: tuple[str, ...]) -> str | None:
    """Miembro que corresponde a alguno de los alias, o None si la edición no lo publica.

    Se busca sobre nombres sin acentos porque INEGI publica `tamaño_localidad.csv`
    y `año.csv`; el resultado se traduce de vuelta al nombre real del ZIP.
    """
    by_normalized = {strip_accents(name).lower(): name for name in archive.namelist()}
    expected = f"{member_dir}{strip_accents(aliases[0]).lower()}.csv"
    try:
        match = resolve_member(list(by_normalized), expected, _member_pattern(aliases), description=aliases[0])
    except FileNotFoundError:
        return None
    return by_normalized[match]


def fact_member(archive: zipfile.ZipFile) -> str:
    """CSV de hechos, descartando la nota y la bitácora de cambios."""
    for name in archive.namelist():
        normalized = strip_accents(name).lower()
        if not normalized.startswith(FACT_MEMBER_DIR) or not normalized.endswith(".csv"):
            continue
        if any(token in normalized for token in FACT_MEMBER_EXCLUDE):
            continue
        return name
    raise FileNotFoundError(f"El ZIP no trae CSV de hechos. Contenido: {sorted(archive.namelist())}")


def read_catalog_csv(archive: zipfile.ZipFile, member: str) -> pd.DataFrame:
    """Lee un catálogo tolerando los CSV mal formados de INEGI.

    Dos defectos reales, mismo origen y síntomas opuestos: una descripción con
    coma sin comillas ("Área industrial (taller, fabrica u obra)"). Si el
    archivo trae coma final, pandas la absorbe en una columna fantasma y trunca
    la descripción en silencio; si no la trae, revienta al tokenizar. Aquí los
    campos que sobran se reincorporan a la última columna real.
    """
    raw = archive.read(member)
    for encoding in SOURCE_ENCODINGS:
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            logger.warning(f"'{member}' no es {encoding}; probando el siguiente encoding")
    else:
        raise UnicodeDecodeError(f"Ningún encoding de {SOURCE_ENCODINGS} sirvió para '{member}'")

    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        return pd.DataFrame()

    # La coma final del header crea una columna sin nombre que no es un campo.
    header = list(rows[0])
    while header and not header[-1].strip():
        header.pop()
    width = len(header)

    records = []
    for row in rows[1:]:
        if not any(field.strip() for field in row):
            continue
        if len(row) > width:
            row = [*row[: width - 1], ",".join(row[width - 1 :]).rstrip(",")]
        # Un campo vacío es nulo, como lo trataría pandas.
        records.append([field or None for field in row] + [None] * (width - len(row)))

    return pd.DataFrame(records, columns=header, dtype=str)


def read_fact_chunks(archive: zipfile.ZipFile, member: str, chunk_size: int):
    """El CSV de hechos pesa cientos de MB: se recorre por lotes, nunca completo."""
    yield from read_csv_from_zip(archive, member, SOURCE_ENCODINGS, dtype=str, chunksize=chunk_size)
