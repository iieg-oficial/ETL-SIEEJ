from typing import Final

PIPELINE_NAME: Final[str] = "edafologia"
SOURCE_NAME: Final[str] = "INEGI Edafologia historica 1:250 000 Serie III"
SOURCE_VERSION: Final[str] = "Serie III"
SOURCE_FILENAME: Final[str] = "794551118313_s.zip"
CANONICAL_SRID: Final[int] = 6368
JALISCO_CVE_ENT: Final[int] = 14

SOURCE_URL_ENV: Final[str] = "SOURCE_URL"

RENAME_HEADER: Final[dict[str, str]] = {
    "OBJECTID": "source_objectid",
    "Clave_wrb": "clave_wrb",
    "Grupo1": "grupo1_origen",
    "Califp_g1": "califp_g1_origen",
    "Califs_g1": "califs_g1_origen",
    "Grupo2": "grupo2_origen",
    "Califp_g2": "califp_g2_origen",
    "Califs_g2": "califs_g2_origen",
    "Grupo3": "grupo3_origen",
    "Califp_g3": "califp_g3_origen",
    "Clase_tex": "clase_textural_origen",
    "Lmte_sup": "limite_superior_origen",
    "Fase_fis_u": "fase_fisica_origen",
    "Fase_qui_u": "fase_quimica_origen",
    "Shape_Leng": "shape_leng_origen",
    "Shape_Area": "shape_area_origen",
}

EXPECTED_SOURCE_COLUMNS: Final[tuple[str, ...]] = tuple(RENAME_HEADER)
CONTROLLED_SOURCE_COLUMNS: Final[tuple[str, ...]] = ("Grupo1", "Califp_g1", "Califs_g1")
NULL_VALUES: Final[list[str]] = ["", "n/a", "N/A", "na", "NA", "null", "NULL"]

LIMIT_SOURCE_KEYS: Final[tuple[str, str]] = ("iieg", "inegi")
