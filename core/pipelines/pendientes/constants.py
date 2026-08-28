from typing import Final

PIPELINE_NAME: Final[str] = "pendientes"
PIPELINE_VERSION: Final[str] = "0.4.0"
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
