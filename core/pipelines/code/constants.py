from typing import Final

PIPELINE_NAME: Final[str] = "code"

# CODE attached its data in the methodology field of the form, not in the data one.
UPLOAD_FIELD: Final[str] = "adjunte_el_documento_metodologico_asociado_al_conjunto_de_datos"

MANIFEST_FILENAME: Final[str] = "manifest.json"

# Catalogs travel through disk so load can be retried as its own Airflow task.
CATALOGS_FILENAME: Final[str] = "catalogs.pkl"

# The zip also ships a gpkg that duplicates the sheet; the xlsx is the source.
XLSX_GLOB: Final[str] = "*.xlsx"
EXTRACT_DIRNAME: Final[str] = "reto"

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
