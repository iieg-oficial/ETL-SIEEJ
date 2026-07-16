from typing import Final

PIPELINE_NAME: Final[str] = "edafologia"
SOURCE_NAME: Final[str] = "INEGI Edafologia historica 1:250 000 Serie III"
SOURCE_VERSION: Final[str] = "Serie III"
SOURCE_FILENAME: Final[str] = "794551118313_s.zip"
CANONICAL_SRID: Final[int] = 6368
JALISCO_CVE_ENT: Final[int] = 14
PIPELINE_VERSION: Final[str] = "0.2.0"

SOURCE_URL_ENV: Final[str] = "SOURCE_URL"
EXPECTED_AREA_LAYER_STEM: Final[str] = "conj_nac_inf_edaf_esc_250k_ser_III_area"
EXCLUDED_POINT_LAYER_SUFFIX: Final[str] = "_pto"
MANIFEST_FILENAME: Final[str] = "manifest.json"
TRANSFORM_MANIFEST_FILENAME: Final[str] = "transform_manifest.json"
TRANSFORM_OUTPUT_FILENAME: Final[str] = "edafologias_transformadas.gpkg"
TRANSFORM_OUTPUT_LAYER: Final[str] = "edafologias"
CVEGEO_TABLE: Final[str] = "public.cvegeo_municipalities"
CVEGEO_ENTITY_FILTER: Final[str] = "cve_ent = 14"
BOUNDARIES_GPKG_FILENAME: Final[str] = "municipal_boundaries.gpkg"
CONTROLLED_CATALOG_VERSION: Final[str] = "v1"
CONTROLLED_CATALOG_ORIGIN: Final[str] = "elaboracion_propia"
CONTROLLED_CATALOG_VERSION_DATE: Final[str | None] = None
CONTROLLED_CATALOG_METHODOLOGY: Final[str] = (
    "Catalogos controlados versionados en el pipeline. Los nombres y codigos confirmados "
    "documentalmente provienen del Diccionario de Datos Edafologicos de INEGI; las decisiones "
    "de seleccion e interpretacion para el pipeline son elaboracion propia del IIEG. "
    "Califp_g1 y Califs_g1 consultan el mismo listado comun de calificadores de los grupos de suelo."
)
CONTROLLED_CATALOG_REFERENCE_INSTITUTION: Final[str] = "INEGI"
CONTROLLED_CATALOG_REFERENCE_DOCUMENT: Final[str] = "Diccionario de Datos Edafologicos"
CONTROLLED_CATALOG_REFERENCE_SCALE: Final[str] = "1:250 000"
CONTROLLED_CATALOG_REFERENCE_DOCUMENT_VERSION: Final[str] = "4"
CONTROLLED_CATALOG_REFERENCE_YEAR: Final[int] = 2016
CONTROLLED_CATALOG_FL_REFERENCE_PAGE: Final[int] = 57
CONTROLLED_CATALOG_STATUS: Final[str] = (
    "catalogo elaborado y transcrito de manera controlada, con verificacion documental progresiva"
)
CONTROLLED_CATALOG_PENDING_METADATA: Final[tuple[str, ...]] = (
    "fecha exacta de version del catalogo IIEG",
    "responsable",
)
MUNICIPAL_BOUNDARY_SOURCES: Final[dict[str, dict[str, str]]] = {
    "iieg": {
        "layer": "municipios_iieg",
        "geometry_column": "geom_iieg",
        "expected_gist_index": "idx_cvegeo_mun_geom_iieg",
    },
    "inegi": {
        "layer": "municipios_inegi",
        "geometry_column": "geom_inegi",
        "expected_gist_index": "idx_cvegeo_mun_geom_inegi",
    },
}

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
VECTOR_EXTENSIONS: Final[tuple[str, ...]] = (".shp", ".gpkg", ".geojson", ".json")
POLYGON_GEOMETRY_TYPES: Final[tuple[str, ...]] = (
    "Polygon",
    "MultiPolygon",
    "Polygon Z",
    "MultiPolygon Z",
    "3D Polygon",
    "3D MultiPolygon",
)

LIMIT_SOURCE_KEYS: Final[tuple[str, str]] = ("iieg", "inegi")

EDAFOLOGIA_RESUMENES_MUNICIPALES_VIEW_COLUMNS: Final[tuple[str, ...]] = (
    "fuente_limite_municipal_id",
    "municipality_cvegeo",
    "source_version",
    "grupo_edafologico_id",
    "calificador_primario_id",
    "calificador_secundario_id",
    "area_m2",
    "area_ha",
    "pct_municipio",
    "fragment_count",
)
