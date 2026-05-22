from typing import Final, List

RENAME_HEADER: Final[dict[str, str]] = {
    "cve_geo": "cve_geo",
    "entidad_id": "entidad_id",
    "municipio_id": "municipio_id",
    "porc_participacion_2018": "2018",
    "porc_participacion_2021": "2021",
    "porc_participacion_2024": "2024",
}

NULL_VALUES: Final[List[str]] = ["n.a.", "n/a", "na", "null", ""]

YEAR_COLUMNS: Final[List[str]] = ["2018", "2021", "2024"]
