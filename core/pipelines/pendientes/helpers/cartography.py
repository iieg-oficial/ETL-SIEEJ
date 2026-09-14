from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Any

import numpy as np
import rasterio

from core.pipelines.pendientes.constants import (
    CLASSIFIED_NODATA,
    ELEVATION_Q10_NODATA,
    RASTER_BLOCK_SIZE,
    SIEVE_CONNECTIVITY,
    SIEVE_THRESHOLD,
)
from core.pipelines.pendientes.helpers.windows import core_tile_windows
from core.utils.files import sha256_file


def restricted_sieve_values(original: np.ndarray, proposal: np.ndarray, nodata: int = CLASSIFIED_NODATA) -> np.ndarray:
    if original.shape != proposal.shape:
        raise ValueError("Original and sieve proposal must share a grid")
    output = original.copy()
    valid = (original != nodata) & (proposal != nodata)
    delta = proposal.astype(np.int16) - original.astype(np.int16)
    accepted = valid & (np.abs(delta) == 1)
    output[accepted] = proposal[accepted]
    output[original == nodata] = nodata
    return output


def create_restricted_sieve_raster(
    source_path: Path,
    output_path: Path,
    *,
    processing_window_size: int = 2048,
) -> dict[str, Any]:
    if output_path.exists():
        raise FileExistsError(f"Generalized classified raster already exists: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    proposal_path = output_path.with_suffix(".sieve-proposal.tif")
    partial = output_path.with_suffix(".partial.tif")
    proposal_path.unlink(missing_ok=True)
    partial.unlink(missing_ok=True)
    command = [
        "gdal_sieve.py",
        "-st",
        str(SIEVE_THRESHOLD),
        f"-{SIEVE_CONNECTIVITY}",
        "-of",
        "GTiff",
        str(source_path.resolve()),
        str(proposal_path.resolve()),
    ]
    started = time.perf_counter()
    proposed = accepted = rejected_large_jump = unchanged = nodata_pixels = 0
    transition_counts: dict[str, int] = {}
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        with rasterio.open(source_path) as source, rasterio.open(proposal_path) as proposal:
            if source.shape != proposal.shape or source.transform != proposal.transform or source.crs != proposal.crs:
                raise ValueError("GDAL sieve proposal changed the classified grid")
            profile = source.profile.copy()
            profile.update(
                driver="GTiff",
                dtype="uint8",
                nodata=CLASSIFIED_NODATA,
                tiled=True,
                blockxsize=RASTER_BLOCK_SIZE,
                blockysize=RASTER_BLOCK_SIZE,
                compress="deflate",
                BIGTIFF="IF_SAFER",
            )
            windows = core_tile_windows(source.shape, processing_window_size)
            with rasterio.open(partial, "w", **profile) as destination:
                destination.set_band_unit(1, "class")
                for window in windows:
                    original = source.read(1, window=window)
                    candidate = proposal.read(1, window=window)
                    generalized = restricted_sieve_values(original, candidate)
                    valid = original != CLASSIFIED_NODATA
                    delta = candidate.astype(np.int16) - original.astype(np.int16)
                    proposal_changed = valid & (candidate != CLASSIFIED_NODATA) & (delta != 0)
                    accepted_mask = proposal_changed & (np.abs(delta) == 1)
                    rejected_mask = proposal_changed & (np.abs(delta) >= 2)
                    proposed += int(np.count_nonzero(proposal_changed))
                    accepted += int(np.count_nonzero(accepted_mask))
                    rejected_large_jump += int(np.count_nonzero(rejected_mask))
                    unchanged += int(np.count_nonzero(valid & (generalized == original)))
                    nodata_pixels += int(np.count_nonzero(~valid))
                    for old, new in zip(original[accepted_mask], generalized[accepted_mask], strict=True):
                        key = f"{int(old)}->{int(new)}"
                        transition_counts[key] = transition_counts.get(key, 0) + 1
                    destination.write(generalized, 1, window=window)
        partial.replace(output_path)
    except Exception:
        partial.unlink(missing_ok=True)
        raise
    finally:
        proposal_path.unlink(missing_ok=True)
    return {
        "path": str(output_path),
        "sha256": sha256_file(output_path),
        "source_path": str(source_path),
        "source_sha256": sha256_file(source_path),
        "command": command,
        "threshold": SIEVE_THRESHOLD,
        "removed_component_sizes_pixels": [1, SIEVE_THRESHOLD - 1],
        "connectivity": SIEVE_CONNECTIVITY,
        "acceptance_rule": "abs(candidate_class - original_class) == 1",
        "proposed_change_pixels": proposed,
        "accepted_change_pixels": accepted,
        "rejected_jump_ge_2_pixels": rejected_large_jump,
        "unchanged_valid_pixels": unchanged,
        "nodata_pixels": nodata_pixels,
        "accepted_transitions": transition_counts,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "elapsed_seconds": time.perf_counter() - started,
    }


def quantize_elevation_q10(values: np.ndarray, nodata: float | None) -> np.ndarray:
    valid = np.isfinite(values)
    if nodata is not None:
        valid &= values != nodata
    rounded = np.rint(values[valid].astype(np.float64) / 10.0) * 10.0
    limits = np.iinfo(np.int16)
    if rounded.size and (rounded.min() < limits.min + 1 or rounded.max() > limits.max):
        raise ValueError("Q10 elevation exceeds the Int16 contract")
    output = np.full(values.shape, ELEVATION_Q10_NODATA, dtype=np.int16)
    output[valid] = rounded.astype(np.int16)
    return output


def create_elevation_q10_raster(
    source_path: Path,
    output_path: Path,
    *,
    processing_window_size: int = 2048,
) -> dict[str, Any]:
    if output_path.exists():
        raise FileExistsError(f"Q10 elevation raster already exists: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    partial = output_path.with_suffix(".partial.tif")
    partial.unlink(missing_ok=True)
    valid_pixels = nodata_pixels = nonmultiples = 0
    started = time.perf_counter()
    try:
        with rasterio.open(source_path) as source:
            profile = source.profile.copy()
            profile.update(
                driver="GTiff",
                dtype="int16",
                nodata=ELEVATION_Q10_NODATA,
                tiled=True,
                blockxsize=RASTER_BLOCK_SIZE,
                blockysize=RASTER_BLOCK_SIZE,
                compress="deflate",
                BIGTIFF="IF_SAFER",
            )
            windows = core_tile_windows(source.shape, processing_window_size)
            with rasterio.open(partial, "w", **profile) as destination:
                destination.set_band_unit(1, "metre")
                for window in windows:
                    values = source.read(1, window=window)
                    quantized = quantize_elevation_q10(values, source.nodata)
                    valid = quantized != ELEVATION_Q10_NODATA
                    valid_pixels += int(np.count_nonzero(valid))
                    nodata_pixels += int(np.count_nonzero(~valid))
                    nonmultiples += int(np.count_nonzero(quantized[valid] % 10 != 0))
                    destination.write(quantized, 1, window=window)
        partial.replace(output_path)
    except Exception:
        partial.unlink(missing_ok=True)
        raise
    hard_gates = {
        "all_valid_values_are_multiples_of_10": nonmultiples == 0,
        "valid_pixels_present": valid_pixels > 0,
    }
    return {
        "path": str(output_path),
        "sha256": sha256_file(output_path),
        "parent_path": str(source_path),
        "parent_sha256": sha256_file(source_path),
        "dtype": "Int16",
        "nodata": ELEVATION_Q10_NODATA,
        "vertical_representation_interval_m": 10,
        "method": "round(z / 10) * 10",
        "spatial_filter_after_gaussian": None,
        "valid_pixels": valid_pixels,
        "nodata_pixels": nodata_pixels,
        "nonmultiple_pixels": nonmultiples,
        "hard_gates": {**hard_gates, "all_passed": all(hard_gates.values())},
        "elapsed_seconds": time.perf_counter() - started,
    }
