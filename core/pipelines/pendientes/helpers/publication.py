from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.windows import transform as window_transform
from shapely.geometry import mapping

from core.pipelines.pendientes.constants import (
    CONDITIONED_DEM_PRODUCT,
    CONDITIONING_PROMOTION_QA_FIELDS,
    FINAL_NODATA,
    PRODUCT_CONTRACT,
    SOURCE_NAME,
    TARGET_RESOLUTION_M,
    TARGET_SRID,
)
from core.pipelines.pendientes.helpers.raster import inspect_raster, validate_analytic_grid
from core.utils.files import sha256_file


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _territorial_mask_qa(path: Path, jalisco_geometry: Any) -> dict[str, int | float]:
    """Validate and summarize the territorial mask one native block at a time."""
    inside_pixels = 0
    valid_inside_pixels = 0
    valid_outside_pixels = 0
    with rasterio.open(path, "r") as dataset:
        for _, window in dataset.block_windows(1):
            values = dataset.read(1, window=window, masked=True)
            outside = geometry_mask(
                [mapping(jalisco_geometry)],
                out_shape=(int(window.height), int(window.width)),
                transform=window_transform(window, dataset.transform),
                invert=False,
            )
            valid = ~np.ma.getmaskarray(values)
            inside = ~outside
            inside_pixels += int(np.count_nonzero(inside))
            valid_inside_pixels += int(np.count_nonzero(inside & valid))
            valid_outside_pixels += int(np.count_nonzero(outside & valid))
    if valid_outside_pixels:
        raise ValueError("Product contains valid pixels outside the official Jalisco polygon")
    if not valid_inside_pixels:
        raise ValueError("Product has no valid coverage inside Jalisco")
    return {
        "inside_pixels": inside_pixels,
        "valid_inside_pixels": valid_inside_pixels,
        "nodata_inside_pixels": inside_pixels - valid_inside_pixels,
        "valid_outside_pixels": valid_outside_pixels,
        "inside_coverage_percentage": valid_inside_pixels / inside_pixels * 100 if inside_pixels else 0.0,
    }


def _validate_aligned_bounds(bounds: tuple[float, float, float, float], resolution: float) -> None:
    if any(abs(value / resolution - round(value / resolution)) > 1e-8 for value in bounds):
        raise ValueError(f"Product extent is not aligned to the {resolution} m grid: {bounds}")


def validate_product_contract(product_name: str, path: Path, jalisco_geometry: Any) -> dict[str, Any]:
    if product_name not in PRODUCT_CONTRACT:
        raise ValueError(f"Unknown canonical product: {product_name}")
    contract = PRODUCT_CONTRACT[product_name]
    metadata = inspect_raster(path)
    validate_analytic_grid(metadata, TARGET_SRID, TARGET_RESOLUTION_M, metadata.extent)
    _validate_aligned_bounds(metadata.extent, TARGET_RESOLUTION_M)
    if metadata.data_types != (contract["dtype"],):
        raise ValueError(f"{product_name} must use {contract['dtype']}")
    if metadata.nodata != (FINAL_NODATA,):
        raise ValueError(f"{product_name} must use NoData {FINAL_NODATA}")
    if metadata.z_units != (contract["unit"],):
        raise ValueError(f"{product_name} must declare band unit {contract['unit']}")

    jalisco_bounds = jalisco_geometry.bounds
    product_bounds = metadata.extent
    if (
        product_bounds[0] < jalisco_bounds[0] - TARGET_RESOLUTION_M
        or product_bounds[1] < jalisco_bounds[1] - TARGET_RESOLUTION_M
        or product_bounds[2] > jalisco_bounds[2] + TARGET_RESOLUTION_M
        or product_bounds[3] > jalisco_bounds[3] + TARGET_RESOLUTION_M
    ):
        raise ValueError(f"{product_name} extent indicates the analytic buffer may have been published")
    return {
        "name": product_name,
        "display_name": contract["display_name"],
        "filename": contract["filename"],
        "sha256": sha256_file(path),
        "metadata": metadata.to_dict(),
        "territorial_coverage": _territorial_mask_qa(path, jalisco_geometry),
    }


def _validate_shared_grid_and_mask(products: dict[str, Path]) -> None:
    parent_path = products[CONDITIONED_DEM_PRODUCT]
    with rasterio.open(parent_path, "r") as parent:
        for product_name, path in products.items():
            if product_name == CONDITIONED_DEM_PRODUCT:
                continue
            with rasterio.open(path, "r") as child:
                if (
                    parent.width != child.width
                    or parent.height != child.height
                    or parent.crs != child.crs
                    or parent.transform != child.transform
                    or parent.nodata != child.nodata
                ):
                    raise ValueError(f"{product_name} does not share the conditioned DEM grid")
                for _, window in parent.block_windows(1):
                    parent_mask = np.ma.getmaskarray(parent.read(1, window=window, masked=True))
                    child_mask = np.ma.getmaskarray(child.read(1, window=window, masked=True))
                    if not np.array_equal(parent_mask, child_mask):
                        raise ValueError(f"{product_name} does not share the conditioned DEM NoData mask")


def validate_product_set(
    products: dict[str, Path],
    jalisco_geometry: Any,
) -> dict[str, dict[str, Any]]:
    if set(products) != set(PRODUCT_CONTRACT):
        raise ValueError(f"Exactly these products are required: {sorted(PRODUCT_CONTRACT)}")
    validations = {name: validate_product_contract(name, path, jalisco_geometry) for name, path in products.items()}
    _validate_shared_grid_and_mask(products)
    return validations


def validate_pair_consistency(degrees_path: Path, percentage_path: Path, tolerance: float = 1e-4) -> dict[str, float]:
    """Verify grids, masks, and tan(degrees) × 100 block by block."""
    maximum_difference = 0.0
    with rasterio.open(degrees_path, "r") as degrees, rasterio.open(percentage_path, "r") as percentage:
        if (
            degrees.width != percentage.width
            or degrees.height != percentage.height
            or degrees.crs != percentage.crs
            or degrees.transform != percentage.transform
        ):
            raise ValueError("Canonical slope products do not share the same grid")
        for _, window in degrees.block_windows(1):
            degree_values = degrees.read(1, window=window, masked=True)
            percent_values = percentage.read(1, window=window, masked=True)
            degree_mask = np.ma.getmaskarray(degree_values)
            percent_mask = np.ma.getmaskarray(percent_values)
            if not np.array_equal(degree_mask, percent_mask):
                raise ValueError("Canonical slope products do not share the same NoData mask")
            valid = ~degree_mask
            if not valid.any():
                continue
            expected = np.tan(np.radians(degree_values.data[valid].astype(np.float64))) * 100.0
            differences = np.abs(percent_values.data[valid].astype(np.float64) - expected)
            maximum_difference = max(maximum_difference, float(differences.max()))
            if not np.allclose(percent_values.data[valid], expected, atol=tolerance, rtol=tolerance):
                raise ValueError("Degree and percent slope rasters are not mathematically consistent")
    return {"maximum_absolute_percentage_difference": maximum_difference, "tolerance": tolerance}


def validate_lineage_contract(manifest: dict[str, Any], validations: dict[str, dict[str, Any]]) -> dict[str, Any]:
    source = manifest.get("source", {})
    if (
        source.get("producer") != "INEGI"
        or source.get("product") != SOURCE_NAME
        or source.get("role") != "source_original"
        or source.get("scope") != "national"
        or source.get("immutable") is not True
        or not _is_sha256(source.get("sha256"))
    ):
        raise ValueError("Products manifest does not identify the immutable original INEGI CEM source")

    reprojection = manifest.get("reprojection", {})
    if (
        reprojection.get("method") != "bilinear"
        or reprojection.get("role") != "staging_baseline"
        or reprojection.get("publishable") is not False
        or reprojection.get("includes_analytic_buffer") is not True
        or not _is_sha256(reprojection.get("baseline_sha256"))
    ):
        raise ValueError("Products manifest has an invalid reprojection lineage")

    conditioning = manifest.get("conditioning", {})
    if (
        not conditioning.get("candidate_id")
        or not conditioning.get("method")
        or not isinstance(conditioning.get("parameters"), dict)
        or conditioning.get("promoted") is not True
        or conditioning.get("baseline_sha256") != reprojection["baseline_sha256"]
    ):
        raise ValueError("Products manifest has no reproducibly promoted conditioning candidate")
    qa = conditioning.get("qa", {})
    missing_qa = sorted(set(CONDITIONING_PROMOTION_QA_FIELDS) - set(qa))
    if missing_qa:
        raise ValueError(f"Conditioned DEM promotion QA is incomplete: {missing_qa}")
    percentiles = qa.get("absolute_difference_percentiles", {})
    if not {"p50", "p90", "p95", "p99"}.issubset(percentiles):
        raise ValueError("Conditioned DEM promotion QA lacks absolute-change percentiles")

    products = manifest.get("products", {})
    conditioned_sha256 = validations[CONDITIONED_DEM_PRODUCT]["sha256"]
    conditioned_entry = products.get(CONDITIONED_DEM_PRODUCT, {})
    if conditioned_entry.get("sha256") != conditioned_sha256:
        raise ValueError("Conditioned DEM checksum does not match its manifest entry")
    for slope_name in ("pendiente_grados", "pendiente_porcentaje"):
        slope_entry = products.get(slope_name, {})
        if (
            slope_entry.get("sha256") != validations[slope_name]["sha256"]
            or slope_entry.get("parent_product") != CONDITIONED_DEM_PRODUCT
            or slope_entry.get("parent_sha256") != conditioned_sha256
        ):
            raise ValueError(f"{slope_name} is not a child of the promoted conditioned DEM from this run")
    return {
        "source_sha256": source["sha256"],
        "baseline_sha256": reprojection["baseline_sha256"],
        "conditioning_candidate_id": conditioning["candidate_id"],
        "conditioning_method": conditioning["method"],
        "conditioning_parameters": conditioning["parameters"],
        "conditioned_dem_sha256": conditioned_sha256,
        "children": ["pendiente_grados", "pendiente_porcentaje"],
    }
