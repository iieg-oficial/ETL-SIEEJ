import io
import zipfile
from datetime import date

import pandas as pd
import requests
import urllib3

from core.pipelines.enoe_microdatos.constants import COE1_COLS, COE2_COLS, JALISCO_ENT, JOIN_KEYS, SDEM_COLS

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


def _find_csv(z: zipfile.ZipFile, prefix: str) -> str:
    for name in z.namelist():
        upper = name.upper()
        if upper.startswith(prefix.upper()) and upper.endswith(".CSV"):
            return name
    raise ValueError(f"No se encontró {prefix}*.csv en el ZIP")


def _read_table(z: zipfile.ZipFile, prefix: str, want_cols: list[str]) -> pd.DataFrame:
    csv_name = _find_csv(z, prefix)
    with z.open(csv_name) as f:
        df = pd.read_csv(f, encoding="latin-1", low_memory=False)
    df.columns = [c.strip().lower() for c in df.columns]
    available = [c for c in want_cols if c in df.columns]
    return df[available]


def download_sdem_coe(url: str, anio: int, trimestre: int, fallbacks: list[str] | None = None) -> pd.DataFrame:
    all_urls = [url] + (fallbacks or [])
    last_exc: Exception | None = None

    for u in all_urls:
        try:
            response = requests.get(u, verify=False, timeout=180, headers=_HEADERS)
            response.raise_for_status()

            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                sdem = _read_table(z, "ENOE_SDEM", SDEM_COLS)
                ent_col = "cve_ent" if "cve_ent" in sdem.columns else "ent"
                sdem = sdem[sdem[ent_col] == JALISCO_ENT].copy()

                coe1 = _read_table(z, "ENOE_COE1", COE1_COLS)
                coe2 = _read_table(z, "ENOE_COE2", COE2_COLS)

            join_sdem_coe1 = [k for k in JOIN_KEYS if k in sdem.columns and k in coe1.columns]
            df = sdem.merge(coe1, on=join_sdem_coe1, how="left")

            join_df_coe2 = [k for k in JOIN_KEYS if k in df.columns and k in coe2.columns]
            df = df.merge(coe2, on=join_df_coe2, how="left")

            return df

        except Exception as e:
            last_exc = e
            continue

    raise last_exc  # type: ignore[misc]
