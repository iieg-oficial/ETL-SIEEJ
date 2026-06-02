from typing import Final, List

RENAME_HEADER: Final[dict] = {
    "id": "id",
    "nom_estab": "nombre_establecimiento",
    "raz_social": "razon_social",
    "codigo_act": "codigo_actividad",
    "per_ocu": "per_ocu",
    "tipoUniEco": "tipo_uni_eco",
    "latitud": "latitud",
    "longitud": "longitud",
    "fecha_alta": "fecha_alta",
    "nomb_asent": "nombre_asentamiento",
    "ageb": "ageb",
    "cve_mun": "cve_mun",
    "municipio": "municipio",
    "cve_loc": "localidad_id",
    "localidad": "localidad",
}

NULL_VALUES: Final[List[str]] = ["", "N/A", "NA", "n/a", "na", "null", "NULL", " "]

TITLE_COLS: Final[List[str]] = [
    "nombre_establecimiento",
    "razon_social",
    "nombre_asentamiento",
    "municipio",
    "localidad",
]

DATE_COLS: Final[List[str]] = ["fecha_alta"]

ENTIDADES_MEXICO: Final[List[int]] = list(range(1, 33))

RAW_COLS: Final[List[str]] = [
    "id",
    "nombre_establecimiento",
    "razon_social",
    "latitud",
    "longitud",
    "fecha_alta",
    "nombre_asentamiento",
    "ageb",
    "codigo_actividad",
    "entidad_id",
    "cve_mun",
    "localidad_id",
    "fecha_actualizacion",
    "rango_personal_id",
    "tipo_establecimiento_id",
]

INT_COLS: Final[set] = {
    "id",
    "entidad_id",
    "cve_mun",
    "localidad_id",
    "rango_personal_id",
    "tipo_establecimiento_id",
}
