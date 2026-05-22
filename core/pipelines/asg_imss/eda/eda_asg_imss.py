"""EDA del pipeline ``asg_imss``.

Analiza las DOS fuentes que componen el flujo:

1. Catálogos (XLSX con múltiples hojas) — diccionario oficial del IMSS.
2. Datos mensuales (CSV separado por ``|``) — Asegurados, Salarios y
   Trabajadores eventuales por delegación/subdelegación, entidad,
   municipio, sector económico, tamaño de patrón, sexo, rango de edad,
   rango salarial y rango UMA.

Ejecutar con::

    conda run -n etl python core/pipelines/asg_imss/eda/eda_asg_imss.py

Restricciones EDA:
- Solo lee los archivos de muestra locales que el DEA aprobó.
- Genera ``core/pipelines/asg_imss/eda/reporte_eda.json``.
- No descarga datos a ``eda/`` ni escribe en ``data/extract``.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
REPO_ROOT = Path("/home/zamax/Documents/Repos/iieg/ETL_SIEEJ")
SAMPLE_CSV = REPO_ROOT / "asg-2026-01-31.csv"
SAMPLE_XLSX = REPO_ROOT / "diccionario_de_datos_1.xlsx"

URL_CATALOGO = "http://datos.imss.gob.mx/sites/default/files/diccionario_de_datos_1.xlsx"
URL_DATOS_TEMPLATE = "http://datos.imss.gob.mx/sites/default/files/asg-YYYY-MM-DD.csv"

REPORT_PATH = REPO_ROOT / "core" / "pipelines" / "asg_imss" / "eda" / "reporte_eda.json"

# Hojas del XLSX: nombre exacto -> alias interno (catálogo destino).
CATALOG_SHEETS: dict[str, str] = {
    "delegación-subdelegación": "cat_delegacion_subdelegacion",
    "entidad-municipio": "cat_entidad_municipio",
    "sector 1": "cat_sector_1",
    "sector 2": "cat_sector_2",
    "sector 4": "cat_sector_4",
    "Tamaño de registro patronal": "cat_tamano_patron",
    "sexo": "cat_sexo",
    "Rango edad": "cat_rango_edad",
    "Rango salario": "cat_rango_salarial",
    "Rango UMA": "cat_rango_uma",
}

# En estos catálogos el valor literal "NA" es un VALOR VÁLIDO, no nulo.
NA_AS_VALID_VALUE = {
    "cat_delegacion_subdelegacion",
    "cat_entidad_municipio",
    "cat_tamano_patron",
    "cat_sexo",
    "cat_rango_edad",
    "cat_rango_salarial",
    "cat_rango_uma",
}

# Columnas del CSV: clasificación esperada según las reglas aprobadas por DEA.
METRICAS_INT = [
    "asegurados",
    "no_trabajadores",
    "ta",
    "teu",
    "tec",
    "tpu",
    "tpc",
    "ta_sal",
    "teu_sal",
    "tec_sal",
    "tpu_sal",
    "tpc_sal",
]
METRICAS_FLOAT = [
    "masa_sal_ta",
    "masa_sal_teu",
    "masa_sal_tec",
    "masa_sal_tpu",
    "masa_sal_tpc",
]
COLUMNAS_CATALOGO_CSV = {
    "cve_delegacion": "cat_delegacion_subdelegacion (par cve_delegacion+cve_subdelegacion)",
    "cve_subdelegacion": "cat_delegacion_subdelegacion (par cve_delegacion+cve_subdelegacion)",
    "cve_entidad": "cat_entidad_municipio (par cve_entidad+cve_municipio)",
    "cve_municipio": "cat_entidad_municipio (par cve_entidad+cve_municipio)",
    "sector_economico_1": "cat_sector_1 (1 char) — derivable de sector_economico_4[:1]",
    "sector_economico_2": "cat_sector_2 (2 chars) — derivable de sector_economico_4[:2]",
    "sector_economico_4": "cat_sector_4 (4 chars)",
    "tamano_patron": "cat_tamano_patron",
    "sexo": "cat_sexo",
    "rango_edad": "cat_rango_edad",
    "rango_salarial": "cat_rango_salarial",
    "rango_uma": "cat_rango_uma",
}

# Columnas reales del CSV. Importante: el archivo publicado por IMSS
# corrompe la 'ñ' de 'tamaño_patron' en algunas publicaciones, dejando
# el byte U+FFFD (REPLACEMENT CHARACTER) en lugar de la letra. Por eso
# se contemplan ambas variantes.
CSV_RENAME = {
    "tamaño_patron": "tamano_patron",
    "tama\ufffdo_patron": "tamano_patron",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def detect_encoding(path: Path) -> str:
    """Detecta utf-8 vs latin1 leyendo bytes crudos."""
    raw = path.read_bytes()
    try:
        raw.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        return "latin1"


def safe_sample(values, k: int = 10):
    out = []
    for v in values:
        if pd.isna(v):
            out.append(None)
        else:
            out.append(str(v))
        if len(out) >= k:
            break
    return out


# ---------------------------------------------------------------------------
# 1. Análisis del XLSX (catálogos)
# ---------------------------------------------------------------------------
print("=" * 72)
print("1. Análisis de catálogos (XLSX)")
print("=" * 72)
print(f"   Archivo : {SAMPLE_XLSX}")

xlsx = pd.ExcelFile(SAMPLE_XLSX)
print(f"   Hojas detectadas ({len(xlsx.sheet_names)}): {xlsx.sheet_names}")

catalogos_info: list[dict] = []
for hoja, alias in CATALOG_SHEETS.items():
    if hoja not in xlsx.sheet_names:
        print(f"   [WARN] Hoja faltante: {hoja!r}")
        continue

    # Headers reales empiezan en la fila 2 (skiprows=1, 0-indexed).
    df_cat = pd.read_excel(
        SAMPLE_XLSX,
        sheet_name=hoja,
        skiprows=1,
        dtype=str,
        keep_default_na=False,  # Conservar literal "NA"
        na_values=[],  # Nada se interpreta como NaN
    )
    df_cat = df_cat.dropna(how="all").reset_index(drop=True)
    # Quitar columnas totalmente vacías que aparecen por el formato del XLSX.
    df_cat = df_cat.loc[:, [c for c in df_cat.columns if not str(c).startswith("Unnamed")]]

    cols = list(df_cat.columns)
    n_filas = len(df_cat)

    # Detectar literal "NA" en cualquier celda.
    contiene_na_literal = bool((df_cat.astype(str).map(lambda x: x.strip() == "NA")).any().any())

    columnas_detalle = []
    for col in cols:
        serie = df_cat[col].astype(str).str.strip()
        valores = serie.unique().tolist()
        columnas_detalle.append(
            {
                "nombre": str(col),
                "valores_unicos": int(serie.nunique()),
                "muestra": safe_sample(valores, 8),
            }
        )

    catalogos_info.append(
        {
            "hoja_xlsx": hoja,
            "tabla_destino": alias,
            "filas": int(n_filas),
            "columnas": [str(c) for c in cols],
            "columnas_detalle": columnas_detalle,
            "na_literal_es_valor_valido": alias in NA_AS_VALID_VALUE,
            "contiene_na_literal_en_muestra": contiene_na_literal,
        }
    )

    print(f"   - {hoja!r:<40} → {alias:<32} filas={n_filas:<4} cols={cols}  NA-literal={contiene_na_literal}")


# ---------------------------------------------------------------------------
# 2. Análisis del CSV (datos)
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("2. Análisis de datos (CSV mensual)")
print("=" * 72)
print(f"   Archivo : {SAMPLE_CSV}")

encoding_csv = detect_encoding(SAMPLE_CSV)
print(f"   Encoding detectado: {encoding_csv}")

# Leer SIN interpretar nulos para detectar el literal "NA" tal cual viene.
df_raw = pd.read_csv(
    SAMPLE_CSV,
    sep="|",
    encoding=encoding_csv,
    dtype=str,
    keep_default_na=False,
    na_values=[],
)
print(f"   Filas (con keep_default_na=False): {len(df_raw):,}")
print(f"   Columnas: {list(df_raw.columns)}")

# Filas totalmente vacías (todas las columnas son string vacío "").
filas_vacias_mask = (df_raw.apply(lambda s: s.str.strip() == "") | df_raw.isna()).all(axis=1)
n_filas_vacias = int(filas_vacias_mask.sum())
print(f"   Filas completamente vacías: {n_filas_vacias}")

# Aplicar rename (tamaño_patron -> tamano_patron).
df_raw = df_raw.rename(columns=CSV_RENAME)

# Versión "limpia" para conteo de duplicados y análisis: drop filas vacías y trim.
df_clean = df_raw.loc[~filas_vacias_mask].copy()
for col in df_clean.columns:
    df_clean[col] = df_clean[col].astype(str).str.strip()

# Duplicados exactos sobre todas las columnas.
dup_mask = df_clean.duplicated(keep=False)
n_dup_total = int(dup_mask.sum())
n_dup_extra = int(df_clean.duplicated(keep="first").sum())
print(f"   Filas duplicadas (todas las apariciones): {n_dup_total}")
print(f"   Filas duplicadas a eliminar (extras):     {n_dup_extra}")

# Filtro Jalisco (cve_entidad = 14) — solo informativo para el sample.
if "cve_entidad" in df_clean.columns:
    n_jalisco = int((df_clean["cve_entidad"] == "14").sum())
    print(f"   Filas con cve_entidad=14 (Jalisco) en sample: {n_jalisco}")
else:
    n_jalisco = 0

# Para análisis de nulabilidad: en el CSV el vacío "" es NULL real para sectores.
# En las demás columnas catálogo, "" no debería aparecer (validar).
# Para métricas, convertir a numérico.
total_filas = len(df_clean)

# ---------------------------------------------------------------------------
# 2b. Análisis columna a columna
# ---------------------------------------------------------------------------
print()
print("   Detalle por columna:")
columnas_info: list[dict] = []

for col in df_clean.columns:
    serie_str = df_clean[col]
    es_vacio = serie_str == ""
    n_vacios = int(es_vacio.sum())
    pct_vacios = round(n_vacios / total_filas * 100, 4) if total_filas else 0.0
    n_literal_na = int((serie_str == "NA").sum())
    valores_unicos = int(serie_str.nunique())
    muestra = safe_sample(serie_str[~es_vacio].unique().tolist(), 8)

    # Clasificación
    if col in METRICAS_INT:
        rol = "metrica_int"
        tipo_homologado = "INTEGER"
    elif col in METRICAS_FLOAT:
        rol = "metrica_float"
        tipo_homologado = "NUMERIC(18,2)"
    elif col in COLUMNAS_CATALOGO_CSV:
        rol = "catalogo_fk"
        tipo_homologado = "VARCHAR"
    else:
        rol = "otro"
        tipo_homologado = "VARCHAR"

    # Para métricas: revisar dtype real (int vs float) y rango.
    metrica_stats = None
    if rol in {"metrica_int", "metrica_float"}:
        # Convertir respetando "" como NaN para los stats.
        num = pd.to_numeric(serie_str.replace("", pd.NA), errors="coerce")
        n_no_enteros = 0
        if rol == "metrica_int":
            # Detectar si algún valor tiene parte decimal != 0.
            non_null = num.dropna()
            if len(non_null):
                n_no_enteros = int((non_null != non_null.astype("int64", errors="ignore")).sum())
                # Más robusto: parte fraccionaria.
                n_no_enteros = int(((non_null - non_null.round()).abs() > 1e-9).sum())
        metrica_stats = {
            "min": None if num.dropna().empty else float(num.min()),
            "max": None if num.dropna().empty else float(num.max()),
            "media": None if num.dropna().empty else float(num.mean()),
            "no_enteros": n_no_enteros if rol == "metrica_int" else None,
        }

    # Para sectores: confirmar largo esperado.
    largo_observado = None
    if col in {"sector_economico_1", "sector_economico_2", "sector_economico_4"}:
        no_vacios = serie_str[~es_vacio]
        if not no_vacios.empty:
            largos = no_vacios.str.len().unique().tolist()
            largo_observado = sorted(int(x) for x in largos)

    info = {
        "nombre_original": col,
        "rol": rol,
        "tipo_pandas_lectura": "object",  # se leyó como str
        "tipo_homologado_propuesto": tipo_homologado,
        "vacios_count": n_vacios,
        "vacios_pct": pct_vacios,
        "literal_NA_count": n_literal_na,
        "valores_unicos": valores_unicos,
        "muestra_valores": muestra,
        "catalogo_referenciado": COLUMNAS_CATALOGO_CSV.get(col),
        "metrica_stats": metrica_stats,
        "largo_observado": largo_observado,
    }
    columnas_info.append(info)

    print(
        f"     {col:<22} vac={n_vacios:<4} ({pct_vacios:5.2f}%)  "
        f"NA-lit={n_literal_na:<4} card={valores_unicos:<4} rol={rol}"
        + (f" largos={largo_observado}" if largo_observado else "")
    )


# ---------------------------------------------------------------------------
# 3. Reglas y hallazgos críticos
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("3. Hallazgos críticos")
print("=" * 72)

hallazgos: list[str] = []

# 3.1 Sectores: nulables, longitud fija.
sec_cols = ["sector_economico_1", "sector_economico_2", "sector_economico_4"]
for sc in sec_cols:
    if sc in df_clean.columns:
        info = next(c for c in columnas_info if c["nombre_original"] == sc)
        hallazgos.append(
            f"{sc}: {info['vacios_count']} vacíos en sample "
            f"({info['vacios_pct']}%) → NULL real permitido; largo(s) observado(s) "
            f"{info['largo_observado']}."
        )

# 3.2 NA literal en catálogos.
cols_con_na_literal = [c["nombre_original"] for c in columnas_info if c["literal_NA_count"] > 0]
if cols_con_na_literal:
    hallazgos.append(
        "El literal 'NA' aparece como VALOR VÁLIDO en columnas catálogo del CSV: "
        f"{cols_con_na_literal}. NO debe parsearse como NULL al leer el CSV."
    )

# 3.3 Hojas XLSX con NA literal.
cat_con_na = [c["tabla_destino"] for c in catalogos_info if c["contiene_na_literal_en_muestra"]]
if cat_con_na:
    hallazgos.append(f"Catálogos XLSX que contienen literal 'NA' como valor: {cat_con_na}.")

# 3.4 Duplicados y filas vacías.
hallazgos.append(
    f"Sample contiene {n_filas_vacias} filas completamente vacías y "
    f"{n_dup_extra} duplicados exactos extra (transform debe dedup + drop empty)."
)

# 3.5 Encoding.
hallazgos.append(
    f"Encoding del CSV de muestra: {encoding_csv}. El extractor debe intentar "
    "utf-8 primero y fallback a latin1, ya que IMSS publica con codificaciones inconsistentes."
)

# 3.6 dtype real de métricas int.
metricas_int_no_enteros = [
    c["nombre_original"]
    for c in columnas_info
    if c["rol"] == "metrica_int" and c["metrica_stats"] and c["metrica_stats"].get("no_enteros")
]
if metricas_int_no_enteros:
    hallazgos.append(
        "Las siguientes métricas marcadas como INTEGER tienen valores decimales en sample: "
        f"{metricas_int_no_enteros} → revisar con DEA si deben ser NUMERIC."
    )
else:
    hallazgos.append(f"Métricas {METRICAS_INT}: todos los valores en sample son enteros → INTEGER OK.")

# 3.7 Sectores jerárquicos
hallazgos.append(
    "sector_economico_4 ('XYZZ') contiene la jerarquía completa. sector_economico_1 y "
    "sector_economico_2 son derivables (slicing) y deben validarse contra cat_sector_1 / cat_sector_2."
)

# 3.8 Geografía
hallazgos.append(
    "Geografía: cve_entidad+cve_municipio NO corresponden a INEGI/CVEGEO. Son códigos "
    "internos del IMSS — ver cat_entidad_municipio."
)

for h in hallazgos:
    print(f"   - {h}")

# ---------------------------------------------------------------------------
# 3b. Ambigüedades reales (NO inventar reglas, devolver al DEA)
# ---------------------------------------------------------------------------
ambiguedades: list[str] = []

# A.1 Longitud de sectores observada vs regla declarada por DEA.
largos_observados = {
    sc: next(c["largo_observado"] for c in columnas_info if c["nombre_original"] == sc)
    for sc in sec_cols
    if sc in df_clean.columns
}
largos_esperados = {
    "sector_economico_1": [1],
    "sector_economico_2": [2],
    "sector_economico_4": [4],
}
discrepancia_sectores = {
    k: {"esperado": largos_esperados[k], "observado": v}
    for k, v in largos_observados.items()
    if v is not None and v != largos_esperados[k]
}
if discrepancia_sectores:
    ambiguedades.append(
        "Longitud de sectores en el CSV de muestra NO coincide con la regla declarada "
        f"por DEA ({largos_esperados}). Observado: {discrepancia_sectores}. "
        "Hipótesis: la fuente puede estar publicando los códigos sin padding de ceros "
        "a la izquierda. Confirmar con DEA si se debe rellenar con ceros o si la regla "
        "de longitudes (1/2/4) debe ajustarse."
    )

# A.2 Mojibake de 'tamaño_patron'.
cols_csv_originales = list(pd.read_csv(SAMPLE_CSV, sep="|", encoding=encoding_csv, dtype=str, nrows=0).columns)
tiene_replacement = any("\ufffd" in c for c in cols_csv_originales)
if tiene_replacement:
    ambiguedades.append(
        "El header del CSV de muestra contiene el byte U+FFFD (REPLACEMENT CHARACTER) "
        "en la columna 'tamaño_patron' — la fuente parece estar corrompida en origen. "
        "El extractor debe normalizar el header (renombrar a 'tamano_patron') con "
        "tolerancia tanto a 'ñ' válida como al U+FFFD."
    )

# A.3 Sample muy chico.
ambiguedades.append(
    "El sample tiene solo ~300 filas y no contiene duplicados ni filas vacías. "
    "La regla de dedup/drop-empty proviene de DEA, no se observó en este sample."
)

for a in ambiguedades:
    print(f"   [AMBIG] {a}")


# ---------------------------------------------------------------------------
# 4. Reporte JSON
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("4. Generando reporte_eda.json")
print("=" * 72)

reporte: dict = {
    "flujo": "asg_imss",
    "fecha_analisis": str(date.today()),
    "fuentes": [
        {
            "id": "catalogos",
            "descripcion": ("Diccionario oficial IMSS con catálogos por hoja. Headers reales en fila 2 (skiprows=1)."),
            "url": URL_CATALOGO,
            "formato": "xlsx",
            "num_archivos": 1,
            "hojas": list(CATALOG_SHEETS.keys()),
            "periodicidad": "ocasional (actualización del diccionario)",
        },
        {
            "id": "datos",
            "descripcion": (
                "Asegurados, Salarios y Trabajadores eventuales — archivo mensual. "
                "Separador '|'; encoding utf-8/latin1 según publicación."
            ),
            "url_template": URL_DATOS_TEMPLATE,
            "ejemplo_archivo": SAMPLE_CSV.name,
            "formato": "csv",
            "separador": "|",
            "encoding_detectado_sample": encoding_csv,
            "periodicidad": "mensual",
            "filtro_obligatorio": {"cve_entidad": "14"},
            "estrategia_update": "append-only (solo-inserciones)",
        },
    ],
    "catalogos": catalogos_info,
    "dataset_principal": {
        "tabla_objetivo_stg": "stg_asg_imss",
        "dimensiones_sample": {
            "filas_total": int(len(df_raw)),
            "filas_vacias": n_filas_vacias,
            "filas_duplicadas_extra": n_dup_extra,
            "filas_utiles": int(total_filas - n_dup_extra),
            "filas_jalisco_sample": n_jalisco,
            "columnas": int(len(df_raw.columns)),
        },
        "columnas": columnas_info,
        "llave_natural_candidata": [
            "cve_delegacion",
            "cve_subdelegacion",
            "cve_entidad",
            "cve_municipio",
            "sector_economico_4",
            "tamano_patron",
            "sexo",
            "rango_edad",
            "rango_salarial",
            "rango_uma",
            # Periodo no viene en el CSV: lo aporta el nombre del archivo.
            "periodo (derivado de YYYY-MM-DD del nombre del archivo)",
        ],
        "metricas_enteras": METRICAS_INT,
        "metricas_float": METRICAS_FLOAT,
        "columnas_nulables": sec_cols,
        "renames_aplicados": CSV_RENAME,
    },
    "geografia": {
        "nivel": "municipal_imss",
        "columnas_geo": ["cve_entidad", "cve_municipio"],
        "compatible_inegi": False,
        "nota": (
            "El catálogo entidad-municipio es propio del IMSS y no coincide con "
            "CVE_ENT/CVE_MUN INEGI. No usar la tabla cvegeo para FK."
        ),
    },
    "reglas_negocio": {
        "na_literal_es_valor_valido_en_catalogos": sorted(NA_AS_VALID_VALUE),
        "na_literal_no_aplica_en": [
            "cat_sector_1",
            "cat_sector_2",
            "cat_sector_4",
        ],
        "columnas_con_null_real": sec_cols,
        "jerarquia_sectores": {
            "sector_1": "1 char",
            "sector_2": "2 chars (prefijo de sector_4)",
            "sector_4": "4 chars (valor en el CSV)",
            "derivacion": "sector_1 = sector_4[:1]; sector_2 = sector_4[:2]",
        },
        "jerarquia_delegacion": "cat_delegacion_subdelegacion: par (cve_delegacion, cve_subdelegacion)",
        "jerarquia_entidad_municipio": "cat_entidad_municipio: par (cve_entidad, cve_municipio)",
        "dedup_transform": "drop filas completamente vacías; drop duplicados exactos",
        "filtro_extract": "cve_entidad == '14' (Jalisco)",
    },
    "hallazgos_criticos": hallazgos,
    "ambiguedades_para_dea": ambiguedades,
    "notas": (
        "EDA basado en archivos de muestra locales aprobados por DEA "
        "(asg-2026-01-31.csv ~300 filas y diccionario_de_datos_1.xlsx). "
        "Los conteos numéricos (filas, duplicados, vacíos) corresponden al "
        "sample y NO a la publicación completa."
    ),
}

REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    json.dump(reporte, f, indent=2, ensure_ascii=False, default=str)

print(f"   Reporte guardado en: {REPORT_PATH}")
print(f"   Catálogos          : {[c['tabla_destino'] for c in catalogos_info]}")
print(f"   Columnas dataset   : {len(columnas_info)}")
print(f"   Hallazgos          : {len(hallazgos)}")
