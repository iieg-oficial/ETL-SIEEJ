import io
import zipfile
from datetime import date

import pandas as pd
import requests
import urllib3

from core.pipelines.enoe.constants import JALISCO_ENT, SDEM_COLS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"}


def current_trimestre() -> tuple[int, int]:
    today = date.today()
    return today.year, (today.month - 1) // 3 + 1


def trimestres_range(start_year: int, start_t: int) -> list[tuple[int, int]]:
    end_year, end_t = current_trimestre()
    result = []
    y, t = start_year, start_t
    while (y, t) <= (end_year, end_t):
        result.append((y, t))
        t += 1
        if t > 4:
            t = 1
            y += 1
    return result


def _parse_sdem(content: bytes, anio: int, trimestre: int) -> pd.DataFrame:
    # Try both "enoe" (regular) and "enoen" (COVID-19 period: 2020 T2–2022)
    for prefix in ("enoe", "enoen"):
        csv_name = (
            f"conjunto_de_datos_sdem_{prefix}_{anio}_{trimestre}t/"
            f"conjunto_de_datos/conjunto_de_datos_sdem_{prefix}_{anio}_{trimestre}t.csv"
        )
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                with z.open(csv_name) as f:
                    df = pd.read_csv(f, encoding="latin-1", low_memory=False)
            break
        except KeyError:
            continue
    else:
        raise ValueError(f"SDEM CSV not found in ZIP for {anio} T{trimestre}")

    df.columns = [c.strip().lower() for c in df.columns]
    ent_col = "cve_ent" if "cve_ent" in df.columns else "ent"
    df = df[df[ent_col] == JALISCO_ENT].copy()
    available = [c for c in SDEM_COLS if c in df.columns]
    return df[available]


def download_sdem(url: str, anio: int, trimestre: int, fallbacks: list[str] | None = None) -> pd.DataFrame:
    all_urls = [url] + (fallbacks or [])
    last_exc: Exception | None = None
    for u in all_urls:
        try:
            response = requests.get(u, verify=False, timeout=120, headers=_HEADERS)
            response.raise_for_status()
            return _parse_sdem(response.content, anio, trimestre)
        except Exception as e:
            last_exc = e
            continue
    raise last_exc  # type: ignore[misc]
