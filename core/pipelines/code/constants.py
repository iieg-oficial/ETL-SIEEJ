from typing import Final

PIPELINE_NAME: Final[str] = "code"

VIEW_RETO_GEO: Final[str] = "vm_reto_code_geo"
VIEW_ACADEMIAS_GEO: Final[str] = "vm_academias_deportivas_geo"
VIEW_POLIDEPORTIVOS_GEO: Final[str] = "vm_polideportivos_geo"

# CODE attached its data in the methodology field of the form, not in the data one.
UPLOAD_FIELD: Final[str] = "adjunte_el_documento_metodologico_asociado_al_conjunto_de_datos"

# Academias and Polideportivos came in the data field of the form.
DATA_FIELD: Final[str] = "carga_de_datos"

MANIFEST_FILENAME: Final[str] = "manifest.json"

# Catalogs travel through disk so load can be retried as its own Airflow task.
CATALOGS_FILENAME: Final[str] = "catalogs.pkl"

# The zip also ships a gpkg that duplicates the sheet; the xlsx is the source.
XLSX_GLOB: Final[str] = "*.xlsx"
EXTRACT_DIRNAME: Final[str] = "reto"

GPKG_GLOB: Final[str] = "*.gpkg"
CSV_GLOB: Final[str] = "*.csv"

# Raw frames of the gpkg datasets. Catalog CSVs are told apart by their header,
# since file names change between uploads.
FRAME_DATOS: Final[str] = "datos"
FRAME_CAT_DEPORTE: Final[str] = "cat_deporte"
FRAME_CAT_TIPO: Final[str] = "cat_tipo"
CATALOG_HEADERS: Final[dict[str, frozenset[str]]] = {
    FRAME_CAT_DEPORTE: frozenset({"deporte", "id"}),
    FRAME_CAT_TIPO: frozenset({"tipo", "id"}),
}

SHEET_PUNTOS: Final[str] = "base"
SHEET_ACTIVIDADES: Final[str] = "cat_actividad"
PUNTOS_FRAME: Final[str] = "puntos"

NULL_VALUES: Final[list[str]] = ["NA", "N/A", "null", "nan", ""]

PUNTOS_RENAMES: Final[dict[str, str]] = {
    "fecha": "fecha_corte",
    "id": "clave_punto",
    "clave_agem": "municipio_id",
    "espacio": "nombre_espacio",
    "dias_y_horarios": "dias_horarios",
    "cat_actividad": "actividad_id",
    "cantidad_de_usuarios": "cantidad_usuarios",
    "y": "latitud",
    "x": "longitud",
}

# `municipio` and the free-text `actividad` are dropped: names resolve in the
# view against cvegeo and cat_actividades.
PUNTOS_COLUMNS: Final[list[str]] = [
    "fecha_corte",
    "clave_punto",
    "region",
    "municipio_id",
    "nombre_espacio",
    "dias_horarios",
    "actividad_id",
    "cantidad_usuarios",
    "longitud",
    "latitud",
]

# NOT NULL columns of the fact table and its unique key.
REQUIRED_COLUMNS: Final[list[str]] = ["clave_punto", "municipio_id", "nombre_espacio", "fecha_corte"]
UNIQUE_KEY: Final[list[str]] = ["fecha_corte", "municipio_id", "nombre_espacio"]

ACTIVIDADES_COLUMNS: Final[list[str]] = ["id", "actividad"]

INTEGER_COLUMNS: Final[list[str]] = ["clave_punto", "municipio_id", "actividad_id", "cantidad_usuarios"]
FLOAT_COLUMNS: Final[list[str]] = ["latitud", "longitud"]

# Words kept in lowercase unless they open the label ("Sierra de Amula").
LOWERCASE_WORDS: Final[frozenset[str]] = frozenset({"de", "del", "la", "las", "los", "y", "e", "en", "el", "a", "al"})

# Transformed frames.
ACADEMIAS_FRAME: Final[str] = "academias"
POLIDEPORTIVOS_FRAME: Final[str] = "polideportivos"
POLIDEPORTIVO_DEPORTES_FRAME: Final[str] = "polideportivo_deportes"

# Dates in the gpkg files are dd/mm/yyyy text.
GEO_DATE_FORMAT: Final[str] = "%d/%m/%Y"
WGS84: Final[str] = "EPSG:4326"

ACADEMIAS_RENAMES: Final[dict[str, str]] = {
    "fecha": "fecha_corte",
    "cve_mun": "municipio_id",
    "deportenombrelargo": "deporte_nombre_largo",
}

# Names (municipio, deporte) are dropped: municipio resolves in the view against
# cvegeo and deporte through the catalog. `cat_deporte` is only used to audit.
ACADEMIAS_COLUMNS: Final[list[str]] = [
    "fecha_corte",
    "municipio_id",
    "beneficiarios_total",
    "beneficiarios_hombres",
    "beneficiarios_mujeres",
    "deporte_nombre_largo",
    "deporte",
    "cat_deporte",
    "tipo",
    "domicilio",
    "horarios",
    "longitud",
    "latitud",
]
ACADEMIAS_INTEGER_COLUMNS: Final[list[str]] = [
    "municipio_id",
    "beneficiarios_total",
    "beneficiarios_hombres",
    "beneficiarios_mujeres",
]
ACADEMIAS_REQUIRED_COLUMNS: Final[list[str]] = ["fecha_corte", "municipio_id", "deporte_id", "tipo"]

POLIDEPORTIVOS_RENAMES: Final[dict[str, str]] = {
    "fecha": "fecha_corte",
    "clave_entidad": "entidad_id",
    "cve_mun": "municipio_id",
}
POLIDEPORTIVOS_COLUMNS: Final[list[str]] = [
    "fecha_corte",
    "entidad_id",
    "municipio_id",
    "nombre_centro",
    "domicilio",
    "horarios",
    "servicios",
    "deportes",
    "longitud",
    "latitud",
]
POLIDEPORTIVOS_INTEGER_COLUMNS: Final[list[str]] = ["entidad_id", "municipio_id"]
POLIDEPORTIVOS_REQUIRED_COLUMNS: Final[list[str]] = ["fecha_corte", "entidad_id", "municipio_id", "nombre_centro"]
POLIDEPORTIVOS_UNIQUE_KEY: Final[list[str]] = ["fecha_corte", "municipio_id", "nombre_centro"]
DEPORTES_SEPARATOR: Final[str] = ","

DEPORTES_COLUMNS: Final[list[str]] = ["id", "deporte"]
