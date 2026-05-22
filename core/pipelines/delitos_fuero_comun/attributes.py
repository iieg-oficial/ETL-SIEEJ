from enum import auto, StrEnum


class DelitosFueroComunTables(StrEnum):
    CAT_BIEN_JURIDICO_AFECTADO = auto()
    CAT_TIPO_DELITO = auto()
    CAT_SUBTIPO_DELITO = auto()
    CAT_MODALIDAD = auto()
    STG_DELITOS_FUERO_COMUN_2015_2025 = auto()
    STG_DELITOS_FUERO_COMUN_2026 = auto()


# Column definitions for both staging tables (post-transform, pre-load).
# dtype follows pandas nullable-integer convention (Int16/Int32 for nullable ints).
COLUMNS_STG: dict[str, dict[str, object]] = {
    "anio": {"dtype": "Int16", "nullable": False},
    "cvegeo": {"dtype": "Int32", "nullable": False},
    "bien_juridico_afectado_id": {"dtype": "Int32", "nullable": False},
    "tipo_delito_id": {"dtype": "Int32", "nullable": False},
    "subtipo_delito_id": {"dtype": "Int32", "nullable": False},
    "modalidad_id": {"dtype": "Int32", "nullable": False},
    "enero": {"dtype": "Int32", "nullable": True},
    "febrero": {"dtype": "Int32", "nullable": True},
    "marzo": {"dtype": "Int32", "nullable": True},
    "abril": {"dtype": "Int32", "nullable": True},
    "mayo": {"dtype": "Int32", "nullable": True},
    "junio": {"dtype": "Int32", "nullable": True},
    "julio": {"dtype": "Int32", "nullable": True},
    "agosto": {"dtype": "Int32", "nullable": True},
    "septiembre": {"dtype": "Int32", "nullable": True},
    "octubre": {"dtype": "Int32", "nullable": True},
    "noviembre": {"dtype": "Int32", "nullable": True},
    "diciembre": {"dtype": "Int32", "nullable": True},
}
