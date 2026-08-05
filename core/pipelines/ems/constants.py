import re
from typing import Literal

DATASET_MEMBER_PATTERN = re.compile(r"tr_ems_entidad_federativa_indice_2013_(\d{4})\.csv$")
CATALOG_MEMBER_PATTERN = re.compile(r"tc_actividad\.csv$")


SOURCE_ENCODING: str = "utf-8"

# Firma de un archivo ZIP. INEGI responde 200 con HTML cuando la ruta no existe,
# así que el status code no sirve para detectar una URL inválida.
ZIP_MAGIC: Literal[b"PK"] = b"PK"

RENAME_HEADER: dict[str, str] = {
    "CODIGO_ACTIVIDAD": "codigo_actividad",
    "CVEGEO": "entidad_id",
    "ANIO": "anio",
    "MES": "mes",
    "M000": "ind_ingresos_bienes_serv",
    "K000": "ind_gastos_consumo",
    "H000A": "per_ocu_tot",
    "H000": "per_ocu_dependiente",
    "I000A": "per_ocu_no_dependiente",
    "J000": "remuneraciones_tot",
    "ESTATUS": "estatus",
}

CATALOG_RENAME_HEADER: dict[str, str] = {
    "CODIGO_ACTIVIDAD": "codigo_actividad",
    "DESCRIPCION_ACTIVIDAD": "descripcion",
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

FLOAT_COLS: list[str] = [
    "ind_ingresos_bienes_serv",
    "ind_gastos_consumo",
    "per_ocu_tot",
    "per_ocu_dependiente",
    "per_ocu_no_dependiente",
    "remuneraciones_tot",
]

CONFLICT_KEYS: list[str] = ["fecha", "entidad_id", "codigo_actividad"]
