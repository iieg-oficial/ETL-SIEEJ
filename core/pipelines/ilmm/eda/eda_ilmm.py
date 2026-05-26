"""
EDA script para el pipeline ilmm (Indicadores de Ocupacion y Empleo - INEGI).

Fuente: ZIP descargable por año (trimestre 1 de cada año como muestra representativa).
URL patrón: https://www.inegi.org.mx/contenidos/programas/ilmm/datosabiertos/
            conjunto_de_datos_ilmm_{year}_1t_csv.zip

Ejecutar con:
    conda run -n etl python core/pipelines/ilmm/eda/eda_ilmm.py
"""

import io
import json
import zipfile
from datetime import date
from pathlib import Path

import pandas as pd
import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BASE_URL = (
    "https://www.inegi.org.mx/contenidos/programas/ilmm/datosabiertos/"
    "conjunto_de_datos_ilmm_{year}_1t_csv.zip"
)
SAMPLE_YEARS = [2024, 2020, 2017]  # primary + 2 historical for consistency check
PRIMARY_YEAR = 2024
CATALOG_THRESHOLD = 100
NULL_VALUES = ["NA", "N/A", "null", "nan", ""]
NATURAL_KEY = ["ent", "mun", "est"]
REPORT_PATH = Path("core/pipelines/ilmm/eda/reporte_eda.json")
EXTRACT_DIR = Path("data/extract/ilmm")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def download_zip(year: int) -> bytes:
    """Download and return the raw ZIP bytes for the given year."""
    url = BASE_URL.format(year=year)
    print(f"   Downloading {url} …")
    response = requests.get(url, timeout=180)
    response.raise_for_status()
    print(f"   ZIP downloaded: {len(response.content):,} bytes")
    return response.content


def _read_csv_auto_encoding(raw: bytes, **kwargs) -> pd.DataFrame:
    """Try utf-8-sig first (handles BOM), then fall back to latin-1."""
    for enc in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(io.BytesIO(raw), encoding=enc, **kwargs)
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode CSV with utf-8-sig or latin-1")


def extract_dataframes(zip_bytes: bytes) -> tuple[pd.DataFrame, pd.DataFrame | None, list[str]]:
    """
    Extract the main dataset CSV and the est catalog CSV from the ZIP.
    Returns (df_main, df_est, members).
    """
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        members = zf.namelist()

        # Main dataset CSV
        main_candidates = [
            m for m in members if "conjunto_de_datos" in m.lower() and m.lower().endswith(".csv")
        ]
        if not main_candidates:
            raise ValueError(f"No main dataset CSV found in ZIP. Members: {members}")
        main_csv_name = main_candidates[0]
        df_main = _read_csv_auto_encoding(
            zf.read(main_csv_name),
            sep=",",
            dtype=str,
            keep_default_na=False,
            na_values=NULL_VALUES,
        )
        # Strip BOM artifact from column names if present
        df_main.columns = [c.lstrip("\ufeff") for c in df_main.columns]

        # Catalog est.csv (skip mun.csv and ent.csv)
        est_candidates = [
            m for m in members
            if m.lower().endswith("est.csv") and "catalogos" in m.lower()
        ]
        df_est: pd.DataFrame | None = None
        if est_candidates:
            df_est = _read_csv_auto_encoding(
                zf.read(est_candidates[0]),
                sep=",",
                dtype=str,
                keep_default_na=False,
                na_values=NULL_VALUES,
            )
            df_est.columns = [c.lstrip("\ufeff") for c in df_est.columns]

    return df_main, df_est, members


def analyze_columns(df: pd.DataFrame, natural_key: list[str]) -> list[dict]:
    """Return per-column analysis dictionaries."""
    total = len(df)
    infos: list[dict] = []
    for col in df.columns:
        serie = df[col]
        nulos = int(serie.isna().sum())
        nulos_pct = round(nulos / total * 100, 4) if total else 0.0
        cardinalidad = int(serie.nunique(dropna=True))
        es_clave = col in natural_key
        # est is both a natural-key component and a catalog (maps to est.csv)
        es_catalogo = cardinalidad < CATALOG_THRESHOLD
        muestra = [str(v) for v in sorted(serie.dropna().unique().tolist())[:10]]
        infos.append(
            {
                "nombre_original": col,
                "tipo_original": str(serie.dtype),
                "cardinalidad": cardinalidad,
                "nulos_count": nulos,
                "nulos_pct": nulos_pct,
                "es_clave": es_clave,
                "es_catalogo": es_catalogo,
                "muestra_valores": muestra,
            }
        )
    return infos


# ---------------------------------------------------------------------------
# Step 1 — Download primary year (2024)
# ---------------------------------------------------------------------------
print("=" * 60)
print(f"1. Downloading ZIP for primary year {PRIMARY_YEAR} …")
EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

zip_2024 = download_zip(PRIMARY_YEAR)

# ---------------------------------------------------------------------------
# Step 2 — Inspect ZIP contents
# ---------------------------------------------------------------------------
print("\n2. Inspecting ZIP contents …")
with zipfile.ZipFile(io.BytesIO(zip_2024)) as zf:
    all_members = zf.namelist()

print(f"   Files in ZIP: {all_members}")

df_main, df_est, _ = extract_dataframes(zip_2024)
total_filas, total_cols = df_main.shape

# Save main CSV to extract dir for optional inspection (not inside eda/)
with zipfile.ZipFile(io.BytesIO(zip_2024)) as zf:
    main_candidates = [
        m for m in zf.namelist()
        if "conjunto_de_datos" in m.lower() and m.lower().endswith(".csv")
    ]
    main_csv_name = main_candidates[0]
    csv_path = EXTRACT_DIR / Path(main_csv_name).name
    csv_path.write_bytes(zf.read(main_csv_name))
    print(f"   Main CSV saved to: {csv_path}")

# ---------------------------------------------------------------------------
# Step 3 — Main CSV overview
# ---------------------------------------------------------------------------
print("\n3. Main CSV overview …")
print(f"   Rows   : {total_filas:,}")
print(f"   Columns: {total_cols}")
print(f"   Column names: {list(df_main.columns)}")
print("\n   dtypes:")
print(df_main.dtypes.to_string())
print("\n   First rows:")
print(df_main.head(5).to_string())
print("\n   Describe (all as object/str):")
print(df_main.describe(include="all").to_string())

# ---------------------------------------------------------------------------
# Step 4 — Column-level analysis
# ---------------------------------------------------------------------------
print("\n4. Column-level analysis …")
col_infos = analyze_columns(df_main, NATURAL_KEY)
for info in col_infos:
    print(
        f"   {info['nombre_original']:<20} dtype={info['tipo_original']:<8} "
        f"nulos={info['nulos_pct']:.2f}%  card={info['cardinalidad']}  "
        f"muestra={info['muestra_valores'][:5]}"
    )

# ---------------------------------------------------------------------------
# Step 4b — Key columns detail
# ---------------------------------------------------------------------------
print("\n4b. Key columns detail …")
KEY_COLS_DETAIL = ["ent", "mun", "est", "informales", "ocupados"]
for col in KEY_COLS_DETAIL:
    if col in df_main.columns:
        vals = sorted(df_main[col].dropna().unique().tolist())
        num = pd.to_numeric(df_main[col], errors="coerce").dropna()
        num_range = f"min={num.min():.4f}  max={num.max():.4f}" if not num.empty else "non-numeric"
        print(f"   {col}: {len(vals)} uniq → {vals[:20]}  |  {num_range}")

# mun zero-padding check: any municipality code with fewer than 3 digits needs LPAD
if "mun" in df_main.columns:
    mun_digits = df_main["mun"].dropna().apply(
        lambda x: len(str(int(float(x))).lstrip("-"))
    )
    mun_min_digits = int(mun_digits.min())
    mun_max_digits = int(mun_digits.max())
    lpad_needed = mun_min_digits < 3
    print(f"\n   mun digits range: min={mun_min_digits}  max={mun_max_digits}  → LPAD(mun::text, 3, '0') needed: {lpad_needed}")

# ---------------------------------------------------------------------------
# Step 4c — Natural key uniqueness
# ---------------------------------------------------------------------------
print("\n4c. Natural key uniqueness …")
key_present = [c for c in NATURAL_KEY if c in df_main.columns]
if len(key_present) == len(NATURAL_KEY):
    dup_mask = df_main.duplicated(subset=key_present, keep=False)
    n_dup = int(dup_mask.sum())
    print(f"   Duplicates on {NATURAL_KEY}: {n_dup}")
    key_unique = n_dup == 0
else:
    n_dup = -1
    key_unique = False
    print(f"   WARNING: Natural key columns not all present. Found: {key_present}")

# ---------------------------------------------------------------------------
# Step 5 — Catalog est.csv
# ---------------------------------------------------------------------------
print("\n5. Catalog est.csv …")
if df_est is not None:
    print(f"   Columns: {list(df_est.columns)}")
    print(f"   Rows: {len(df_est)}")
    print(df_est.to_string())
    est_col_infos = analyze_columns(df_est, [])
else:
    print("   WARNING: est.csv not found in ZIP")
    est_col_infos = []

# ---------------------------------------------------------------------------
# Step 6 — Historical consistency check (2020, 2017)
# ---------------------------------------------------------------------------
print("\n6. Historical consistency check …")
historical_years = [y for y in SAMPLE_YEARS if y != PRIMARY_YEAR]
primary_cols = set(df_main.columns)
consistency_results: list[dict] = []

for year in historical_years:
    print(f"\n   --- Year {year} ---")
    try:
        zip_hist = download_zip(year)
        df_hist, _, _ = extract_dataframes(zip_hist)
        hist_cols = set(df_hist.columns)
        missing_in_hist = primary_cols - hist_cols
        extra_in_hist = hist_cols - primary_cols
        print(f"   Rows: {len(df_hist):,}  Columns: {len(df_hist.columns)}")
        print(f"   Missing vs 2024: {missing_in_hist}")
        print(f"   Extra vs 2024  : {extra_in_hist}")
        same_cols = primary_cols == hist_cols
        print(f"   Same column set: {same_cols}")

        # Check dtypes consistency
        dtype_diffs: list[str] = []
        for col in primary_cols & hist_cols:
            if str(df_main[col].dtype) != str(df_hist[col].dtype):
                dtype_diffs.append(
                    f"{col}: 2024={df_main[col].dtype} vs {year}={df_hist[col].dtype}"
                )
        if dtype_diffs:
            print(f"   dtype differences: {dtype_diffs}")
        else:
            print(f"   dtype differences: none")

        consistency_results.append(
            {
                "year": year,
                "filas": len(df_hist),
                "columnas": len(df_hist.columns),
                "columnas_faltantes": sorted(missing_in_hist),
                "columnas_extra": sorted(extra_in_hist),
                "columnas_identicas": same_cols,
                "dtype_diffs": dtype_diffs,
            }
        )
    except Exception as exc:
        print(f"   ERROR for year {year}: {exc}")
        consistency_results.append({"year": year, "error": str(exc)})

# ---------------------------------------------------------------------------
# Step 7 — Build report
# ---------------------------------------------------------------------------
print("\n7. Building reporte_eda.json …")

# Determine tipo_homologado mapping
TIPO_MAP: dict[str, str] = {
    "ent": "SMALLINT",
    "mun": "SMALLINT",
    "est": "SMALLINT",
    "pea": "NUMERIC(10,4)",
    "informales": "NUMERIC(10,4)",
    "ocupados": "NUMERIC(10,4)",
}

report_cols: list[dict] = []
for info in col_infos:
    col = info["nombre_original"]
    tipo_sql = TIPO_MAP.get(col, "VARCHAR(255)")
    # Refine based on cardinality/pattern
    if col not in TIPO_MAP:
        num = pd.to_numeric(df_main[col], errors="coerce").dropna()
        if not num.empty:
            if (num == num.astype(int)).all():
                tipo_sql = "INTEGER"
            else:
                tipo_sql = "NUMERIC(10,4)"
    report_cols.append(
        {
            "nombre_original": col,
            "tipo_original": info["tipo_original"],
            "tipo_homologado": tipo_sql,
            "es_clave": info["es_clave"],
            "es_catalogo": info["es_catalogo"],
            "valores_unicos": info["cardinalidad"],
            "nulos_pct": info["nulos_pct"],
            "muestra_valores": info["muestra_valores"],
        }
    )

# Catalog est.csv columns
est_report_cols: list[dict] = []
if df_est is not None:
    for info in est_col_infos:
        est_report_cols.append(
            {
                "nombre_original": info["nombre_original"],
                "tipo_original": info["tipo_original"],
                "tipo_homologado": "VARCHAR(255)",
                "es_clave": info["nombre_original"] == "est",
                "es_catalogo": True,
                "valores_unicos": info["cardinalidad"],
                "nulos_pct": info["nulos_pct"],
                "muestra_valores": info["muestra_valores"],
            }
        )

notas: list[str] = []
if not key_unique:
    notas.append(f"Se detectaron {n_dup} filas con llave natural duplicada en {NATURAL_KEY}.")
notas.append(
    "mun requiere LPAD(mun::text, 3, '0') para construir los 3 dígitos del municipio cuando mun < 100; "
    "cve_geo = LPAD(ent::text, 2, '0') || LPAD(mun::text, 3, '0'). "
    "ent=0 y mun=0 indican nivel nacional/estatal (filas agregadas)."
)
notas.append(
    "est=1 → estimación puntual, est=2 → error estándar. "
    "La tasa de desocupación se deriva de: 100 - ocupados cuando est=1."
)
notas.append(
    "Ignorar catalogos/mun.csv y catalogos/ent.csv del ZIP; usar cv_geo del repositorio."
)
notas.append(f"Consistencia histórica verificada para años: {[r['year'] for r in consistency_results]}.")
if consistency_results:
    for res in consistency_results:
        if res.get("columnas_faltantes") or res.get("columnas_extra"):
            notas.append(
                f"Año {res['year']}: columnas faltantes={res.get('columnas_faltantes')}, "
                f"extra={res.get('columnas_extra')}."
            )

reporte: dict = {
    "flujo": "ilmm",
    "fecha_analisis": str(date.today()),
    "fuente": {
        "url": BASE_URL,
        "formato": "zip_csv",
        "patron_url": "conjunto_de_datos_ilmm_{year}_1t_csv.zip",
        "anios_disponibles": SAMPLE_YEARS,
        "num_archivos": 1,
        "periodicidad": "anual",
        "encoding": "latin-1",
        "separador": ",",
    },
    "dimensiones": {
        "filas": total_filas,
        "columnas": total_cols,
    },
    "llave_natural": NATURAL_KEY,
    "llave_unica": key_unique,
    "columnas": report_cols,
    "catalogo_est": {
        "nombre_archivo": "catalogos/est.csv",
        "columnas": est_report_cols,
        "filas": len(df_est) if df_est is not None else 0,
    },
    "geografia": {
        "nivel": "municipal",
        "columnas_geo": ["ent", "mun"],
        "construccion_cvegeo": "LPAD(ent::text, 2, '0') || LPAD(mun::text, 3, '0')",
    },
    "consistencia_historica": consistency_results,
    "notas": notas,
}

REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    json.dump(reporte, f, indent=2, ensure_ascii=False)

print(f"\nReport saved to: {REPORT_PATH}")
print(f"  Flujo        : {reporte['flujo']}")
print(f"  Filas        : {reporte['dimensiones']['filas']:,}")
print(f"  Columnas     : {reporte['dimensiones']['columnas']}")
print(f"  Llave única  : {reporte['llave_unica']}")
catalogos_candidatos = [c["nombre_original"] for c in report_cols if c["es_catalogo"]]
print(f"  Catálogos    : {catalogos_candidatos}")
print("\nDone.")
