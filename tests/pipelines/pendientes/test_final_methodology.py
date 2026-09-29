from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

from core.pipelines.pendientes.constants import (
    DEGREES_CLASSIFICATION,
    ELEVATION_Q10_NODATA,
    GAUSSIAN_SIGMA_PIXELS,
    GAUSSIAN_TRUNCATE,
    PERCENT_CLASSIFICATION,
    SIEVE_CONNECTIVITY,
    SIEVE_THRESHOLD,
)
from core.pipelines.pendientes.helpers.cartography import (
    create_elevation_q10_raster,
    create_restricted_sieve_raster,
    quantize_elevation_q10,
    restricted_sieve_values,
)
from core.pipelines.pendientes.helpers.classification import classify_values
from core.pipelines.pendientes.helpers.conditioning import create_gaussian_conditioned_dem, normalized_gaussian
from core.pipelines.pendientes.helpers.productive_we5 import inspect_productive_we5_backend, wood_evans_module_commands
from core.pipelines.pendientes.helpers.slope_products import percent_from_degrees


def _raster(path: Path, values: np.ndarray, *, dtype: str = "float32", nodata: float = -9999) -> None:
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=values.shape[1],
        height=values.shape[0],
        count=1,
        dtype=dtype,
        nodata=nodata,
        crs="EPSG:6368",
        transform=from_origin(600_000, 2_400_000, 15, 15),
        tiled=True,
        blockxsize=16,
        blockysize=16,
    ) as dataset:
        dataset.write(values.astype(dtype), 1)
        dataset.set_band_unit(1, "metre" if dtype != "uint8" else "class")


def test_normalized_gaussian_contract_and_nodata_preservation(tmp_path: Path) -> None:
    assert GAUSSIAN_SIGMA_PIXELS == 1.5
    assert GAUSSIAN_TRUNCATE == 4.0
    values = np.full((33, 35), 100.0, dtype=np.float32)
    values[16, 17] = -9999
    expected = normalized_gaussian(
        values,
        sigma_pixels=GAUSSIAN_SIGMA_PIXELS,
        truncate=GAUSSIAN_TRUNCATE,
        nodata=-9999,
    )
    assert expected.dtype == np.float32
    assert expected[16, 17] == -9999
    np.testing.assert_allclose(expected[expected != -9999], 100.0, atol=1e-5)

    source = tmp_path / "source.tif"
    output = tmp_path / "g15.tif"
    _raster(source, values)
    create_gaussian_conditioned_dem(source, output, tile_size=16)
    with rasterio.open(output) as dataset:
        observed = dataset.read(1)
        assert dataset.transform == from_origin(600_000, 2_400_000, 15, 15)
        assert dataset.dtypes == ("float32",)
        assert dataset.nodata == -9999
    assert np.array_equal(observed.view(np.uint32), expected.view(np.uint32))


def test_classification_bins_are_exact_and_independent() -> None:
    degree_values = np.asarray([0, 1.999, 2, 5, 10, 15, 25, 50], dtype=np.float64)
    percent_values = np.asarray([0, 0.499, 0.5, 2, 5, 8, 16, 30, 45], dtype=np.float64)
    assert classify_values(degree_values, DEGREES_CLASSIFICATION).tolist() == [1, 1, 2, 3, 4, 5, 6, 7]
    assert classify_values(percent_values, PERCENT_CLASSIFICATION).tolist() == [1, 1, 2, 3, 4, 5, 6, 7, 8]
    assert len(DEGREES_CLASSIFICATION) != len(PERCENT_CLASSIFICATION)


def test_percent_is_derived_bitwise_from_degrees() -> None:
    degrees = np.asarray([0, 2, 5, 45, 60], dtype=np.float32)
    expected = (np.tan(np.radians(degrees.astype(np.float64))) * 100).astype(np.float32)
    assert np.array_equal(percent_from_degrees(degrees).view(np.uint32), expected.view(np.uint32))


def test_productive_wood_evans_contract_is_exact(tmp_path: Path) -> None:
    backend = inspect_productive_we5_backend()
    assert {key: backend[key] for key in ("method", "size", "exponent", "zscale")} == {
        "method": "slope",
        "size": 5,
        "exponent": 0.0,
        "zscale": 1.0,
    }
    commands = wood_evans_module_commands(tmp_path / "g15.tif", tmp_path / "we5.tif")
    module = next(command for command in commands if command.startswith("r.param.scale"))
    assert "method=slope" in module
    assert "size=5" in module
    assert "exponent=0" in module
    assert "zscale=1" in module
    assert "type=Float32" in commands[-1]


def test_restricted_sieve_accepts_only_adjacent_classes_and_preserves_nodata() -> None:
    original = np.asarray([[1, 2, 1, 4, 2, 255]], dtype=np.uint8)
    proposal = np.asarray([[2, 1, 3, 2, 5, 1]], dtype=np.uint8)
    observed = restricted_sieve_values(original, proposal)
    assert observed.tolist() == [[2, 1, 1, 4, 2, 255]]


def test_restricted_sieve_uses_eight_connectivity_and_threshold_eight(tmp_path: Path) -> None:
    assert SIEVE_CONNECTIVITY == 8
    assert SIEVE_THRESHOLD == 8
    values = np.ones((32, 32), dtype=np.uint8)
    values[2, 2:9] = 2  # seven pixels: proposed and accepted as adjacent class
    values[12, 12] = 3  # one pixel: proposed jump of two and therefore retained
    values[20:23, 20:23] = 2  # nine pixels: not proposed by threshold 8
    source = tmp_path / "raw.tif"
    output = tmp_path / "generalized.tif"
    _raster(source, values, dtype="uint8", nodata=255)
    report = create_restricted_sieve_raster(source, output, processing_window_size=16)
    with rasterio.open(output) as dataset:
        result = dataset.read(1)
    assert np.all(result[2, 2:9] == 1)
    assert result[12, 12] == 3
    assert np.all(result[20:23, 20:23] == 2)
    assert report["accepted_change_pixels"] == 7
    assert report["rejected_jump_ge_2_pixels"] == 1


def test_q10_stores_real_int16_elevations_without_spatial_filter(tmp_path: Path) -> None:
    values = np.asarray([[1534.9, 1535.0, 1544.9, 1545.0, -9999]], dtype=np.float32)
    observed = quantize_elevation_q10(values, -9999)
    assert observed.dtype == np.int16
    assert observed.tolist() == [[1530, 1540, 1540, 1540, ELEVATION_Q10_NODATA]]

    source = tmp_path / "g15.tif"
    output = tmp_path / "q10.tif"
    tiled_values = np.tile(values, (16, 7))
    _raster(source, tiled_values)
    report = create_elevation_q10_raster(source, output, processing_window_size=16)
    with rasterio.open(output) as dataset:
        assert dataset.dtypes == ("int16",)
        assert dataset.nodata == ELEVATION_Q10_NODATA
        valid = dataset.read(1) != ELEVATION_Q10_NODATA
        assert np.all(dataset.read(1)[valid] % 10 == 0)
    assert report["spatial_filter_after_gaussian"] is None
