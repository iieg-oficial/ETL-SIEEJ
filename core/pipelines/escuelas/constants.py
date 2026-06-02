from typing import Final

PIPELINE_NAME: Final[str] = "escuelas"

DIRECTORIO_DATASET: Final[str] = "directorio"
ESTADISTICA_DATASET: Final[str] = "estadistica"

ENTIDAD_ID_JALISCO: Final[int] = 14
DEFAULT_SOURCE_YEAR: Final[int] = 2026

DIRECTORIO_COLUMN_RENAMES: Final[dict[str, str]] = {
    "turno": "turno_id",
    "localidad": "localidad_id",
    "colonia": "colonia_id",
    "municipio": "municipio_id",
    "sostenimiento": "codigo_sostenimiento_id",
    "nombre_sostenimiento": "sostenimiento",
    "region": "region_id",
}

DIRECTORIO_COLUMNS: Final[list[str]] = [
    "clave_ct",
    "turno_id",
    "nombre_turno",
    "nombre_ct",
    "domicilio",
    "localidad_id",
    "nombre_localidad",
    "colonia_id",
    "nombre_colonia",
    "municipio_id",
    "nombre_municipio",
    "medio",
    "director",
    "codigo_postal",
    "telefono",
    "zona_escolar",
    "sector",
    "codigo_sostenimiento_id",
    "sostenimiento",
    "nivel",
    "programa",
    "region_id",
    "nombre_region",
    "longitud",
    "latitud",
    "escuelas",
    "hombres_matriculados",
    "mujeres_matriculadas",
    "total_matriculados",
    "total_docentes_directivo",
]

ESTADISTICA_COLUMNS: Final[list[str]] = ["nivel_programa", "sostenimiento", "escuelas", "matricula", "docentes"]

CATALOG_VALUE_COLUMNS: Final[list[str]] = [
    "nombre_turno",
    "sostenimiento",
    "nivel",
    "programa",
    "nombre_region",
    "medio",
    "nivel_programa",
]

OPTIONAL_ZERO_TO_NULL_COLUMNS: Final[list[str]] = [
    "telefono",
    "codigo_postal",
    "colonia_id",
    "nombre_colonia",
    "sector",
]

DIRECTORIO_NUMERIC_COLUMNS: Final[list[str]] = [
    "turno_id",
    "localidad_id",
    "colonia_id",
    "municipio_id",
    "zona_escolar",
    "sector",
    "codigo_sostenimiento_id",
    "region_id",
    "escuelas",
    "hombres_matriculados",
    "mujeres_matriculadas",
    "total_matriculados",
    "total_docentes_directivo",
]

DIRECTORIO_FLOAT_COLUMNS: Final[list[str]] = ["longitud", "latitud"]
ESTADISTICA_NUMERIC_COLUMNS: Final[list[str]] = ["escuelas", "matricula", "docentes"]

NULL_VALUES: Final[list[str]] = ["NA", "N/A", "null", "nan", ""]
