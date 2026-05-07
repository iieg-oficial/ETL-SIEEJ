PIPELINE_NAME = "etef"

# Strings que representan nulos en la fuente
NULL_VALUES: list[str] = ["NO APLICA", "NA", "N/A", "null", "nan", ""]

# Mapa de columnas originales → nombres internos (snake_case)
COLUMN_RENAME_MAP: dict[str, str] = {
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

# Columnas de fecha (se parsean en transform)
DATE_COLUMNS: list[str] = []

# Columnas de catálogo dinámico (se sincronizan en load)
CATALOG_COLUMNS: list[str] = ["codigo_scian"]

# Campos para el natural key: (ANIO, TRIMESTRE, CVE_ENT, CODIGO_SCIAN)
NATURAL_KEY_COLUMNS: list[str] = ["anio", "trimestre", "cve_ent", "codigo_scian"]
