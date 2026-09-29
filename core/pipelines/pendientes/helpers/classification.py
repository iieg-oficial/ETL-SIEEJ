from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import numpy as np
import rasterio

from core.pipelines.pendientes.constants import (
    CLASSIFIED_NODATA,
    CLASSIFIED_RESERVED_CODE,
    RASTER_BLOCK_SIZE,
)
from core.pipelines.pendientes.helpers.experimental_metrics import valid_mask
from core.pipelines.pendientes.helpers.windows import core_tile_windows
from core.utils.files import sha256_file


def classify_values(values: np.ndarray, classes: tuple[dict[str, object], ...]) -> np.ndarray:
    output = np.full(values.shape, CLASSIFIED_RESERVED_CODE, dtype=np.uint8)
    for definition in classes:
        lower = float(definition["lower"])
        upper = definition["upper"]
        selected = values >= lower
        if upper is not None:
            selected &= values < float(upper)
        output[selected] = int(definition["code"])
    return output


def threshold_contract_qa(classes: tuple[dict[str, object], ...]) -> dict[str, Any]:
    epsilon = np.float64(1e-9)
    probes: list[dict[str, Any]] = []
    for definition in classes:
        lower = float(definition["lower"])
        code = int(definition["code"])
        values = [lower, lower + epsilon]
        expected = [code, code]
        if lower > 0:
            values.insert(0, lower - epsilon)
            expected.insert(0, code - 1)
        upper = definition["upper"]
        if upper is not None:
            upper_float = float(upper)
            values.extend((upper_float - epsilon, upper_float, upper_float + epsilon))
            expected.extend((code, code + 1, code + 1))
        observed = classify_values(np.asarray(values, dtype=np.float64), classes)
        probes.extend(
            {
                "value": value,
                "expected_code": expected_code,
                "observed_code": int(observed_code),
                "passed": int(observed_code) == expected_code,
            }
            for value, expected_code, observed_code in zip(values, expected, observed, strict=True)
        )
    return {"probes": probes, "all_passed": all(probe["passed"] for probe in probes)}


def create_classified_raster(
    continuous_path: Path,
    output_path: Path,
    classes: tuple[dict[str, object], ...],
    methodological_source: str,
    processing_window_size: int = 2048,
) -> dict[str, Any]:
    if output_path.exists():
        raise FileExistsError(f"Classified analytical raster already exists: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    partial = output_path.with_suffix(".partial.tif")
    partial.unlink(missing_ok=True)
    class_counts = {int(definition["code"]): 0 for definition in classes}
    mask_mismatch = unclassified = reserved = invalid_code = valid_pixels = 0
    started = time.perf_counter()
    with rasterio.open(continuous_path) as source:
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
        try:
            with rasterio.open(partial, "w", **profile) as destination:
                destination.set_band_unit(1, "class")
                for window in windows:
                    continuous = source.read(1, window=window)
                    source_valid = valid_mask(continuous, source.nodata)
                    classified = np.full(continuous.shape, CLASSIFIED_NODATA, dtype=np.uint8)
                    classified[source_valid] = classify_values(continuous[source_valid], classes)
                    classified_valid = classified != CLASSIFIED_NODATA
                    mask_mismatch += int(np.count_nonzero(source_valid ^ classified_valid))
                    valid_pixels += int(np.count_nonzero(classified_valid))
                    reserved += int(np.count_nonzero(classified[source_valid] == CLASSIFIED_RESERVED_CODE))
                    valid_codes = np.asarray(tuple(class_counts), dtype=np.uint8)
                    invalid_code += int(np.count_nonzero(~np.isin(classified[source_valid], valid_codes)))
                    for code in class_counts:
                        class_counts[code] += int(np.count_nonzero(classified == code))
                    destination.write(classified, 1, window=window)
            partial.replace(output_path)
        except Exception:
            partial.unlink(missing_ok=True)
            raise
    unclassified = reserved + invalid_code
    distribution = []
    for definition in classes:
        code = int(definition["code"])
        pixels = class_counts[code]
        distribution.append(
            {
                **definition,
                "lower_inclusive": True,
                "upper_inclusive": False if definition["upper"] is not None else None,
                "pixel_count": pixels,
                "area_ha": pixels * 225.0 / 10_000.0,
                "area_km2": pixels * 225.0 / 1_000_000.0,
                "percentage_of_valid_area": pixels / valid_pixels * 100.0,
                "methodological_source": methodological_source,
            }
        )
    threshold_qa = threshold_contract_qa(classes)
    hard_gates = {
        "mask_equality": mask_mismatch == 0,
        "all_valid_pixels_classified": unclassified == 0,
        "class_count_sum": sum(class_counts.values()) == valid_pixels,
        "reserved_code_absent": reserved == 0,
        "only_defined_codes": invalid_code == 0,
        "threshold_contract": threshold_qa["all_passed"],
    }
    return {
        "path": str(output_path),
        "sha256": sha256_file(output_path),
        "parent_path": str(continuous_path),
        "parent_sha256": sha256_file(continuous_path),
        "dtype": "UInt8",
        "nodata": CLASSIFIED_NODATA,
        "reserved_code": CLASSIFIED_RESERVED_CODE,
        "valid_pixels": valid_pixels,
        "mask_mismatch_pixels": mask_mismatch,
        "valid_pixels_without_class": unclassified,
        "distribution": distribution,
        "threshold_qa": threshold_qa,
        "hard_gates": {**hard_gates, "all_passed": all(hard_gates.values())},
        "processing_window_count": len(windows),
        "elapsed_seconds": time.perf_counter() - started,
    }
