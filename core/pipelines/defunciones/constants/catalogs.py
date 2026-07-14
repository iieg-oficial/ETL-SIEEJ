from typing import Final

EDAD_KEYWORD: Final[str] = "edad"
EDAD_EXCLUDE: Final[tuple[str, ...]] = ("agrup", "gest")

EDAD_DATASET: Final[str] = "cat_edad"
ASISTENCIA_MEDICA_DATASET: Final[str] = "cat_asistencia_medica"
SEXO_DATASET: Final[str] = "cat_sexo"

PROPER_NOUN_CATALOGS: Final[frozenset[str]] = frozenset(
    {"cat_origen", "cat_lenguas", "cat_localidades", "cat_entidad_pais"}
)

ANIO_CATALOG: Final[str] = "cat_anio"

SENTINEL_DESCRIPTIONS: Final[tuple[tuple[str, str], ...]] = (
    (r"^(?:Entidad|Municipio|Localidad)\s+no\s+aplica\b.*$", "No aplica"),
    (r"^(?:Entidad|Municipio|Localidad)\s+no\s+especificad[ao]\b.*$", "No especificado"),
)
