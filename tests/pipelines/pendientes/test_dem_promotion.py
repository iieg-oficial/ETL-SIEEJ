from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio
from affine import Affine
from shapely.geometry import box

from core.pipelines.pendientes.constants import (
    DEM_PROMOTION_AOI_SHA256,
    DEM_PROMOTION_PARENT_MANIFEST_SHA256,
    DEM_PROMOTION_SOURCE_SHA256,
    STATEWIDE_CANDIDATE_FP2_CONFIG,
    STATEWIDE_CANDIDATE_SHA256,
)
from core.pipelines.pendientes.helpers.territorial_dem import (
    aligned_territorial_window,
    create_territorial_dem,
    validate_territorial_dem,
)
from core.pipelines.pendientes.helpers.methodology.dem_promotion import PendientesDemPromotion


def _context_raster(path: Path) -> np.ndarray:
    values = np.arange(400, dtype=np.float32).reshape(20, 20)
    values[5, 5] = -9999.0
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=20,
        height=20,
        count=1,
        dtype="float32",
        crs="EPSG:6368",
        transform=Affine(15, 0, 0, 0, -15, 300),
        nodata=-9999.0,
        tiled=True,
        blockxsize=256,
        blockysize=256,
        compress="deflate",
    ) as dataset:
        dataset.write(values, 1)
    return values


def test_territorial_window_is_derived_from_parent_grid(tmp_path):
    context_path = tmp_path / "context.tif"
    _context_raster(context_path)
    geometry = box(37, 52, 263, 278)
    with rasterio.open(context_path) as dataset:
        window = aligned_territorial_window(dataset, geometry)
    assert window.flatten() == (2, 1, 16, 16)


def test_territorial_dem_preserves_values_mask_grid_nodata_and_area(tmp_path):
    context_path = tmp_path / "context.tif"
    _context_raster(context_path)
    output_path = tmp_path / "territorial.tif"
    geometry = box(37, 52, 263, 278)
    processing = create_territorial_dem(context_path, output_path, geometry, processing_window_size=8)
    qa = validate_territorial_dem(
        context_path,
        output_path,
        geometry,
        geometry.area,
        processing_window_size=8,
        histogram_bins=1000,
    )
    assert processing["territorial_window"] == {
        "column_offset": 2,
        "row_offset": 1,
        "width": 16,
        "height": 16,
    }
    assert qa["grid"]["passed"] is True
    assert qa["value_equality"]["different_pixels"] == 0
    assert qa["value_equality"]["max_abs_difference"] == 0
    assert qa["mask"]["mask_mismatch_pixels"] == 0
    assert qa["mask"]["valid_outside_jalisco_pixels"] == 0
    assert qa["mask"]["nodata_inside_jalisco_pixels"] == 1
    assert qa["mask"]["inherited_parent_nodata_inside_jalisco_pixels"] == 1
    assert qa["area"]["valid_area_m2"] == qa["mask"]["valid_dem_pixels"] * 225
    with rasterio.open(output_path) as dataset:
        assert dataset.units == ("metre",)
        assert dataset.nodata == -9999.0


def test_phase6b_frozen_lineage_constants():
    assert STATEWIDE_CANDIDATE_SHA256 == "fe3189c49bb2c5bbc8d02fdca40303907c5adeb47ad9af14921a33355324faef"
    assert DEM_PROMOTION_PARENT_MANIFEST_SHA256 == (
        "af90c02741d3cffe98b30ee6f37afbae8c07ac590421cf09008fd45f6772bdfb"
    )
    assert DEM_PROMOTION_SOURCE_SHA256 == "2f291fc05805dc9a9c1bf63b8d26def1b44ebe144f3beb3ef19d0ff72a572a79"
    assert DEM_PROMOTION_AOI_SHA256 == "b54e2a5d1efeea4d5abd697bed76e964bb648baeb07fffb168722de2fd06e63c"
    assert STATEWIDE_CANDIDATE_FP2_CONFIG["zfactor"] == 1.0


def test_phase6b_rejects_a_changed_frozen_aoi(tmp_path, monkeypatch):
    stage = PendientesDemPromotion()
    stage.aoi_path = tmp_path / "aoi.gpkg"
    stage.aoi_path.write_bytes(b"changed")
    monkeypatch.setattr(
        "core.pipelines.pendientes.helpers.methodology.dem_promotion.sha256_file",
        lambda path: "0" * 64,
    )
    with np.testing.assert_raises_regex(ValueError, "Frozen AOI checksum changed"):
        stage._read_aoi()


def test_phase6b_manifest_promotes_context_parent_for_derivatives(tmp_path, monkeypatch):
    stage = PendientesDemPromotion()
    stage.territorial_path = tmp_path / "territorial.tif"
    stage.territorial_path.write_bytes(b"existing")
    stage.manifest_path = tmp_path / "manifest.json"
    parent = {
        "whitebox_backend": {"observed_version": "WhiteboxTools v2.4.0"},
    }
    source = {"tiff_sha256": DEM_PROMOTION_SOURCE_SHA256}
    monkeypatch.setattr(stage, "_validate_integrity", lambda: (parent, source))
    geometry = box(0, 0, 15, 15)
    monkeypatch.setattr(
        stage,
        "_read_aoi",
        lambda: (
            geometry,
            {
                "sha256": DEM_PROMOTION_AOI_SHA256,
                "vector_area_m2": geometry.area,
            },
        ),
    )
    qa = {
        "grid": {"passed": True, "width": 1, "height": 1, "transform": [15, 0, 0, 0, -15, 15], "bounds": [0, 0, 15, 15]},
        "value_equality": {"bitwise_equal": True, "different_pixels": 0, "max_abs_difference": 0},
        "mask": {
            "mask_mismatch_pixels": 0,
            "valid_outside_jalisco_pixels": 0,
            "nodata_inside_jalisco_pixels": 0,
            "inherited_parent_nodata_inside_jalisco_pixels": 0,
        },
        "area": {},
        "statistics_m": {},
    }
    monkeypatch.setattr(
        "core.pipelines.pendientes.helpers.methodology.dem_promotion.validate_territorial_dem",
        lambda *args: qa,
    )
    monkeypatch.setattr(
        "core.pipelines.pendientes.helpers.methodology.dem_promotion.sha256_file",
        lambda path: {
            stage.baseline_path: "1461f63298509f045476b9e6e0597ee8eba3138af82e033eb232ddef3bf50fcd",
            stage.parent_manifest_path: DEM_PROMOTION_PARENT_MANIFEST_SHA256,
            stage.context_path: STATEWIDE_CANDIDATE_SHA256,
        }.get(path, "a" * 64),
    )
    manifest = stage.execute()
    assert manifest["status"] == "conditioned_dem_validated_for_derivatives"
    assert manifest["derivative_contract"]["slope_parent"] == "validated_context_dem"
    assert manifest["derivative_contract"]["prohibited_slope_parent"] == "territorially_clipped_dem"
    assert manifest["lineage"]["validated_context_dem"]["sha256"] == STATEWIDE_CANDIDATE_SHA256
    assert manifest["master_grid"]["required_products"] == [
        "modelo_elevacion_acondicionado",
        "pendiente_grados",
        "pendiente_porcentaje",
    ]
