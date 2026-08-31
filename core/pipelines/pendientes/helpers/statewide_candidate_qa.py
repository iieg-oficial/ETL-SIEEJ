from __future__ import annotations

from pathlib import Path
from typing import Any

from core.utils.files import read_json, sha256_file


def validate_contextual_reference_manifest(
    path: Path,
    expected_chip_count: int,
    expected_halo: int,
    expected_tile_size: int,
) -> dict[str, Any]:
    manifest = read_json(path)
    if manifest is None:
        raise FileNotFoundError(f"Contextual reference manifest not found: {path}")
    checks = {
        "candidate_id": manifest.get("candidate_id") == "FP2",
        "halo_pixels": manifest.get("halo_pixels") == expected_halo,
        "production_tile_size_pixels": manifest.get("production_tile_size_pixels") == expected_tile_size,
        "chip_count": manifest.get("chip_count") == expected_chip_count,
        "exact_chip_count": manifest.get("exact_chip_count") == expected_chip_count,
        "all_chips_exact": manifest.get("all_chips_exact") is True,
        "maximum_difference_zero": all(
            result.get("max_abs_difference") == 0.0
            and result.get("n_pixels_different") == 0
            and result.get("array_identical") is True
            and result.get("mask_mismatch_pixels") == 0
            for result in manifest.get("results", {}).values()
        ),
        "seam_crossing_present": manifest.get("seam_crossing_chip_count", 0) >= 1,
        "all_seam_crossing_exact": manifest.get("all_seam_crossing_chips_exact") is True,
    }
    if len(manifest.get("results", {})) != expected_chip_count:
        checks["result_count"] = False
    if not all(checks.values()):
        raise ValueError(f"Contextual reference validation failed: {checks}")
    return {"path": str(path), "sha256": sha256_file(path), "checks": checks, "manifest": manifest}


def validate_seam_manifest(path: Path, tile_size: int, width: int, height: int) -> dict[str, Any]:
    manifest = read_json(path)
    if manifest is None:
        raise FileNotFoundError(f"Seam QA manifest not found: {path}")
    records = manifest.get("records", [])
    expected_vertical = list(range(tile_size, width, tile_size))
    expected_horizontal = list(range(tile_size, height, tile_size))
    observed_vertical = [
        record["pixel_position"] for record in records if record.get("orientation") == "vertical"
    ]
    observed_horizontal = [
        record["pixel_position"] for record in records if record.get("orientation") == "horizontal"
    ]
    checks = {
        "seam_count": manifest.get("seam_count") == len(expected_vertical) + len(expected_horizontal),
        "all_vertical_boundaries": observed_vertical == expected_vertical,
        "all_horizontal_boundaries": observed_horizontal == expected_horizontal,
        "descriptive_aggregate_present": all(
            key in manifest.get("aggregate", {})
            for key in ("gradient_discontinuity", "second_difference_anomaly")
        ),
    }
    if not all(checks.values()):
        raise ValueError(f"Statewide seam QA validation failed: {checks}")
    return {"path": str(path), "sha256": sha256_file(path), "checks": checks, "manifest": manifest}
