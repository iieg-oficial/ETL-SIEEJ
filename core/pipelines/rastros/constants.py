import re
from typing import Literal

from core.pipelines.rastros.attributes import RastrosTables as T

DATASET_MEMBER_PATTERN = re.compile(r"conjunto_de_datos/esgrm_mensual_tr_cifra_(\d{4})\.csv$")
SOURCE_ENCODING: str = "latin-1"

# Firma de un archivo ZIP. INEGI responde 200 con HTML cuando la ruta no existe,
# así que el status code no sirve para detectar una URL inválida.
ZIP_MAGIC: Literal[b"PK"] = b"PK"

RENAME_HEADER: dict[str, str] = {
    "ANIO": "anio",
    "ID_MES": "mes",
    "CVEGEO": "entidad_id",
    "ESPECIE_GANADERA": "especie_ganadera",
    "NUMERO_CABEZAS": "numero_cabezas",
    "ESTATUS_DATO_CBZ": "estatus_cabeza",
    "PRODUCCION_CARNE": "produccion_carne",
    "ESTATUS_DATO_PROD": "estatus_produccion",
    "VALOR_PRODUCCION": "vproduccion",
    "ESTATUS_DATO_VPROD": "estatus_vproduccion",
    "ESTATUS": "tipo_cifra",
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
    "numero_cabezas",
    "produccion_carne",
    "vproduccion",
]

ESTATUS_COLS: list[str] = [
    "estatus_cabeza",
    "estatus_produccion",
    "estatus_vproduccion",
]

CATALOG_TEXT_COLS: dict[T, str] = {
    T.CAT_ESTATUS: "estatus",
    T.CAT_ESPECIES_GANADERAS: "especie_ganadera",
    T.CAT_TIPO_CIFRA: "tipo_cifra",
}

CATALOG_FK_RESOLUTION = {
    "especie_ganadera": (T.CAT_ESPECIES_GANADERAS, "especie_ganadera_id"),
    "tipo_cifra": (T.CAT_TIPO_CIFRA, "tipo_cifra_id"),
    "estatus_cabeza": (T.CAT_ESTATUS, "estatus_cabeza_id"),
    "estatus_produccion": (T.CAT_ESTATUS, "estatus_produccion_id"),
    "estatus_vproduccion": (T.CAT_ESTATUS, "estatus_vproduccion_id"),
}

CONFLICT_KEYS = ["fecha", "entidad_id", "especie_ganadera_id"]
