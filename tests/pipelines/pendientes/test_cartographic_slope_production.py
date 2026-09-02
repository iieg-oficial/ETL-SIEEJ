from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

from core.pipelines.pendientes.constants import (
    CARTOGRAPHIC_PRODUCTION_DECISION,
    CARTOGRAPHIC_PRODUCTION_STATUS,
    COG_CLASSIFIED_OPTIONS,
    MULTISCALE_SLOPE_PARENT_SHA256,
)
from core.pipelines.pendientes.helpers.methodology.cartographic_slope_production import (
    DEM_COG_SHA256,
    HISTORICAL_COG_SHA256,
    PendientesCartographicSlopeProduction,
)
from core.pipelines.pendientes.helpers.productive_we5 import verify_eight_we5_chips
from core.pipelines.pendientes.helpers.slope_products import percent_from_degrees


def _raster(path: Path, values: np.ndarray, unit: str = "degree") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=values.shape[1],
        height=values.shape[0],
        count=1,
        dtype="float32",
        nodata=-9999,
        crs="EPSG:6368",
        transform=from_origin(0, values.shape[0] * 15, 15, 15),
    ) as dataset:
        dataset.write(values.astype(np.float32), 1)
        dataset.set_band_unit(1, unit)


def test_productive_decision_backend_and_release_contracts_are_frozen(tmp_path: Path) -> None:
    assert CARTOGRAPHIC_PRODUCTION_DECISION == "WoodEvans5x5_recomendado_para_produccion"
    assert CARTOGRAPHIC_PRODUCTION_STATUS == "analytical_and_cartographic_slope_family_validated"
    assert MULTISCALE_SLOPE_PARENT_SHA256 == "fe3189c49bb2c5bbc8d02fdca40303907c5adeb47ad9af14921a33355324faef"
    assert COG_CLASSIFIED_OPTIONS["OVERVIEW_RESAMPLING"] == "MODE"
    production = PendientesCartographicSlopeProduction()
    production.context_dem_path = tmp_path / "context.tif"
    _raster(production.context_dem_path, np.ones((2, 2), dtype=np.float32), unit="metre")
    checkpoint = production._checkpoint({}, {"version": "GRASS GIS 8.3.2"})
    assert checkpoint["parameters"] == {"method": "slope", "size": 5, "exponent": 0.0, "zscale": 1.0}
    assert checkpoint["grass_region"]["crs_epsg"] == 6368
    assert checkpoint["grass_region"]["ewres"] == checkpoint["grass_region"]["nsres"] == 15.0


def test_horn_and_dem_historical_release_hashes_remain_explicit() -> None:
    assert DEM_COG_SHA256 == "7c533785f0d2740d6dcf9db56aebb05a38e80b07b0b555393a1318806a72fd24"
    assert HISTORICAL_COG_SHA256["pendiente_grados"].startswith("3d87bf")
    assert HISTORICAL_COG_SHA256["pendiente_porcentaje"].startswith("68de35")


def test_we5_percent_is_derived_once_and_float32_exact() -> None:
    degrees = np.asarray([0.0, 2.0, 5.0, 45.0, 60.0], dtype=np.float32)
    expected = (np.tan(np.radians(degrees.astype(np.float64))) * 100).astype(np.float32)
    observed = percent_from_degrees(degrees)
    assert observed.dtype == np.float32
    assert np.array_equal(observed.view(np.uint32), expected.view(np.uint32))


def test_statewide_extraction_reproduces_exactly_eight_references(tmp_path: Path) -> None:
    values = np.arange(1024 * 1024, dtype=np.float32).reshape(1024, 1024) / 1000
    statewide = tmp_path / "statewide.tif"
    _raster(statewide, values)
    samples = []
    phase_dir = tmp_path / "phase8a1"
    for index in range(8):
        chip_id = f"chip_{index}"
        samples.append(
            {
                "chip_id": chip_id,
                "center_x": 512 * 15.0,
                "center_y": 512 * 15.0,
            }
        )
        _raster(phase_dir / "chips" / chip_id / "WE5.tif", values)
    report = verify_eight_we5_chips(statewide, {"real_chip_sample": samples}, phase_dir)
    assert report["chip_count"] == report["exact_chip_count"] == 8
    assert report["different_pixels"] == 0
    assert report["max_abs_difference"] == 0
    assert report["hard_gates"]["all_passed"]
