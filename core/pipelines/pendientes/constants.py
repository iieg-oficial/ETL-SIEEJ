from typing import Final

PIPELINE_NAME: Final[str] = "pendientes"
PIPELINE_VERSION: Final[str] = "0.17.0"
SOURCE_NAME: Final[str] = "Continuo de Elevaciones Mexicano 4.0"
SOURCE_PRODUCER: Final[str] = "INEGI"
SOURCE_EDITION: Final[int] = 2025
SOURCE_TEMPORAL_COVERAGE: Final[int] = 2024
SOURCE_UPC: Final[str] = "794551151600"
SOURCE_NOMINAL_RESOLUTION_M: Final[int] = 15
SOURCE_TIFF_MEMBER: Final[str] = "conjunto_de_datos/continuonacional_15m.tif"
SOURCE_TIFF_FILENAME: Final[str] = "continuonacional_15m.tif"
SOURCE_ALLOWED_SRIDS: Final[tuple[int, ...]] = (6365,)
SOURCE_EXPECTED_BANDS: Final[int] = 1
SOURCE_EXPECTED_DTYPE: Final[str] = "Int16"
SOURCE_EXPECTED_NODATA: Final[int] = 32767
SOURCE_EXPECTED_RESOLUTION_DEGREES: Final[float] = 1.0 / 7200.0
SOURCE_RESOLUTION_ABS_TOLERANCE: Final[float] = 1e-10
SOURCE_VERTICAL_QUANTITY: Final[str] = "length"
SOURCE_VERTICAL_UNIT: Final[str] = "metre"
SOURCE_RESAMPLING_DOCUMENTED: Final[str] = "bilinear"
SOURCE_LINEAGE_INPUT: Final[str] = "MDT_125_16bits_sust.tif"
SOURCE_LINEAGE_OUTPUT: Final[str] = "MDT_15m_16bits_bilinear.tif"
SOURCE_LINEAGE_REFERENCES: Final[tuple[str, ...]] = (
    "MDT_125_16bits_filtro2.tif",
    "MDT_125_sust.tif",
)

TARGET_SRID: Final[int] = 6368
TARGET_RESOLUTION_M: Final[float] = 15.0
AOI_BUFFER_M: Final[float] = 10_000.0
CVEGEO_DATABASE_NAME: Final[str] = "cvegeo"
CVEGEO_STATE_BOUNDARY_TABLE: Final[str] = "public.cvegeo_state_boundary"
CVEGEO_MUNICIPALITY_TABLE: Final[str] = "public.cvegeo_municipalities"
ALLOWED_BOUNDARY_GEOMETRY_COLUMNS: Final[tuple[str, ...]] = ("geom_iieg", "geom_inegi")
DEFAULT_BOUNDARY_GEOMETRY_COLUMN: Final[str] = "geom_iieg"

SOURCE_ZIP_FILENAME: Final[str] = "794551151600_t.zip"
EXTRACT_MANIFEST_FILENAME: Final[str] = "manifest.json"
ANALYTIC_DEM_FILENAME: Final[str] = "cem_reproyectado_baseline.tif"
AOI_FILENAME: Final[str] = "aoi_procesamiento.gpkg"
AOI_TERRITORIAL_LAYER: Final[str] = "jalisco"
AOI_ANALYTIC_LAYER: Final[str] = "jalisco_buffer"
FINAL_DTYPE: Final[str] = "Float32"
FINAL_NODATA: Final[float] = -9999.0
RASTER_BLOCK_SIZE: Final[int] = 256
GAUSSIAN_SIGMA_PIXELS: Final[float] = 1.5
GAUSSIAN_SIGMA_METRES: Final[float] = 22.5
GAUSSIAN_TRUNCATE: Final[float] = 4.0
GAUSSIAN_TILE_SIZE_PIXELS: Final[int] = 2048
DIAGNOSTIC_CHIP_SIZE: Final[int] = 1024
NEAR_FLAT_DIFFERENCE_TOLERANCE_M: Final[float] = 1e-6
EXPERIMENT_BASELINE_SHA256: Final[str] = "1461f63298509f045476b9e6e0597ee8eba3138af82e033eb232ddef3bf50fcd"
EXPERIMENT_CHIP_STRIDE: Final[int] = 1024
EXPERIMENT_SELECTION_DECIMATION: Final[int] = 8
EXPERIMENT_MIN_VALID_PERCENTAGE: Final[float] = 99.5
EXPERIMENT_FILTER_HALO_PIXELS: Final[int] = 6
EXPERIMENT_MODIFIED_TOLERANCE_M: Final[float] = 1e-6
EXPERIMENT_STRONG_GRADIENT_PERCENTILE: Final[float] = 90.0
EXPERIMENT_SELECTION_PERCENTILES: Final[tuple[int, ...]] = (10, 25, 40, 50, 60, 75, 90)
EXPERIMENT_ELEVATION_CHANGE_THRESHOLDS_M: Final[tuple[float, ...]] = (0.25, 0.5, 1.0, 2.0)
EXPERIMENT_HILLSHADE_AZIMUTH_DEGREES: Final[float] = 315.0
EXPERIMENT_HILLSHADE_ALTITUDE_DEGREES: Final[float] = 45.0
CALIBRATION_BANDING_REFERENCE_PERCENTILE: Final[float] = 90.0
CALIBRATION_REPETITION_MIN_LAG_PIXELS: Final[int] = 4
CALIBRATION_REPETITION_MAX_LAG_PIXELS: Final[int] = 64
STATE_VALIDATION_DIRECTORY_NAME: Final[str] = "fase_05a_validacion_estatal"
STATE_VALIDATION_MANIFEST_FILENAME: Final[str] = "state_validation_manifest.json"
STATE_VALIDATION_INVENTORY_FILENAME: Final[str] = "state_validation_inventory.json"
STATE_VALIDATION_SECTOR_COLUMNS: Final[int] = 6
STATE_VALIDATION_SECTOR_ROWS: Final[int] = 6
STATE_VALIDATION_BANDING_CLASSES: Final[tuple[str, ...]] = (
    "banding_bajo",
    "banding_medio",
    "banding_alto",
)
STATE_VALIDATION_MORPHOLOGY_CLASSES: Final[tuple[str, ...]] = (
    "plano",
    "lomerio",
    "montana",
    "valle",
    "transicion_valle_sierra",
)
BANDING_REVIEW_DIRECTORY_NAME: Final[str] = "fase_05b_detector_banding"
BANDING_REVIEW_CSV_FILENAME: Final[str] = "banding_review.csv"
BANDING_REVIEW_MANIFEST_FILENAME: Final[str] = "banding_detector_manifest.json"
BANDING_REVIEW_PRIORITY_COUNT: Final[int] = 15
BANDING_REVIEW_LABELS: Final[tuple[str, ...]] = (
    "banding_presente",
    "banding_ausente",
    "dudoso",
)
SLOPE_QA_CLASSES_DEGREES: Final[tuple[tuple[float, float | None], ...]] = (
    (0.0, 2.0),
    (2.0, 5.0),
    (5.0, 10.0),
    (10.0, 15.0),
    (15.0, 30.0),
    (30.0, 45.0),
    (45.0, None),
)
SUPPORTED_SOURCE_DTYPES: Final[tuple[str, ...]] = (
    "Byte",
    "Int16",
    "UInt16",
    "Int32",
    "UInt32",
    "Float32",
    "Float64",
)

FINAL_DIRECTORY_NAME: Final[str] = "final"
FINAL_ANALYTICAL_DIRECTORY_NAME: Final[str] = "analiticos"
FINAL_CARTOGRAPHIC_DIRECTORY_NAME: Final[str] = "cartograficos"
FINAL_TABLE_DIRECTORY_NAME: Final[str] = "tablas"
FINAL_INTERMEDIATE_DIRECTORY_NAME: Final[str] = "intermedios"
FINAL_TRANSFORM_MANIFEST_FILENAME: Final[str] = "transform_manifest.json"
FINAL_MUNICIPAL_STATISTICS_FILENAME: Final[str] = "estadisticas_pendiente_municipal.parquet"
FINAL_DEGREES_CLASSIFIED_FILENAME: Final[str] = "pendiente_grados_clasificada_jalisco_15m.tif"
FINAL_PERCENT_CLASSIFIED_FILENAME: Final[str] = "pendiente_porcentaje_clasificada_jalisco_15m.tif"
FINAL_ELEVATION_Q10_FILENAME: Final[str] = "elevacion_jalisco_intervalo_vertical_10m.tif"
CLASSIFIED_NODATA: Final[int] = 255
CLASSIFIED_RESERVED_CODE: Final[int] = 0
ELEVATION_Q10_NODATA: Final[int] = -32768
SIEVE_THRESHOLD: Final[int] = 8
SIEVE_CONNECTIVITY: Final[int] = 8
COG_BLOCK_SIZE: Final[int] = 512
COG_COMPRESSION: Final[str] = "DEFLATE"
COG_LEVEL: Final[int] = 9
COG_CONTINUOUS_OVERVIEW_RESAMPLING: Final[str] = "AVERAGE"
COG_CLASSIFIED_OVERVIEW_RESAMPLING: Final[str] = "MODE"
COG_CONTINUOUS_OPTIONS: Final[dict[str, str]] = {
    "COMPRESS": COG_COMPRESSION,
    "PREDICTOR": "FLOATING_POINT",
    "OVERVIEW_PREDICTOR": "FLOATING_POINT",
    "LEVEL": str(COG_LEVEL),
    "BLOCKSIZE": str(COG_BLOCK_SIZE),
    "BIGTIFF": "IF_SAFER",
    "OVERVIEWS": "AUTO",
    "OVERVIEW_RESAMPLING": COG_CONTINUOUS_OVERVIEW_RESAMPLING,
}
COG_CLASSIFIED_OPTIONS: Final[dict[str, str]] = {
    "COMPRESS": COG_COMPRESSION,
    "LEVEL": str(COG_LEVEL),
    "BLOCKSIZE": str(COG_BLOCK_SIZE),
    "BIGTIFF": "IF_SAFER",
    "OVERVIEWS": "AUTO",
    "OVERVIEW_RESAMPLING": COG_CLASSIFIED_OVERVIEW_RESAMPLING,
}
COG_ELEVATION_Q10_OPTIONS: Final[dict[str, str]] = dict(COG_CLASSIFIED_OPTIONS)
DEGREES_CLASSIFICATION: Final[tuple[dict[str, object], ...]] = (
    {"code": 1, "lower": 0.0, "upper": 2.0, "label": "llano", "label_es": "Llano"},
    {"code": 2, "lower": 2.0, "upper": 5.0, "label": "suave", "label_es": "Suave"},
    {
        "code": 3,
        "lower": 5.0,
        "upper": 10.0,
        "label": "accidentado_medio",
        "label_es": "Accidentado medio",
    },
    {"code": 4, "lower": 10.0, "upper": 15.0, "label": "accidentado", "label_es": "Accidentado"},
    {
        "code": 5,
        "lower": 15.0,
        "upper": 25.0,
        "label": "fuertemente_accidentado",
        "label_es": "Fuertemente accidentado",
    },
    {"code": 6, "lower": 25.0, "upper": 50.0, "label": "escarpado", "label_es": "Escarpado"},
    {"code": 7, "lower": 50.0, "upper": None, "label": "muy_escarpado", "label_es": "Muy escarpado"},
)
PERCENT_CLASSIFICATION: Final[tuple[dict[str, object], ...]] = (
    {"code": 1, "lower": 0.0, "upper": 0.5, "label": "very_flat", "label_es": "Muy plano"},
    {"code": 2, "lower": 0.5, "upper": 2.0, "label": "flat", "label_es": "Plano"},
    {
        "code": 3,
        "lower": 2.0,
        "upper": 5.0,
        "label": "gently_sloping",
        "label_es": "Suavemente inclinado",
    },
    {"code": 4, "lower": 5.0, "upper": 8.0, "label": "undulating", "label_es": "Ondulado"},
    {
        "code": 5,
        "lower": 8.0,
        "upper": 16.0,
        "label": "rolling",
        "label_es": "Moderadamente accidentado",
    },
    {"code": 6, "lower": 16.0, "upper": 30.0, "label": "hilly", "label_es": "Accidentado"},
    {"code": 7, "lower": 30.0, "upper": 45.0, "label": "steep", "label_es": "Escarpado"},
    {"code": 8, "lower": 45.0, "upper": None, "label": "very_steep", "label_es": "Muy escarpado"},
)
CLASSIFICATION_SOURCES: Final[dict[str, str]] = {
    "degrees": "Precedente cartográfico INEGI-DGG en estudios integrados de cuencas; no es norma universal.",
    "percent": "FAO/IIASA Global Agro-Ecological Zones (GAEZ).",
}
MUNICIPAL_BOUNDARY_FILENAME: Final[str] = "municipal_boundaries.gpkg"
MUNICIPAL_SNAPSHOT_MANIFEST_FILENAME: Final[str] = "municipal_snapshot_manifest.json"
MUNICIPAL_BOUNDARY_ARTIFACT_VERSION: Final[str] = "cvegeo V1"
MUNICIPAL_BOUNDARY_SOURCES: Final[dict[str, dict[str, str | int]]] = {
    "iieg": {
        "id": 1,
        "layer": "municipios_iieg",
        "geometry_column": "geom_iieg",
        "state_geometry_column": "geom_iieg",
        "state_layer": "estado_iieg",
        "expected_gist_index": "idx_cvegeo_mun_geom_iieg",
        "version": MUNICIPAL_BOUNDARY_ARTIFACT_VERSION,
    },
    "inegi": {
        "id": 2,
        "layer": "municipios_inegi",
        "geometry_column": "geom_inegi",
        "state_geometry_column": "geom_inegi",
        "state_layer": "estado_inegi",
        "expected_gist_index": "idx_cvegeo_mun_geom_inegi",
        "version": MUNICIPAL_BOUNDARY_ARTIFACT_VERSION,
    },
}
EXPECTED_MUNICIPALITY_COUNT: Final[int] = 125
JALISCO_CVE_ENT: Final[int] = 14
MUNICIPAL_INDICATOR_IDS: Final[tuple[str, ...]] = (
    "elevacion_media_municipal_m",
    "pendiente_media_municipal_grados",
    "pendiente_mediana_municipal_grados",
    "pendiente_p95_municipal_grados",
    "pendiente_media_municipal_porcentaje",
)
LOAD_ANALYTICAL_DIRECTORY_NAME: Final[str] = "analiticos"
LOAD_GEOPORTAL_DIRECTORY_NAME: Final[str] = "geoportal"
RELEASE_MANIFEST_FILENAME: Final[str] = "release_manifest.json"
MULTISCALE_SLOPE_WINDOWS: Final[tuple[int, ...]] = (3, 5, 7)
MULTISCALE_SMALL_COMPONENT_PIXELS: Final[int] = 9
