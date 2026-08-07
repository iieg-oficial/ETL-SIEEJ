import re
from typing import Literal


DATASET_MEMBER_PATTERN = re.compile(r"tr_variable_total_entidad_mensual_2018_(\d{4})\.csv$")
CATALOG_MEMBER_PATTERN = re.compile(r"tc_actividad\.csv$")
DATASET_DESCRIPTION = "tr_variable_total_entidad_mensual"
CATALOG_DESCRIPTION = "tc_actividad"

SOURCE_ENCODING: str = "utf-8"
ZIP_MAGIC: Literal[b"PK"] = b"PK"

RENAME_HEADER: dict[str, str] = {
    "CODIGO_ACTIVIDAD": "codigo_actividad",
    "CODIGO_ENTIDAD": "entidad_id",
    "ANIO": "anio",
    "MES": "mes",
    "H001A": "per_ocu_tot",
    "H001D": "horas_trabajadas",
    "J000A": "remuneraciones",
    "O101A": "valor_produccion",
    "M312A": "valor_ventas",
    "ESTATUS": "estatus",
}

CATALOG_RENAME_HEADER: dict[str, str] = {
    "CODIGO_ACTIVIDAD": "codigo_actividad",
    "DESCRIPCION": "descripcion",
}

NULL_VALUES: list[str] = [
    "null",
    "nan",
    "-",
    "--",
    "---",
    "*",
    "s/d",
    "sin dato",
]

INT_COLS: list[str] = [
    "per_ocu_tot",
    "remuneraciones",
    "valor_produccion",
    "valor_ventas",
]

FLOAT_COLS: list[str] = [
    "horas_trabajadas",
]

CONFLICT_KEYS: list[str] = ["fecha", "entidad_id", "codigo_actividad"]
