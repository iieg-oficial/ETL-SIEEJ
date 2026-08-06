from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Optional
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from core.pipelines.delitos_fuero_comun.constants import SESNSP_URL
from core.utils.http import http_get
from core.utils.logger import get_console_logger
from core.utils.normalize import strip_accents

logger = get_console_logger(__name__)

_YEAR_RANGE = re.compile(r"\d{4}\s*-\s*\d{4}")


class _AnchorParser(HTMLParser):
    """Extrae el (texto, href) de cada <a> de la página."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: Optional[str] = None
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._href is not None:
            text = " ".join("".join(self._buffer).split())
            self.links.append((text, self._href))
            self._href = None
            self._buffer = []


def _as_direct_download(href: str) -> str:
    """Fuerza la descarga directa del archivo en vez de la vista previa de SharePoint."""
    parts = urlsplit(href)
    query = dict(parse_qsl(parts.query))
    query["download"] = "1"
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def _normalize(text: str) -> str:
    return " ".join(strip_accents(text).split()).lower()


def _is_vigente(normalized_text: str) -> bool:
    return (
        "fuero" in normalized_text
        and "delitos" in normalized_text
        and "incidencia delictiva municipal" in normalized_text
        and "tablero" not in normalized_text
        and not _YEAR_RANGE.search(normalized_text)
    )


def _is_historico(normalized_text: str) -> bool:
    return (
        "fuero" in normalized_text
        and "delitos" in normalized_text
        and "incidencia delictiva municipal" in normalized_text
        and "tablero" not in normalized_text
        and bool(_YEAR_RANGE.search(normalized_text))
    )


def resolve_urls() -> Optional[dict[str, str]]:
    """Resuelve, leyendo en vivo la página de SESNSP, las URLs vigentes de descarga.

    Los links de SharePoint cambian cada mes y sus IDs no son predecibles, pero el
    texto de los anchors que los envuelven es estable salvo por el rango de fechas,
    así que se identifican por ese texto en vez de por una URL fija.

    Devuelve None si no logra identificar ambos links, para que el caller decida
    hacer fallback a un valor conocido en vez de fallar.
    """
    try:
        response = http_get(SESNSP_URL, timeout=30)
        response.raise_for_status()
    except Exception as exc:
        logger.warning(f"No se pudo descargar la página de SESNSP ({SESNSP_URL}): {exc}")
        return None

    parser = _AnchorParser()
    parser.feed(response.text)

    url_2026: Optional[str] = None
    url_historico: Optional[str] = None
    for text, href in parser.links:
        if not href:
            continue
        normalized = _normalize(text)
        if url_2026 is None and _is_vigente(normalized):
            url_2026 = href
        if url_historico is None and _is_historico(normalized):
            url_historico = href

    if not url_2026 or not url_historico:
        logger.warning(
            "No se pudieron resolver ambos links en la página de SESNSP "
            f"(vigente={'ok' if url_2026 else 'faltante'}, historico={'ok' if url_historico else 'faltante'})"
        )
        return None

    return {"url_2026": _as_direct_download(url_2026), "url_historico": _as_direct_download(url_historico)}
