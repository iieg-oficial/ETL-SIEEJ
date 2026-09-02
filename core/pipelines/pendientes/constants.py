from typing import Final

PIPELINE_NAME: Final[str] = "pendientes"
PIPELINE_VERSION: Final[str] = "0.16.0"
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
DEM_PROMOTION_PARENT_MANIFEST_SHA256: Final[str] = "af90c02741d3cffe98b30ee6f37afbae8c07ac590421cf09008fd45f6772bdfb"
DEM_PROMOTION_SOURCE_SHA256: Final[str] = "2f291fc05805dc9a9c1bf63b8d26def1b44ebe144f3beb3ef19d0ff72a572a79"
DEM_PROMOTION_DECISIONS: Final[tuple[str, ...]] = (
    "dem_validation_failed",
    "conditioned_dem_validated_for_derivatives",
)
SLOPE_SELECTION_DIRECTORY_NAME: Final[str] = "fase_07a_seleccion_algoritmo_pendiente"
SLOPE_SELECTION_MANIFEST_FILENAME: Final[str] = "slope_algorithm_selection_manifest.json"
SLOPE_SELECTION_PARENT_MANIFEST_SHA256: Final[str] = "9aed5594e044ce78ab7512812c186d088b92d955c375d3e98c60315e797c6e55"
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
SLOPE_PRODUCTION_PHASE7A_SHA256: Final[str] = "0cadc4d50a23c59e6e1e00f10e76ff9135de06e04340eeeb9ce2a21ee26cba6d"
VALIDATED_DEM_SHA256: Final[str] = "bd0bcf1236bd90297cb66f453e3655979294a0e49f5ba802f38aa987dfdbcc03"
VALIDATED_DEGREES_SHA256: Final[str] = "acd6f01e836d94295fc87da3d88747b85a8899821a53fc56abfb0f2bc38b0a3a"
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

CONDITIONED_DEM_PRODUCT: Final[str] = "modelo_elevacion_acondicionado"

FINAL_DIRECTORY_NAME: Final[str] = "final"
FINAL_ANALYTICAL_DIRECTORY_NAME: Final[str] = "analiticos"
FINAL_CARTOGRAPHIC_DIRECTORY_NAME: Final[str] = "cartograficos"
FINAL_TABLE_DIRECTORY_NAME: Final[str] = "tablas"
FINAL_INTERMEDIATE_DIRECTORY_NAME: Final[str] = "intermedios"
FINAL_TRANSFORM_MANIFEST_FILENAME: Final[str] = "transform_manifest.json"
FINAL_MUNICIPAL_STATISTICS_FILENAME: Final[str] = "estadisticas_pendiente_municipal.parquet"
FINAL_DEGREES_CLASSIFIED_FILENAME: Final[str] = "pendiente_grados_clasificada_jalisco_15m.tif"
FINAL_PERCENT_CLASSIFIED_FILENAME: Final[str] = "pendiente_porcentaje_clasificada_jalisco_15m.tif"
CLASSIFIED_NODATA: Final[int] = 255
CLASSIFIED_RESERVED_CODE: Final[int] = 0
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
        "expected_gist_index": "idx_cvegeo_mun_geom_iieg",
        "version": MUNICIPAL_BOUNDARY_ARTIFACT_VERSION,
    },
    "inegi": {
        "id": 2,
        "layer": "municipios_inegi",
        "geometry_column": "geom_inegi",
        "state_geometry_column": "geom_inegi",
        "expected_gist_index": "idx_cvegeo_mun_geom_inegi",
        "version": MUNICIPAL_BOUNDARY_ARTIFACT_VERSION,
    },
}
EXPECTED_MUNICIPALITY_COUNT: Final[int] = 125
JALISCO_CVE_ENT: Final[int] = 14
CONTEXT_DEM_PATH: Final[str] = (
    "data/transform/pendientes/fase_06a_produccion_estatal_candidata/"
    "modelo_elevacion_acondicionado_contexto_jalisco_15m.tif"
)
CONTEXT_DEM_SHA256: Final[str] = "fe3189c49bb2c5bbc8d02fdca40303907c5adeb47ad9af14921a33355324faef"
CONTEXT_WE5_DEGREES_PATH: Final[str] = (
    "data/transform/pendientes/fase_08a2_produccion_cartografica_we5/pendiente_grados_contexto_jalisco_15m.tif"
)
CONTEXT_WE5_DEGREES_SHA256: Final[str] = "c41d4141db9123246789040bfd57f1110f252f529af9b46a54663f68e4df93ed"
FROZEN_RELEASE_COG_SHA256: Final[dict[str, str]] = {
    "modelo_elevacion_acondicionado": "7c533785f0d2740d6dcf9db56aebb05a38e80b07b0b555393a1318806a72fd24",
    "pendiente_grados": "6f211bad0d5bb887770c172a465fe418ba4717e9a1ab007c2eb16518b83615fd",
    "pendiente_porcentaje": "9b4b9dd18d17884eddfa5a01906b72ad8921c3b497329e7c44c73bd6f12ec81a",
    "pendiente_grados_clasificada": "2a4867bf1895561087b30aded549782b9114c6165a326d6aa0f7cea3b5eb5921",
    "pendiente_porcentaje_clasificada": "23f7c5245bb856786f9ea141bbc4563ad3c656e39171e0988f41749db7a533c3",
}
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
MULTISCALE_SLOPE_DIRECTORY_NAME: Final[str] = "fase_08a1_evaluacion_pendiente_multiescala"
MULTISCALE_SLOPE_MANIFEST_FILENAME: Final[str] = "multiscale_slope_evaluation_manifest.json"
MULTISCALE_SLOPE_PARENT_SHA256: Final[str] = STATEWIDE_CANDIDATE_SHA256
MULTISCALE_SLOPE_WINDOWS: Final[tuple[int, ...]] = (3, 5, 7)
MULTISCALE_SLOPE_CONTEXT_PIXELS: Final[int] = 32
MULTISCALE_SMALL_COMPONENT_PIXELS: Final[int] = 9
MULTISCALE_DECISIONS: Final[tuple[str, ...]] = (
    "Horn3x3_mantener_como_cartografico",
    "WoodEvans5x5_recomendado_para_cartografia",
    "WoodEvans7x7_recomendado_para_cartografia",
    "requiere_revision",
)
CARTOGRAPHIC_PRODUCTION_DIRECTORY_NAME: Final[str] = "fase_08a2_produccion_cartografica_we5"
CARTOGRAPHIC_PRODUCTION_MANIFEST_FILENAME: Final[str] = "cartographic_slope_production_manifest.json"
CARTOGRAPHIC_PRODUCTION_CONTEXT_FILENAME: Final[str] = "pendiente_grados_contexto_jalisco_15m.tif"
CARTOGRAPHIC_PRODUCTION_DEGREES_FILENAME: Final[str] = "pendiente_grados_jalisco_15m.tif"
CARTOGRAPHIC_PRODUCTION_PERCENT_FILENAME: Final[str] = "pendiente_porcentaje_jalisco_15m.tif"
CARTOGRAPHIC_PRODUCTION_DECISION: Final[str] = "WoodEvans5x5_recomendado_para_produccion"
CARTOGRAPHIC_PRODUCTION_STATUS: Final[str] = "analytical_and_cartographic_slope_family_validated"
