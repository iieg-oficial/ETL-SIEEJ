from typing import Final, List

RENAME_HEADER: Final[dict] = {
    "clee": "clee",
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
    "tipo_vial": "tipo_vial",
    "nom_vial": "nom_vial",
    "numero_ext": "numero_ext",
    "cod_postal": "cod_postal",
    "telefono": "telefono",
    "www": "contacto_web",
    "cve_mun": "cve_mun",
    "municipio": "municipio",
    "cve_loc": "localidad_id",
    "localidad": "localidad",
}

# Keys are source CSV column names. An unknown key is a silent no-op and pandas
# infers the type, dropping leading zeros.
DTYPE_OVERRIDES: Final[dict] = {
    "numero_int": str,
    "numero_ext": str,
    "cod_postal": str,
    "telefono": str,
    "www": str,
}

NULL_VALUES: Final[List[str]] = ["", "N/A", "NA", "n/a", "na", "null", "NULL", " "]

TITLE_COLS: Final[List[str]] = [
    "nombre_establecimiento",
    "razon_social",
    "nombre_asentamiento",
    "municipio",
    "localidad",
    "tipo_vial",
    "nom_vial",
]

DATE_COLS: Final[List[str]] = ["fecha_alta"]

ENTIDADES_MEXICO: Final[List[int]] = list(range(1, 33))

ENTIDAD_JALISCO: Final[int] = 14

RAW_COLS: Final[List[str]] = [
    "clee",
    "id",
    "nombre_establecimiento",
    "razon_social",
    "latitud",
    "longitud",
    "fecha_alta",
    "nombre_asentamiento",
    "ageb",
    "tipo_vial",
    "nom_vial",
    "numero_ext",
    "cod_postal",
    "telefono",
    "contacto_web",
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

ENTIDADES = list(range(1, 33))
