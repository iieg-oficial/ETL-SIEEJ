from typing import Final, List

RENAME_HEADER: Final[dict] = {
    "id": "id",
    "nom_estab": "nombre_establecimiento",
    "raz_social": "razon_social",
    "codigo_act": "actividad_economica_id",
    "nombre_act": "nombre_actividad_economica",
    "per_ocu": "per_ocu",
    "tipoUniEco": "tipo_uni_eco",
    "latitud": "latitud",
    "longitud": "longitud",
    "fecha_alta": "fecha_alta",
    "nomb_asent": "nombre_asentamiento",
    "ageb": "ageb",
    "cve_mun": "cve_mun",
    "municipio": "municipio",
    "cve_loc": "clave_localidad",
    "localidad": "localidad",
}

NULL_VALUES: Final[List[str]] = ["", "N/A", "NA", "n/a", "na", "null", "NULL", " "]

TITLE_COLS: Final[List[str]] = [
    "nombre_establecimiento",
    "razon_social",
    "nombre_asentamiento",
    "municipio",
    "localidad",
    "nombre_actividad_economica",
]

DATE_COLS: Final[List[str]] = ["fecha_alta"]

ENTIDADES_MEXICO: Final[List[int]] = list(range(1, 33))
