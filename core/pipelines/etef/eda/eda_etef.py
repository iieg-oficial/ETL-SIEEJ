"""
EDA script para el pipeline etef (Estadística de la Exportación de la
Empresa Formal - INEGI).

Alcance: análisis nacional completo (sin filtro CVE_ENT).
Estrategia objetivo: SCD2 por row_hash sobre columnas mutables.

Ejecutar con:
    conda run -n etl python core/pipelines/etef/eda/eda_etef.py
"""

import io
import json
import zipfile
from datetime import date
from pathlib import Path

import pandas as pd
import requests

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
SOURCE_URL = (
    "https://www.inegi.org.mx/contenidos/programas/exporta_ef/datosabiertos/conjunto_de_datos_eef_trimestral_csv.zip"
)
EXTRACT_DIR = Path("data/extract/etef")
REPORT_PATH = Path("core/pipelines/etef/eda/reporte_eda.json")
NATURAL_KEY = ["ANIO", "TRIMESTRE", "CVE_ENT", "CODIGO_SCIAN"]
MUTABLE_COLS = ["VAL_USD", "ESTATUS_CIFRA", "ESTATUS"]
CATALOG_THRESHOLD = 100  # cardinalidad máxima para considerar catálogo

# ---------------------------------------------------------------------------
# 1. Descarga del ZIP
# ---------------------------------------------------------------------------
print("=" * 60)
print("1. Descargando ZIP desde INEGI …")
EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

response = requests.get(SOURCE_URL, timeout=180)
response.raise_for_status()
zip_bytes = response.content
print(f"   ZIP descargado: {len(zip_bytes):,} bytes")

# ---------------------------------------------------------------------------
# 2. Inspección del ZIP
# ---------------------------------------------------------------------------
print("\n2. Inspeccionando contenido del ZIP …")
with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
    members = zf.namelist()
    print(f"   Archivos en el ZIP: {members}")

    csv_members = [m for m in members if m.lower().endswith(".csv")]
    if not csv_members:
        raise ValueError("No se encontró ningún CSV dentro del ZIP")

    # Preferir el CSV dentro de conjunto_de_datos/ (dataset principal)
    main_csv = [m for m in csv_members if "conjunto_de_datos" in m.lower()]
    csv_name = main_csv[0] if main_csv else csv_members[0]
    print(f"   CSV detectado: {csv_name}")

    csv_bytes = zf.read(csv_name)

# Guardar CSV en extract para inspección posterior (no dentro de eda/)
csv_path = EXTRACT_DIR / Path(csv_name).name
csv_path.write_bytes(csv_bytes)
print(f"   CSV guardado en: {csv_path}")

# ---------------------------------------------------------------------------
# 3. Lectura completa del CSV
# ---------------------------------------------------------------------------
print("\n3. Leyendo CSV completo …")
NULL_VALUES = ["NO APLICA", "NA", "N/A", "null", "nan", ""]

df = pd.read_csv(
    io.BytesIO(csv_bytes),
    encoding="utf-8",
    sep=",",
    dtype=str,  # Leer todo como string primero
    keep_default_na=False,
    na_values=NULL_VALUES,
)

total_filas, total_cols = df.shape
print(f"   Filas  : {total_filas:,}")
print(f"   Columnas: {total_cols}")
print(f"   Nombres de columnas: {list(df.columns)}")

# ---------------------------------------------------------------------------
# 4. Análisis de columnas
# ---------------------------------------------------------------------------
print("\n4. Analizando columnas …")

RENAME_MAP = {
    "PROD_EST": "prod_est",
    "COBERTURA": "cobertura",
    "ANIO": "anio",
    "MES": "mes",
    "TRIMESTRE": "trimestre",
    "CVE_ENT": "cve_ent",
    "CODIGO_SCIAN": "codigo_scian",
    "VAL_USD": "val_usd",
    "ESTATUS_CIFRA": "estatus_cifra",
    "ESTATUS": "estatus",
}

columnas_info: list[dict] = []
for col in df.columns:
    serie = df[col]
    nulos_count = int(serie.isna().sum())
    nulos_pct = round(nulos_count / total_filas * 100, 4) if total_filas else 0.0
    cardinalidad = int(serie.nunique(dropna=False))
    es_llave = col in NATURAL_KEY
    es_mutable = col in MUTABLE_COLS
    es_catalogo = cardinalidad < CATALOG_THRESHOLD and not es_llave

    columnas_info.append(
        {
            "nombre_original": col,
            "nombre_interno": RENAME_MAP.get(col, col.lower()),
            "tipo_dato": str(serie.dtype),
            "nulos_count": nulos_count,
            "nulos_pct": nulos_pct,
            "cardinalidad": cardinalidad,
            "es_llave_natural": es_llave,
            "es_mutable": es_mutable,
            "es_catalogo": es_catalogo,
        }
    )

    print(f"   {col:<20} dtype={str(serie.dtype):<8} nulos={nulos_pct:.2f}%  card={cardinalidad}")

# ---------------------------------------------------------------------------
# 4b. Cardinalidad de columnas específicas
# ---------------------------------------------------------------------------
print("\n4b. Cardinalidades específicas y muestras …")
CARD_COLS = [
    "PROD_EST",
    "COBERTURA",
    "TRIMESTRE",
    "MES",
    "CVE_ENT",
    "CODIGO_SCIAN",
    "ESTATUS_CIFRA",
    "ESTATUS",
]
for col in CARD_COLS:
    if col in df.columns:
        uniq = sorted(df[col].dropna().unique().tolist())
        print(f"   {col}: {len(uniq)} valores únicos → {uniq[:20]}")

# ---------------------------------------------------------------------------
# 4c. Rango de ANIO y VAL_USD
# ---------------------------------------------------------------------------
print("\n4c. Rangos numéricos …")
if "ANIO" in df.columns:
    anio_vals = pd.to_numeric(df["ANIO"], errors="coerce").dropna()
    print(f"   ANIO : min={int(anio_vals.min())}  max={int(anio_vals.max())}")
    anio_min = int(anio_vals.min())
    anio_max = int(anio_vals.max())
else:
    anio_min, anio_max = None, None

if "VAL_USD" in df.columns:
    val_num = pd.to_numeric(df["VAL_USD"], errors="coerce").dropna()
    print(f"   VAL_USD: min={val_num.min():.2f}  max={val_num.max():.2f}  nulos={df['VAL_USD'].isna().sum()}")

if "CVE_ENT" in df.columns:
    ent_uniq = sorted(df["CVE_ENT"].dropna().unique().tolist())
    print(f"   CVE_ENT valores únicos ({len(ent_uniq)}): {ent_uniq}")
else:
    ent_uniq = []

# ---------------------------------------------------------------------------
# 4d. Duplicados en la llave natural
# ---------------------------------------------------------------------------
print("\n4d. Duplicados en llave natural …")
llave_presente = [c for c in NATURAL_KEY if c in df.columns]
if len(llave_presente) == len(NATURAL_KEY):
    dup_mask = df.duplicated(subset=llave_presente, keep=False)
    n_dup = int(dup_mask.sum())
    print(f"   Filas duplicadas en {NATURAL_KEY}: {n_dup}")
    if n_dup > 0:
        print(df[dup_mask][llave_presente + MUTABLE_COLS].head(10).to_string())
else:
    n_dup = -1
    print(f"   Columnas de llave no disponibles: {llave_presente}")

# ---------------------------------------------------------------------------
# 5. Catálogos candidatos
# ---------------------------------------------------------------------------
print("\n5. Catálogos candidatos …")
catalogos: list[dict] = []
for info in columnas_info:
    if info["es_catalogo"]:
        col = info["nombre_original"]
        muestra = sorted(df[col].dropna().unique().tolist())[:20]
        tabla_name = f"stg_etef_cat_{info['nombre_interno']}"
        catalogos.append(
            {
                "nombre_columna": info["nombre_interno"],
                "nombre_tabla": tabla_name,
                "valores_unicos": info["cardinalidad"],
                "muestra": [str(v) for v in muestra],
            }
        )
        print(f"   {col}: {info['cardinalidad']} valores → {tabla_name}")

# ---------------------------------------------------------------------------
# 6. Resumen de columnas mutables / inmutables
# ---------------------------------------------------------------------------
print("\n6. Columnas mutables (candidatas a SCD2 hash) …")
mutables_confirmadas = [info["nombre_interno"] for info in columnas_info if info["es_mutable"]]
print(f"   {mutables_confirmadas}")

# ---------------------------------------------------------------------------
# 7. Producción del reporte_eda.json
# ---------------------------------------------------------------------------
print("\n7. Generando reporte_eda.json …")

# Periodo: ANIO-TRIMESTRE min/max
if "TRIMESTRE" in df.columns and anio_min is not None:
    tri_min_row = df[df["ANIO"] == str(anio_min)]["TRIMESTRE"].dropna()
    tri_max_row = df[df["ANIO"] == str(anio_max)]["TRIMESTRE"].dropna()
    trim_min = tri_min_row.min() if not tri_min_row.empty else "T1"
    trim_max = tri_max_row.max() if not tri_max_row.empty else "T4"
    periodo_min = f"{anio_min}-{trim_min}"
    periodo_max = f"{anio_max}-{trim_max}"
else:
    periodo_min = str(anio_min)
    periodo_max = str(anio_max)

notas: list[str] = []
if n_dup > 0:
    notas.append(f"Se detectaron {n_dup} filas con llave natural duplicada (múltiples revisiones del mismo dato).")
notas.append(
    "El nombre del CSV dentro del ZIP puede variar entre publicaciones de INEGI; "
    "el extractor debe detectarlo dinámicamente."
)
notas.append("El pipeline anterior filtraba CVE_ENT=14 (Jalisco). La nueva versión es nacional sin filtro geográfico.")

reporte: dict = {
    "flujo": "etef",
    "fecha_analisis": str(date.today()),
    "fuente": {
        "url": SOURCE_URL,
        "tipo": "zip_csv",
        "nombre_csv": csv_name,
        "encoding": "utf-8",
        "separador": ",",
    },
    "resumen": {
        "total_filas": total_filas,
        "total_columnas": total_cols,
        "periodo_min": periodo_min,
        "periodo_max": periodo_max,
        "nivel_geografico": "nacional",
        "filtro_geografico": None,
    },
    "columnas": columnas_info,
    "llave_natural": [RENAME_MAP.get(c, c.lower()) for c in NATURAL_KEY],
    "columnas_mutables": mutables_confirmadas,
    "catalogos": catalogos,
    "scd2": {
        "estrategia": "row_hash",
        "columnas_hash": mutables_confirmadas,
        "columnas_scd": ["row_hash", "valid_from", "valid_to", "is_current"],
    },
    "notas": notas,
}

REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    json.dump(reporte, f, indent=2, ensure_ascii=False)

print(f"\nReporte guardado en: {REPORT_PATH}")
print(f"  Flujo            : {reporte['flujo']}")
print(f"  Filas            : {total_filas:,}")
print(f"  Columnas         : {total_cols}")
print(f"  Periodo          : {periodo_min} → {periodo_max}")
print(f"  Nivel geográfico : {reporte['resumen']['nivel_geografico']}")
print(f"  Llave natural    : {reporte['llave_natural']}")
print(f"  Columnas mutables: {mutables_confirmadas}")
print(f"  Catálogos        : {[c['nombre_columna'] for c in catalogos]}")
print(f"  Duplicados NK    : {n_dup}")
