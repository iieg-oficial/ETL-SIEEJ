from enum import StrEnum, auto


class EtefTables(StrEnum):
    STG_ETEF_CAT_CODIGO_SCIAN = auto()  # "stg_etef_cat_codigo_scian"
    STG_ETEF_DATOS = auto()  # "stg_etef_datos"


# Columnas cuyo cambio dispara una nueva versión SCD2 (entran en el row_hash)
MUTABLE_COLUMNS: list[str] = ["val_usd", "estatus_cifra", "estatus"]

# Alias — mismas columnas que MUTABLE_COLUMNS por convención del pipeline
HASH_COLUMNS: list[str] = MUTABLE_COLUMNS

# Llave natural en nombres de columna de BD (post-resolución FK)
NATURAL_KEY_COLUMNS: list[str] = ["anio", "trimestre", "cve_ent", "codigo_scian_id"]
