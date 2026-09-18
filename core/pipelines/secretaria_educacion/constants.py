from typing import Final

PIPELINE_NAME: Final[str] = "secretaria_educacion"

DIRECTORIO_DATASET: Final[str] = "directorio"
PROGRAMAS_DATASET: Final[str] = "programas"
AULAS_GOOGLE_DATASET: Final[str] = "aulas_google"

DATASETS: Final[list[str]] = [DIRECTORIO_DATASET, PROGRAMAS_DATASET, AULAS_GOOGLE_DATASET]

# El formulario captura el nombre del conjunto como texto libre, así que el ruteo
# es por prefijo normalizado: "Aulas google 2026-2027" sigue cayendo en su dataset.
DATASET_PREFIXES: Final[dict[str, str]] = {
    "directorio catalogo centros de trabajo": DIRECTORIO_DATASET,
    "escuelas beneficiadas por programas estrategicos": PROGRAMAS_DATASET,
    "aulas google": AULAS_GOOGLE_DATASET,
}

MANIFEST_FILENAME: Final[str] = "manifest.json"

NULL_VALUES: Final[list[str]] = ["NA", "N/A", "null", "nan", ""]

# El xlsx del directorio trae título, notas metodológicas y una leyenda antes de
# los encabezados reales.
DIRECTORIO_HEADER_ROW: Final[int] = 13

DIRECTORIO_RENAMES: Final[dict[str, str]] = {
    "clave_de_centro_de_trabajo": "clave_ct",
    "turno": "turno_id",
    "nombre_turno": "turno",
    "nombre_del_centro_de_trabajo": "nombre_ct",
    "localidad": "clave_localidad",
    "nombre_localidad": "localidad",
    "colonia": "clave_colonia",
    "nombre_colonia": "colonia",
    "municipio": "municipio_id",
    "nombre_sostenimiento": "sostenimiento",
    "region": "region_id",
    "nombre_region": "region",
    "matricula_hombres": "hombres_matriculados",
    "matricula_mujeres": "mujeres_matriculadas",
    "matricula_total": "total_matriculados",
    "total_de_docentes_y_directivo_frente_a_grupo": "total_docentes_directivo",
}

# Columnas que sobreviven al transform. nombre_municipio se descarta: el nombre
# se resuelve en la vista contra cvegeo.
DIRECTORIO_COLUMNS: Final[list[str]] = [
    "clave_ct",
    "turno_id",
    "turno",
    "nombre_ct",
    "domicilio",
    "clave_localidad",
    "localidad",
    "clave_colonia",
    "colonia",
    "municipio_id",
    "medio",
    "director",
    "codigo_postal",
    "telefono",
    "zona_escolar",
    "sector",
    "sostenimiento",
    "nivel",
    "programa",
    "region_id",
    "region",
    "longitud",
    "latitud",
    "escuelas",
    "hombres_matriculados",
    "mujeres_matriculadas",
    "total_matriculados",
    "total_docentes_directivo",
]

AULAS_RENAMES: Final[dict[str, str]] = {
    "clave_de_centro_de_trabajo": "clave_ct",
    "nombre_del_centro_de_trabajo": "nombre_ct",
    "region": "region_operativa",
}

# `municipio` es columna de trabajo: el load la resuelve a municipio_id contra
# cvegeo y no llega a ninguna tabla.
AULAS_COLUMNS: Final[list[str]] = [
    "clave_ct",
    "nombre_ct",
    "inmueble",
    "region_operativa",
    "municipio",
    "aulas_asignadas",
]

PROGRAMAS_RENAMES: Final[dict[str, str]] = {
    "clave_de_centro_de_trabajo": "clave_ct",
    "programa": "programa_estrategico",
}

PROGRAMAS_COLUMNS: Final[list[str]] = ["clave_ct", "programa_estrategico"]

# Nombres propios y etiquetas cortas: title case con preposiciones en minúscula.
TITLE_COLS: Final[list[str]] = [
    "nombre_ct",
    "domicilio",
    "localidad",
    "colonia",
    "region",
    "region_operativa",
    "municipio",
    "turno",
    "medio",
    "nivel",
    "sostenimiento",
]

# Descripciones largas: solo la primera letra en mayúscula.
CAPITALIZE_COLS: Final[list[str]] = ["programa", "programa_estrategico"]

# Los nombres de director vienen sin acentos desde el origen y son miles de
# valores distintos. Se les da title case pero no se restituyen acentos:
# adivinarlos produciría errores en nombres de personas reales.
PLAIN_TITLE_COLS: Final[list[str]] = ["director"]

# Palabras que no se capitalizan salvo al inicio del nombre.
LOWERCASE_WORDS: Final[frozenset[str]] = frozenset({"de", "del", "la", "las", "los", "y", "e", "en", "el", "a", "al"})

# Siglas y nombres propios que conservan su forma canónica dentro del texto.
CANONICAL_TOKENS: Final[tuple[str, ...]] = ("ZMG", "CAM", "CENDI", "CONAFE", "SEJ", "Jalisco")

# Acentos que el mapa global no cubre, en la línea de DEFUNCIONES_ACCENT_MAP.
SEJ_ACCENT_MAP: Final[dict[str, str]] = {
    r"\bAUTONOMO\b": "AUTÓNOMO",
    r"\bBILINGUE\b": "BILINGÜE",
    r"\bTECNOLOGICO\b": "TECNOLÓGICO",
    r"\bINDIGENA\b": "INDÍGENA",
    r"\bMUSICA\b": "MÚSICA",
}

DIRECTORIO_NUMERIC_COLUMNS: Final[list[str]] = [
    "turno_id",
    "clave_localidad",
    "clave_colonia",
    "municipio_id",
    "zona_escolar",
    "sector",
    "region_id",
    "escuelas",
    "hombres_matriculados",
    "mujeres_matriculadas",
    "total_matriculados",
    "total_docentes_directivo",
]

DIRECTORIO_FLOAT_COLUMNS: Final[list[str]] = ["longitud", "latitud"]

# Valores centinela del origen que significan "no especificado". El 999 de zona
# escolar queda aislado tras el 255, que es la última zona real.
SENTINEL_VALUES: Final[dict[str, list[int]]] = {"zona_escolar": [999]}

# El origen usa 0 como "sin dato" en estas columnas opcionales.
ZERO_TO_NULL_COLUMNS: Final[list[str]] = [
    "telefono",
    "codigo_postal",
    "clave_colonia",
    "colonia",
    "sector",
    "zona_escolar",
]
