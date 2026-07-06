from typing import Final

EDAD_KEYWORD: Final[str] = "edad"
EDAD_EXCLUDE: Final[tuple[str, ...]] = ("agrup", "gest")

EDAD_DATASET: Final[str] = "cat_edad"
ASISTENCIA_MEDICA_DATASET: Final[str] = "cat_asistencia_medica"
SEXO_DATASET: Final[str] = "cat_sexo"

PROPER_NOUN_CATALOGS: Final[frozenset[str]] = frozenset({"cat_origen", "cat_lenguas"})
