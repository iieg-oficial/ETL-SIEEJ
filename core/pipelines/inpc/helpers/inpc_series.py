import json
import re
import requests
from typing import Optional
from retry import retry

from core.utils.logger import get_logger
from core.pipelines.inpc.config import settings

logger = get_logger("inpc.series")


def _headers_base(referer: str) -> dict[str, str]:
    return {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.inegi.org.mx",
        "Referer": referer,
        "User-Agent": "Mozilla/5.0",
    }


def _get_nodes(
    session: requests.Session,
    id_estructura: str,
    id_nodo: str,
    sig_nivel: int = 2,
    timeout: int = 30,
) -> str:
    payload = {
        "sigNivel": sig_nivel,
        "idNodo": id_nodo,
        "esquemaBD": "",
        "paramfuente": "0|CargaInicial",
        "paramEstructura": id_estructura,
        "notas": [
            {
                "__type": "IP.TrasversalModelos.NotaSerieInfo",
                "IdSerie": "",
                "DescripcionNota": "",
                "IdNota": 0,
                "NotasPie": "Las desagregaciones del INPC solo tienen valor informativo.",
            }
        ],
        "open": False,
    }

    referer = f"{settings.INPC_BASE_URL}?idEstructura={id_estructura}"
    r = session.post(
        settings.INPC_URL_NODOS,
        data=json.dumps(payload),
        headers=_headers_base(referer=referer),
        timeout=timeout,
    )
    r.raise_for_status()
    return r.json().get("d", "") or ""


def _extract_children_pairs(html: str) -> list[tuple[str, str]]:
    return re.findall(r'data-id=(\d+).*?data-title="([^"]+)"', html)


def _find_indice_general_node(children: list[tuple[str, str]]) -> Optional[str]:
    for nid, title in children:
        t = title.strip().lower()
        if "índice general" in t or "indice general" in t:
            return nid
    return None


def _extract_series_ids(html: str) -> list[str]:
    ids = re.findall(r"CBox_Serie_(\d+)", html)
    seen = set()
    out: list[str] = []
    for x in ids:
        x = x.strip()
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _normalize_and_add_indice_general(series_ids: list[str]) -> list[str]:
    seen = set()
    clean: list[str] = []
    for s in series_ids:
        s = s.strip()
        if s and s not in seen:
            seen.add(s)
            clean.append(s)

    clean = sorted(clean, key=int)

    indice_general = str(int(clean[0]) - 1)
    if indice_general not in seen:
        clean = [indice_general] + clean

    return clean


@retry((requests.RequestException, ConnectionError), tries=6, delay=5, jitter=3, logger=logger)
def discover_series_ids(
    id_estructura: str,
    session: Optional[requests.Session] = None,
    timeout: int = 30,
) -> list[str]:
    owns_session = session is None
    if owns_session:
        session = requests.Session()

    try:
        session.get(
            settings.INPC_BASE_URL,
            params={"idEstructura": id_estructura},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=timeout,
        )

        container_id = f"{id_estructura}00100010"
        html_1 = _get_nodes(session, id_estructura, container_id, sig_nivel=2, timeout=timeout)

        series = _extract_series_ids(html_1)
        if series:
            return _normalize_and_add_indice_general(series)

        children = _extract_children_pairs(html_1)
        if not children:
            raise ValueError(f"Children was not found for idEstructura={id_estructura}")

        id_nodo_indice = _find_indice_general_node(children)

        if id_nodo_indice:
            html_2 = _get_nodes(session, id_estructura, id_nodo_indice, sig_nivel=3)
            series = _extract_series_ids(html_2)
            return _normalize_and_add_indice_general(series)

        series = []
        for nodo_id, _ in children:
            html = _get_nodes(session, id_estructura, nodo_id, sig_nivel=3)
            series.extend(_extract_series_ids(html))

        series = _normalize_and_add_indice_general(series)

        if not series:
            raise ValueError(f"Series was not found for idEstructura={id_estructura}")

        return series

    finally:
        if owns_session:
            session.close()
