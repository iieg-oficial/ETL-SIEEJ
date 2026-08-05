import re
from typing import Literal

DATASET_MEMBER_PATTERN = re.compile(r"tr_emec_entidad_federativa_indice_2008_(\d{4})\.csv$")
CATALOG_MEMBER_PATTERN = re.compile(r"tc_actividad\.csv$")
SOURCE_ENCODING: str = "utf-8"

# Firma de un archivo ZIP. INEGI responde 200 con HTML cuando la ruta no existe,
# así que el status code no sirve para detectar una URL inválida.
ZIP_MAGIC: Literal[b"PK"] = b"PK"

RENAME_HEADER: dict[str, str] = {
    "CODIGO_ACTIVIDAD": "codigo_actividad",
    "ANIO": "anio",
    "MES": "mes",
    "ENTIDAD": "entidad",
    "H000W_I000W": "per_ocu_tot",
    "J000W": "remuneraciones_tot",
    "REMUNERACION_MEDIA": "remuneraciones_media",
    "M000W": "ind_ingresos_bienes_serv",
    "K100W": "ind_compras_reventa",
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
    "per_ocu_tot",
    "remuneraciones_tot",
    "remuneraciones_media",
    "ind_ingresos_bienes_serv",
    "ind_compras_reventa",
]

CONFLICT_KEYS: list[str] = ["fecha", "entidad_id", "codigo_actividad"]
CVEGEO_STATES_TABLE: str = "cvegeo_states"
CVEGEO_STATES_NAME_COL: str = "nom_ent"
CVEGEO_STATES_KEY_COL: str = "cve_ent"
