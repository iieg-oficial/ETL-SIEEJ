from typing import Final

PIPELINE_NAME: Final[str] = "edafologia"
SOURCE_NAME: Final[str] = "INEGI Edafologia historica 1:250 000 Serie III"
SOURCE_VERSION: Final[str] = "Serie III"
SOURCE_FILENAME: Final[str] = "794551118313_s.zip"
CANONICAL_SRID: Final[int] = 6368
JALISCO_CVE_ENT: Final[int] = 14
PIPELINE_VERSION: Final[str] = "0.2.0"
BOOTSTRAP_MODE: Final[str] = "bootstrap"

SOURCE_URL_ENV: Final[str] = "SOURCE_URL"
EXPECTED_AREA_LAYER_STEM: Final[str] = "conj_nac_inf_edaf_esc_250k_ser_III_area"
EXCLUDED_POINT_LAYER_SUFFIX: Final[str] = "_pto"
MANIFEST_FILENAME: Final[str] = "manifest.json"
TRANSFORM_MANIFEST_FILENAME: Final[str] = "transform_manifest.json"
TRANSFORM_OUTPUT_FILENAME: Final[str] = "edafologias_transformadas.gpkg"
TRANSFORM_OUTPUT_LAYER: Final[str] = "edafologias"
MUNICIPAL_OVERLAY_DIRNAME: Final[str] = "municipal_overlay"
MUNICIPAL_OVERLAY_OUTPUT_FILENAME: Final[str] = "edafologia_fragmentos_municipales.gpkg"
MUNICIPAL_OVERLAY_OUTPUT_LAYER: Final[str] = "edafologia_fragmentos_municipales"
MUNICIPAL_OVERLAY_MANIFEST_FILENAME: Final[str] = "overlay_manifest.json"
CVEGEO_TABLE: Final[str] = "public.cvegeo_municipalities"
CVEGEO_DATABASE_NAME: Final[str] = "cvegeo"
CVEGEO_ENTITY_FILTER: Final[str] = "cve_ent = 14"
MUNICIPAL_BOUNDARY_ARTIFACT_VERSION: Final[str] = "cvegeo V1"
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
        "version": MUNICIPAL_BOUNDARY_ARTIFACT_VERSION,
    },
    "inegi": {
        "layer": "municipios_inegi",
        "geometry_column": "geom_inegi",
        "expected_gist_index": "idx_cvegeo_mun_geom_inegi",
        "version": MUNICIPAL_BOUNDARY_ARTIFACT_VERSION,
    },
}

RENAME_HEADER: Final[dict[str, str]] = {
    "OBJECTID": "identificador_objeto_fuente",
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
    "Shape_Leng": "longitud_origen",
    "Shape_Area": "superficie_origen",
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
SMALL_FRAGMENT_THRESHOLDS_M2: Final[tuple[float, ...]] = (0.01, 1.0, 10.0, 100.0, 1000.0)
REQUIRED_TRANSFORM_FIELDS: Final[tuple[str, ...]] = (
    "version_fuente",
    "identificador_objeto_fuente",
    "clave_wrb",
    "grupo1_origen",
    "califp_g1_origen",
    "califs_g1_origen",
    "nombre_fuente",
    "url_fuente",
    "nombre_archivo_fuente",
    "sha256_archivo_fuente",
    "fecha_descarga_fuente",
    "fecha_procesamiento",
    "fecha_actualizacion",
)
OVERLAY_COLUMNS: Final[tuple[str, ...]] = (
    "version_fuente",
    "identificador_objeto_fuente",
    "sha256_archivo_fuente",
    "fuente_limite_clave",
    "municipality_id",
    "superficie_m2",
    "superficie_ha",
    "porcentaje_poligono_fuente",
    "porcentaje_municipio_total",
    "porcentaje_cobertura_edafologica",
)

CANONICAL_HASH_FORMULA_VERSION: Final[str] = "edafologia-hash-v1"
CANONICAL_HASH_ALGORITHM: Final[str] = "sha256"
CANONICAL_HASH_FIELD_SEPARATOR: Final[str] = "\u001f"
CANONICAL_HASH_ROW_SEPARATOR: Final[str] = "\n"
CANONICAL_HASH_NULL_TOKEN: Final[str] = "<NULL>"
CANONICAL_HASH_GEOMETRY_SERIALIZATION: Final[str] = (
    "ST_AsEWKB(geometria, 'NDR') encoded as lowercase hexadecimal; EWKB includes SRID"
)
EDA_REPORT_FILENAME: Final[str] = "reporte_eda.json"
ERD_FILENAME: Final[str] = "erd.svg"

EDAFOLOGIA_RESUMENES_MUNICIPALES_VIEW_COLUMNS: Final[tuple[str, ...]] = (
    "fuente_limite_municipal_id",
    "municipality_id",
    "cvegeo",
    "version_fuente",
    "grupo_edafologico_id",
    "calificador_primario_id",
    "calificador_secundario_id",
    "superficie_m2",
    "superficie_ha",
    "porcentaje_municipio",
    "cantidad_fragmentos",
)
