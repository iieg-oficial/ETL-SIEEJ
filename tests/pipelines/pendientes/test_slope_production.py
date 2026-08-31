from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import rasterio
from affine import Affine

from core.pipelines.pendientes.constants import (
    FINAL_NODATA,
    SLOPE_PRODUCTION_PHASE7A_SHA256,
    STATEWIDE_CANDIDATE_SHA256,
)
from core.pipelines.pendientes.helpers.slope_products import (
    create_territorial_degrees,
    create_territorial_percent,
    percent_from_degrees,
    run_context_horn_slope,
    validate_frozen_backend,
    validate_slope_family,
    verify_phase7a_chips,
)
from core.pipelines.pendientes.helpers.slope_selection import planar_surface, write_single_band_raster
from core.pipelines.pendientes.stages.slope_production import PendientesSlopeProduction
from core.utils.files import sha256_file


def _write_tiled(path: Path, values: np.ndarray, transform: Affine, unit: str) -> Path:
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=values.shape[1],
        height=values.shape[0],
        count=1,
        dtype="float32",
        crs="EPSG:6368",
        transform=transform,
        nodata=FINAL_NODATA,
        tiled=True,
        blockxsize=256,
        blockysize=256,
        compress="deflate",
    ) as dataset:
        dataset.write(values.astype(np.float32), 1)
        dataset.set_band_unit(1, unit)
    return path


def _phase7a_backend() -> dict:
    path = Path(
        "data/transform/pendientes/fase_07a_seleccion_algoritmo_pendiente/"
        "slope_algorithm_selection_manifest.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))["next_phase_contract"]["backend"]


def test_frozen_backend_parent_and_phase7a_manifest_contract():
    observed = validate_frozen_backend(_phase7a_backend())
    assert observed["validated"] is True
    assert STATEWIDE_CANDIDATE_SHA256 == (
        "fe3189c49bb2c5bbc8d02fdca40303907c5adeb47ad9af14921a33355324faef"
    )
    manifest_path = Path(
        "data/transform/pendientes/fase_07a_seleccion_algoritmo_pendiente/"
        "slope_algorithm_selection_manifest.json"
    )
    assert sha256_file(manifest_path) == SLOPE_PRODUCTION_PHASE7A_SHA256


def test_context_invocation_is_horn_without_compute_edges_or_percent(tmp_path):
    dem = write_single_band_raster(
        tmp_path / "dem.tif",
        planar_surface(65, 15.0, 30.0, 45.0),
        Affine(15, 0, 0, 0, -15, 975),
        "EPSG:6368",
        "metre",
    )
    output = tmp_path / "slope.tif"
    result = run_context_horn_slope(_phase7a_backend(), dem, output)
    command = result["command"]
    assert command[command.index("-alg") + 1] == "Horn"
    assert "-compute_edges" not in command
    assert "-p" not in command
    with rasterio.open(output) as dataset:
        assert dataset.units == ("degree",)
        assert dataset.block_shapes == [(256, 256)]
        assert np.isclose(dataset.read(1)[32, 32], np.float32(30.0), atol=1e-3)


def test_master_window_mask_percent_math_and_family_lineage(tmp_path):
    transform = Affine(15, 0, 0, 0, -15, 165)
    context_values = np.full((11, 11), 45.0, dtype=np.float32)
    context_values[5, 5] = 60.0
    context = _write_tiled(tmp_path / "context.tif", context_values, transform, "degree")
    master_values = np.full((9, 9), 100.0, dtype=np.float32)
    master_values[0, 0] = FINAL_NODATA
    master = _write_tiled(
        tmp_path / "master.tif",
        master_values,
        Affine(15, 0, 15, 0, -15, 150),
        "metre",
    )
    degrees = tmp_path / "degrees.tif"
    create_territorial_degrees(
        context,
        master,
        degrees,
        {"column_offset": 1, "row_offset": 1, "width": 9, "height": 9},
        processing_window_size=4,
    )
    percent = tmp_path / "percent.tif"
    create_territorial_percent(degrees, percent, processing_window_size=4)
    qa = validate_slope_family(master, degrees, percent, histogram_bins=1000, expected_valid_pixels=80)
    assert qa["hard_gates"]["all_passed"] is True
    assert qa["mask"]["degree_mask_mismatch_pixels"] == 0
    assert qa["mask"]["percent_mask_mismatch_pixels"] == 0
    assert qa["degrees_percent_relation"]["different_float32_pixels"] == 0
    assert qa["percent_qa"]["pixels_gt_100"] == 1
    assert all(value == 0 for value in qa["percent_qa"]["threshold_semantics"].values())
    assert percent_from_degrees(np.array([45.0, 60.0], dtype=np.float32))[0] == np.float32(100.0)
    assert percent_from_degrees(np.array([45.0, 60.0], dtype=np.float32))[1] > np.float32(100.0)


def test_phase7a_chip_reproduction_is_bitwise_for_all_30(tmp_path):
    values = np.arange(64, dtype=np.float32).reshape(8, 8)
    statewide = _write_tiled(tmp_path / "statewide.tif", values, Affine.identity(), "degree")
    reference = _write_tiled(tmp_path / "reference.tif", values[2:6, 2:6], Affine.identity(), "degree")
    inventory = {"chips": []}
    results = {}
    for index in range(30):
        chip_id = f"chip_{index:02d}"
        inventory["chips"].append(
            {"chip_id": chip_id, "column_offset": 2, "row_offset": 2, "width": 4, "height": 4}
        )
        results[chip_id] = {
            "algorithms": {
                "Horn": {"artifact": {"path": str(reference), "sha256": sha256_file(reference)}}
            }
        }
    qa = verify_phase7a_chips(statewide, inventory, {"real_chip_results": results})
    assert qa["chip_count"] == qa["exact_chip_count"] == 30
    assert qa["different_float32_pixels"] == 0
    assert qa["maximum_absolute_difference_degrees"] == 0.0
    assert qa["passed"] is True


def test_final_manifest_records_direct_percent_parent_and_not_published():
    stage = PendientesSlopeProduction()
    manifest = stage._manifest(
        status="slope_family_validated_not_published",
        started=0.0,
        inputs={},
        backend={
            "version": "GDAL test version",
            "edge_policy": "no compute edges",
            "nodata_policy": "full neighborhood",
            "parameters": {"effective_z_factor": 1.0},
        },
        backend_validation={},
        processing={},
        qa={},
        products={
            "pendiente_porcentaje": {
                "parent_product": "pendiente_grados",
                "parent_sha256": "a" * 64,
            }
        },
        phase6b={
            "master_grid": {},
            "lineage": {"source": {}, "baseline": {}},
        },
    )
    assert manifest["status"] == "slope_family_validated_not_published"
    assert manifest["published"] is manifest["loaded"] is manifest["served"] is False
    assert manifest["products"]["pendiente_porcentaje"]["parent_product"] == "pendiente_grados"
