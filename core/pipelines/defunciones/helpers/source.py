from __future__ import annotations

import io
import re
import zipfile
from urllib.parse import urljoin

import pandas as pd

from core.pipelines.defunciones.constants import (
    CATALOG_PAGE_URL,
    CATALOG_ZIP_PATTERN,
    CLAVE_ALIASES,
    CLAVE_COL,
    DESCRIPCION_ALIASES,
    DESCRIPCION_COL,
    DOWNLOAD_TIMEOUT,
    REGISTRO_ZIP_PATTERN,
    SOURCE_ENCODINGS,
)
from core.utils.http import http_get


def _http_get(url: str) -> bytes:
    response = http_get(url, timeout=DOWNLOAD_TIMEOUT)
    response.raise_for_status()
    return response.content


def edition_year(url: str) -> int:
    path = url.split("?", 1)[0]
    years = re.findall(r"(?:19|20)\d{2}", path)
    if not years:
        return -1
    return max(int(year) for year in years)


_edition_year = edition_year


def _discover_urls(pattern: str, page_url: str) -> list[str]:
    html = _http_get(page_url).decode("utf-8", errors="replace")
    hrefs = re.findall(rf'href="([^"]*{pattern})"', html)
    if not hrefs:
        hrefs = re.findall(pattern, html)
    urls = {urljoin(page_url, href) for href in hrefs}
    return sorted(urls, key=_edition_year)


def discover_catalog_urls(page_url: str = CATALOG_PAGE_URL) -> list[str]:
    return _discover_urls(CATALOG_ZIP_PATTERN, page_url)


def discover_registro_urls(page_url: str = CATALOG_PAGE_URL) -> list[str]:
    return _discover_urls(REGISTRO_ZIP_PATTERN, page_url)


def latest_catalog_url(page_url: str = CATALOG_PAGE_URL) -> str:
    urls = discover_catalog_urls(page_url)
    if not urls:
        raise RuntimeError(f"No catalog editions found at {page_url}")
    return urls[-1]


def latest_registro_url(page_url: str = CATALOG_PAGE_URL) -> str:
    urls = discover_registro_urls(page_url)
    if not urls:
        raise RuntimeError(f"No registro editions found at {page_url}")
    return urls[-1]


def download_zip(url: str) -> bytes:
    return _http_get(url)


download_catalog_zip = download_zip


def _iter_csv_members(zip_bytes: bytes, prefix: str = "") -> list[tuple[str, bytes]]:
    members: list[tuple[str, bytes]] = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        for name in archive.namelist():
            lower = name.lower()
            if lower.endswith(".csv"):
                members.append((f"{prefix}{name}", archive.read(name)))
            elif lower.endswith(".zip"):
                members.extend(_iter_csv_members(archive.read(name), prefix=f"{prefix}{name}/"))
    return members


def find_catalog_csv(
    zip_bytes: bytes,
    keyword: str,
    exclude: tuple[str, ...] = (),
) -> tuple[str, bytes]:
    matches = [
        (name, raw)
        for name, raw in _iter_csv_members(zip_bytes)
        if keyword in name.lower() and not any(term in name.lower() for term in exclude)
    ]
    if not matches:
        raise FileNotFoundError(f"No CSV matching '{keyword}' (excluding {exclude}) in ZIP")
    if len(matches) > 1:
        raise ValueError(f"Ambiguous match for '{keyword}': {[name for name, _ in matches]}")
    return matches[0]


def _decode(raw: bytes) -> str:
    for encoding in SOURCE_ENCODINGS:
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode(SOURCE_ENCODINGS[-1], errors="replace")


def _canonical_column(name: str, aliases: tuple[str, ...]) -> str | None:
    normalized = name.strip().lower()
    return normalized if normalized in aliases else None


def read_catalog_csv(raw: bytes, member: str = "") -> pd.DataFrame:
    lines = _decode(raw).splitlines()
    header_idx = next(
        (index for index, line in enumerate(lines) if any(alias in line.lower() for alias in CLAVE_ALIASES)),
        None,
    )
    if header_idx is None:
        raise ValueError(f"No header row (clave/cve) found in {member}")

    frame = pd.read_csv(
        io.StringIO("\n".join(lines[header_idx:])),
        dtype=str,
        keep_default_na=False,
    )

    rename: dict[str, str] = {}
    for column in frame.columns:
        if _canonical_column(column, CLAVE_ALIASES):
            rename[column] = CLAVE_COL
        elif _canonical_column(column, DESCRIPCION_ALIASES):
            rename[column] = DESCRIPCION_COL
    frame = frame.rename(columns=rename)[[CLAVE_COL, DESCRIPCION_COL]]

    for column in (CLAVE_COL, DESCRIPCION_COL):
        frame[column] = frame[column].str.strip()
    return frame


def read_capitulo_grupo_csv(raw: bytes, member: str = "") -> pd.DataFrame:
    lines = _decode(raw).splitlines()
    header_idx = next(
        (i for i, line in enumerate(lines) if "descrip" in line.lower()),
        None,
    )
    if header_idx is None:
        raise ValueError(f"No header row found in {member}")
    frame = pd.read_csv(io.StringIO("\n".join(lines[header_idx:])), dtype=str, keep_default_na=False)
    rename = {}
    for column in frame.columns:
        low = column.strip().lower()
        if low in ("cap", "capitulo"):
            rename[column] = "cap"
        elif low in ("gpo", "grupo"):
            rename[column] = "gpo"
        elif low.startswith("descrip"):
            rename[column] = "descripcion"
    frame = frame.rename(columns=rename)[["cap", "gpo", "descripcion"]]
    for column in frame.columns:
        frame[column] = frame[column].str.strip()
    return frame


def find_registro_csv(zip_bytes: bytes) -> tuple[str, bytes]:
    members = _iter_csv_members(zip_bytes)
    if not members:
        raise FileNotFoundError("No CSV found in registro ZIP")
    return max(members, key=lambda item: len(item[1]))


def read_registro_csv(raw: bytes) -> pd.DataFrame:
    frame = pd.read_csv(
        io.BytesIO(raw),
        dtype=str,
        encoding=_registro_encoding(raw),
        keep_default_na=False,
    )
    frame.columns = [col.strip().lower() for col in frame.columns]
    return frame


def _registro_encoding(raw: bytes) -> str:
    for encoding in SOURCE_ENCODINGS:
        try:
            raw[:4096].decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue
    return SOURCE_ENCODINGS[-1]
