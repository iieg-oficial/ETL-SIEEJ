from typing import Final

PIPELINE_NAME: Final[str] = "pendientes"
PIPELINE_VERSION: Final[str] = "0.14.0"
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
JALISCO_STATE_ID: Final[int] = 14
CVEGEO_DATABASE_NAME: Final[str] = "cvegeo"
CVEGEO_STATE_BOUNDARY_TABLE: Final[str] = "public.cvegeo_state_boundary"
ALLOWED_BOUNDARY_GEOMETRY_COLUMNS: Final[tuple[str, ...]] = ("geom_iieg", "geom_inegi")
DEFAULT_BOUNDARY_GEOMETRY_COLUMN: Final[str] = "geom_iieg"

SOURCE_ZIP_FILENAME: Final[str] = "794551151600_t.zip"
EXTRACT_MANIFEST_FILENAME: Final[str] = "manifest.json"
TRANSFORM_MANIFEST_FILENAME: Final[str] = "transform_manifest.json"
LOAD_MANIFEST_FILENAME: Final[str] = "load_manifest.json"
ANALYTIC_DEM_FILENAME: Final[str] = "cem_reproyectado_baseline.tif"
AOI_FILENAME: Final[str] = "aoi_procesamiento.gpkg"
AOI_TERRITORIAL_LAYER: Final[str] = "jalisco"
AOI_ANALYTIC_LAYER: Final[str] = "jalisco_buffer"
FINAL_DTYPE: Final[str] = "Float32"
FINAL_NODATA: Final[float] = -9999.0
RASTER_BLOCK_SIZE: Final[int] = 256
DIAGNOSTIC_CHIP_SIZE: Final[int] = 1024
NEAR_FLAT_DIFFERENCE_TOLERANCE_M: Final[float] = 1e-6
EXPERIMENT_DIRECTORY_NAME: Final[str] = "fase_04_acondicionamiento"
EXPERIMENT_MANIFEST_FILENAME: Final[str] = "experiment_manifest.json"
EXPERIMENT_CHIP_INVENTORY_FILENAME: Final[str] = "chip_inventory.json"
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
EXPERIMENT_GAUSSIAN_CONFIGS: Final[tuple[dict[str, float | str], ...]] = (
    {"id": "A1", "sigma_pixels": 0.5},
    {"id": "A2", "sigma_pixels": 0.75},
    {"id": "A3", "sigma_pixels": 1.0},
)
EXPERIMENT_BILATERAL_CONFIGS: Final[tuple[dict[str, float | str], ...]] = (
    {"id": "B1", "sigma_dist_pixels": 0.75, "sigma_int_m": 0.5},
    {"id": "B2", "sigma_dist_pixels": 1.0, "sigma_int_m": 1.0},
    {"id": "B3", "sigma_dist_pixels": 1.5, "sigma_int_m": 2.0},
)
EXPERIMENT_FEATURE_PRESERVING_CONFIGS: Final[tuple[dict[str, float | int | str], ...]] = (
    {"id": "C1", "filter": 11, "norm_diff_degrees": 5.0, "num_iter": 1, "max_diff_m": 0.5},
    {"id": "C2", "filter": 11, "norm_diff_degrees": 10.0, "num_iter": 3, "max_diff_m": 1.0},
    {"id": "C3", "filter": 11, "norm_diff_degrees": 15.0, "num_iter": 3, "max_diff_m": 1.0},
)
CALIBRATION_DIRECTORY_NAME: Final[str] = "fase_04b_calibracion"
CALIBRATION_MANIFEST_FILENAME: Final[str] = "calibration_manifest.json"
CALIBRATION_BANDING_REFERENCE_PERCENTILE: Final[float] = 90.0
CALIBRATION_REPETITION_MIN_LAG_PIXELS: Final[int] = 4
CALIBRATION_REPETITION_MAX_LAG_PIXELS: Final[int] = 64
CALIBRATION_PROFILE_OFFSETS_PIXELS: Final[tuple[int, ...]] = (-256, 0, 256)
CALIBRATION_FP_LIMIT_TOLERANCE_M: Final[float] = 1e-5
CALIBRATION_CANDIDATE_ORDER: Final[tuple[str, ...]] = ("RAW", "B2", "FP1", "FP2", "FP3", "FP4")
CALIBRATION_BILATERAL_CONFIG: Final[dict[str, float | str]] = {
    "id": "B2",
    "sigma_dist_pixels": 1.0,
    "sigma_int_m": 1.0,
}
CALIBRATION_FEATURE_PRESERVING_CONFIGS: Final[tuple[dict[str, float | int | str], ...]] = (
    {"id": "FP1", "filter": 11, "norm_diff_degrees": 5.0, "num_iter": 1, "max_diff_m": 0.25},
    {"id": "FP2", "filter": 11, "norm_diff_degrees": 5.0, "num_iter": 1, "max_diff_m": 0.5},
    {"id": "FP3", "filter": 11, "norm_diff_degrees": 7.5, "num_iter": 1, "max_diff_m": 0.5},
    {"id": "FP4", "filter": 11, "norm_diff_degrees": 5.0, "num_iter": 2, "max_diff_m": 0.5},
)
CALIBRATION_DECISION_LABELS: Final[tuple[str, ...]] = (
    "descartar",
    "mantener",
    "recomendado_para_validacion_estatal",
)
STATE_VALIDATION_DIRECTORY_NAME: Final[str] = "fase_05a_validacion_estatal"
STATE_VALIDATION_MANIFEST_FILENAME: Final[str] = "state_validation_manifest.json"
STATE_VALIDATION_INVENTORY_FILENAME: Final[str] = "state_validation_inventory.json"
STATE_VALIDATION_CHIP_COUNT_TARGET: Final[int] = 30
STATE_VALIDATION_SECTOR_COLUMNS: Final[int] = 6
STATE_VALIDATION_SECTOR_ROWS: Final[int] = 6
STATE_VALIDATION_TILE_SIZE_PIXELS: Final[int] = 512
STATE_VALIDATION_HALO_CANDIDATES_PIXELS: Final[tuple[int, ...]] = (5, 6, 8, 12, 16, 24, 32)
STATE_VALIDATION_TILE_TEST_CHIP_COUNT: Final[int] = 4
STATE_VALIDATION_VISUAL_CHIP_COUNT: Final[int] = 10
STATE_VALIDATION_ELEVATION_THRESHOLDS_M: Final[tuple[float, ...]] = (0.1, 0.25, 0.5)
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
STATE_VALIDATION_DECISION_LABELS: Final[tuple[str, ...]] = (
    "rechazar_para_produccion",
    "requiere_ajuste",
    "recomendado_para_promocion",
)
STATE_VALIDATION_FP3_CONFIG: Final[dict[str, float | int | str]] = {
    "id": "FP3",
    "filter": 11,
    "norm_diff_degrees": 7.5,
    "num_iter": 1,
    "max_diff_m": 0.5,
}
BANDING_REVIEW_DIRECTORY_NAME: Final[str] = "fase_05b_detector_banding"
BANDING_REVIEW_CSV_FILENAME: Final[str] = "banding_review.csv"
BANDING_REVIEW_MANIFEST_FILENAME: Final[str] = "banding_detector_manifest.json"
BANDING_REVIEW_PRIORITY_COUNT: Final[int] = 15
BANDING_REVIEW_LABELS: Final[tuple[str, ...]] = (
    "banding_presente",
    "banding_ausente",
    "dudoso",
)
SOURCE_DIAGNOSTIC_DIRECTORY_NAME: Final[str] = "fase_05c_diagnostico_origen"
SOURCE_DIAGNOSTIC_MANIFEST_FILENAME: Final[str] = "source_diagnostic_manifest.json"
SOURCE_DIAGNOSTIC_PROFILE_ANGLE_DEGREES: Final[float] = 43.54017199107539
SOURCE_DIAGNOSTIC_PROFILE_OFFSETS_PIXELS: Final[tuple[int, ...]] = (-128, 0, 128)
SOURCE_DIAGNOSTIC_EVIDENCE_LABELS: Final[tuple[str, ...]] = (
    "principalmente_presente_en_fuente",
    "amplificado_por_reproyeccion",
    "principalmente_inducido_por_reproyeccion",
    "indeterminado",
)
GLOBAL_VALIDATION_DIRECTORY_NAME: Final[str] = "fase_05d_validacion_global_leve"
GLOBAL_VALIDATION_MANIFEST_FILENAME: Final[str] = "global_conditioning_validation_manifest.json"
GLOBAL_VALIDATION_PROFILE_CHIP_COUNT: Final[int] = 10
GLOBAL_VALIDATION_FLOAT_TOLERANCE_M: Final[float] = 1e-5
GLOBAL_VALIDATION_CANDIDATE_IDS: Final[tuple[str, ...]] = ("FP1", "FP2", "FP3")
GLOBAL_VALIDATION_DECISIONS: Final[tuple[str, ...]] = (
    "mantener_RAW",
    "FP1_recomendado_para_procesamiento_estatal",
    "FP2_recomendado_para_procesamiento_estatal",
    "FP3_recomendado_para_procesamiento_estatal",
    "requiere_otra_calibracion",
)
STATEWIDE_CANDIDATE_DIRECTORY_NAME: Final[str] = "fase_06a_produccion_estatal_candidata"
STATEWIDE_CANDIDATE_MANIFEST_FILENAME: Final[str] = "statewide_candidate_manifest.json"
STATEWIDE_CANDIDATE_FILENAME: Final[str] = "modelo_elevacion_acondicionado_contexto_jalisco_15m.tif"
STATEWIDE_CANDIDATE_SHA256: Final[str] = "fe3189c49bb2c5bbc8d02fdca40303907c5adeb47ad9af14921a33355324faef"
STATEWIDE_CANDIDATE_TILE_SIZE_PIXELS: Final[int] = 2048
STATEWIDE_CANDIDATE_HALO_CANDIDATES_PIXELS: Final[tuple[int, ...]] = (5, 6, 8, 12, 16, 24, 32)
STATEWIDE_CANDIDATE_HALO_TEST_CHIP_IDS: Final[tuple[str, ...]] = (
    "problema_manual",
    "sv_06_N02_E05",
    "sv_03_N01_E04",
    "sv_27_N06_E03",
    "sv_14_N04_E01",
    "sv_15_N04_E02",
)
STATEWIDE_CANDIDATE_FP2_CONFIG: Final[dict[str, float | int | str]] = {
    "id": "FP2",
    "filter": 11,
    "norm_diff_degrees": 5.0,
    "num_iter": 1,
    "max_diff_m": 0.5,
    "zfactor": 1.0,
}
STATEWIDE_CANDIDATE_FLOAT_TOLERANCE_M: Final[float] = 1e-5
STATEWIDE_CANDIDATE_DECISIONS: Final[tuple[str, ...]] = (
    "tile_validation_failed",
    "statewide_processing_failed",
    "statewide_candidate_generated_not_promoted",
)
DEM_PROMOTION_DIRECTORY_NAME: Final[str] = "fase_06b_promocion_dem"
DEM_PROMOTION_MANIFEST_FILENAME: Final[str] = "dem_validation_manifest.json"
DEM_PROMOTION_TERRITORIAL_FILENAME: Final[str] = "modelo_elevacion_acondicionado_jalisco_15m.tif"
DEM_PROMOTION_AOI_SHA256: Final[str] = "b54e2a5d1efeea4d5abd697bed76e964bb648baeb07fffb168722de2fd06e63c"
DEM_PROMOTION_PARENT_MANIFEST_SHA256: Final[str] = (
    "af90c02741d3cffe98b30ee6f37afbae8c07ac590421cf09008fd45f6772bdfb"
)
DEM_PROMOTION_SOURCE_SHA256: Final[str] = "2f291fc05805dc9a9c1bf63b8d26def1b44ebe144f3beb3ef19d0ff72a572a79"
DEM_PROMOTION_DECISIONS: Final[tuple[str, ...]] = (
    "dem_validation_failed",
    "conditioned_dem_validated_for_derivatives",
)
SLOPE_SELECTION_DIRECTORY_NAME: Final[str] = "fase_07a_seleccion_algoritmo_pendiente"
SLOPE_SELECTION_MANIFEST_FILENAME: Final[str] = "slope_algorithm_selection_manifest.json"
SLOPE_SELECTION_PARENT_MANIFEST_SHA256: Final[str] = (
    "9aed5594e044ce78ab7512812c186d088b92d955c375d3e98c60315e797c6e55"
)
SLOPE_SELECTION_ALGORITHMS: Final[tuple[str, ...]] = ("Horn", "ZevenbergenThorne")
SLOPE_SELECTION_CONTEXT_PIXELS: Final[int] = 32
SLOPE_SELECTION_DECISIONS: Final[tuple[str, ...]] = (
    "Horn_recomendado_para_produccion",
    "ZevenbergenThorne_recomendado_para_produccion",
    "requiere_revision_metodologica",
)
SLOPE_PRODUCTION_DIRECTORY_NAME: Final[str] = "fase_07b_produccion_pendientes"
SLOPE_PRODUCTION_MANIFEST_FILENAME: Final[str] = "slope_products_manifest.json"
SLOPE_PRODUCTION_CONTEXT_FILENAME: Final[str] = "pendiente_grados_contexto_jalisco_15m.tif"
SLOPE_PRODUCTION_DEGREES_FILENAME: Final[str] = "pendiente_grados_jalisco_15m.tif"
SLOPE_PRODUCTION_PERCENT_FILENAME: Final[str] = "pendiente_porcentaje_jalisco_15m.tif"
SLOPE_PRODUCTION_PHASE7A_SHA256: Final[str] = (
    "0cadc4d50a23c59e6e1e00f10e76ff9135de06e04340eeeb9ce2a21ee26cba6d"
)
SLOPE_PRODUCTION_STATUSES: Final[tuple[str, ...]] = (
    "slope_production_failed",
    "slope_family_validated_not_published",
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
ADMITTED_SLOPE_ALGORITHMS: Final[tuple[str, ...]] = ("Horn", "ZevenbergenThorne")
INITIAL_SLOPE_CANDIDATE: Final[str] = "Horn"
SUPPORTED_SOURCE_DTYPES: Final[tuple[str, ...]] = (
    "Byte",
    "Int16",
    "UInt16",
    "Int32",
    "UInt32",
    "Float32",
    "Float64",
)

CONDITIONED_DEM_PRODUCT: Final[str] = "modelo_elevacion_acondicionado"
CONDITIONED_DEM_DISPLAY_NAME: Final[str] = "Modelo de elevación acondicionado de Jalisco"
PRODUCT_CONTRACT: Final[dict[str, dict[str, str]]] = {
    CONDITIONED_DEM_PRODUCT: {
        "display_name": CONDITIONED_DEM_DISPLAY_NAME,
        "unit": "metre",
        "dtype": FINAL_DTYPE,
        "filename": "modelo_elevacion_acondicionado_jalisco_15m.tif",
    },
    "pendiente_grados": {
        "display_name": "Pendiente de Jalisco en grados",
        "unit": "degree",
        "dtype": FINAL_DTYPE,
        "filename": "pendiente_grados_jalisco_15m.tif",
    },
    "pendiente_porcentaje": {
        "display_name": "Pendiente de Jalisco en porcentaje",
        "unit": "percent",
        "dtype": FINAL_DTYPE,
        "filename": "pendiente_porcentaje_jalisco_15m.tif",
    },
}

CONDITIONING_PROMOTION_QA_FIELDS: Final[tuple[str, ...]] = (
    "mae",
    "rmse",
    "bias",
    "absolute_difference_percentiles",
    "maximum_absolute",
    "modified_pixel_percentage",
    "ridge_preservation",
    "gully_preservation",
    "banding_reduction",
    "flat_terrain_behavior",
    "mountain_terrain_behavior",
)

EXPERIMENT_BASELINE: Final[str] = "raw"
EXPERIMENT_METRICS: Final[tuple[str, ...]] = (
    "elevation_difference",
    "mae",
    "rmse_against_reprojected_dem",
    "bias",
    "p50_absolute",
    "p90_absolute",
    "p95_absolute",
    "p99_absolute",
    "maximum_absolute",
    "slope_distribution",
    "p50",
    "p90",
    "p95",
    "p99",
    "maximum",
    "modified_pixel_percentage",
    "ridge_preservation",
    "gully_preservation",
    "banding_reduction",
    "flat_terrain_behavior",
    "mountain_terrain_behavior",
)
