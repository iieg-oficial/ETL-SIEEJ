from pathlib import Path

import numpy as np
import pytest
import rasterio
from affine import Affine
from rasterio.io import MemoryFile
from rasterio.warp import transform_bounds

from core.pipelines.pendientes.constants import EXPERIMENT_BASELINE_SHA256
from core.pipelines.pendientes.helpers.methodology.source_diagnostics import (
    equivalent_native_window,
    metric_derivatives,
    native_neighbor_differences,
    profile_coordinates,
    quantization_summary,
    spatial_difference_metrics,
    write_profile_csv,
)
from core.pipelines.pendientes.helpers.methodology.source_diagnostic import PendientesSourceDiagnostic


def test_equivalent_window_uses_geographic_footprint_across_crs():
    transform = Affine(1 / 7200, 0, -104.0, 0, -1 / 7200, 21.0)
    profile = {
        "driver": "GTiff",
        "height": 7200,
        "width": 7200,
        "count": 1,
        "dtype": "int16",
        "crs": "EPSG:6365",
        "transform": transform,
        "nodata": 32767,
    }
    native_bounds = (-103.8, 20.2, -103.6, 20.4)
    target_bounds = transform_bounds("EPSG:6365", "EPSG:6368", *native_bounds, densify_pts=21)
    with MemoryFile() as memory:
        with memory.open(**profile) as source:
            window, extracted_bounds = equivalent_native_window(source, target_bounds, rasterio.CRS.from_epsg(6368))
    assert window.width > 0 and window.height > 0
    assert extracted_bounds[0] <= native_bounds[0]
    assert extracted_bounds[1] <= native_bounds[1]
    assert extracted_bounds[2] >= native_bounds[2]
    assert extracted_bounds[3] >= native_bounds[3]


def test_spatial_comparison_requires_common_qa_grid_and_reports_known_delta():
    with pytest.raises(ValueError, match="shared QA grid"):
        spatial_difference_metrics(np.zeros((2, 2)), np.zeros((3, 3)))
    reference = np.array([[1, 2], [3, 4]], dtype=np.float32)
    comparison = reference + 0.5
    metrics = spatial_difference_metrics(reference, comparison, nodata=None)
    assert metrics["bias"] == pytest.approx(0.5)
    assert metrics["mae"] == pytest.approx(0.5)
    assert metrics["rmse"] == pytest.approx(0.5)


def test_int16_quantization_and_native_neighbor_thresholds_are_explicit():
    values = np.array([[10, 10, 11], [12, 13, 15]], dtype=np.int16)
    quantization = quantization_summary(values, 32767)
    neighbors = native_neighbor_differences(values, 32767)
    assert quantization["storage_dtype"] == "int16"
    assert quantization["integer_value_percentage"] == 100.0
    assert quantization["unique_elevation_count"] == 5
    assert neighbors["dz_x"]["percentage_abs_dz_eq_0_m"] == pytest.approx(25.0)
    assert neighbors["dz_x"]["percentage_abs_dz_le_2_m"] == 100.0


def test_profiles_and_csv_are_reproducible(tmp_path: Path):
    first = profile_coordinates(750968, 2329434, 1200, 15, 43.5, 300)
    second = profile_coordinates(750968, 2329434, 1200, 15, 43.5, 300)
    for left, right in zip(first, second, strict=True):
        assert np.array_equal(left, right)
    records = [
        {
            "distance_m": float(distance),
            "x_epsg6368": float(x),
            "y_epsg6368": float(y),
            "longitude_epsg6365": -103.0,
            "latitude_epsg6365": 20.0,
            "native_elevation_m": 100.0,
            "baseline_elevation_m": 100.25,
        }
        for distance, x, y in zip(*first, strict=True)
    ]
    first_path = write_profile_csv(tmp_path / "first.csv", records)
    second_path = write_profile_csv(tmp_path / "second.csv", records)
    assert first_path.read_bytes() == second_path.read_bytes()


def test_metric_derivative_uses_metric_xy_for_metre_z():
    x = np.arange(7, dtype=np.float32) * 15
    elevation = np.tile(x, (7, 1))
    derivatives = metric_derivatives(elevation, 15, nodata=None)
    slope = derivatives["slope"][derivatives["slope_valid"]]
    assert np.allclose(slope, 45.0)


def test_baseline_checksum_contract_remains_frozen():
    assert EXPERIMENT_BASELINE_SHA256 == "1461f63298509f045476b9e6e0597ee8eba3138af82e033eb232ddef3bf50fcd"


def test_evidence_state_supersedes_binary_localization_without_raster_classification():
    diagnostic = PendientesSourceDiagnostic()
    profile = {
        "summary": {
            "alternating_plateau_step_sequences": 10,
            "plateau_transition_percentage": 20.0,
        }
    }
    results = {
        "problema_manual": {
            "native_window": {"quantization": {"integer_value_percentage": 100.0}},
            "profiles": {"transects": [profile, profile, profile]},
            "derivatives": {
                "second_difference_magnitude_m": {
                    "source": {"percentiles": {"p95": 2.0}},
                    "baseline": {"percentiles": {"p95": 1.0}},
                }
            },
        }
    }
    evidence = diagnostic._classify_evidence(results)
    assert evidence["categories"] == ["principalmente_presente_en_fuente"]
    assert evidence["source_signal_present"] is True
