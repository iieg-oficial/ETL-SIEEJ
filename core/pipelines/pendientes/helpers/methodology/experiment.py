from __future__ import annotations

import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from affine import Affine
from rasterio.windows import Window, transform as window_transform

from core.pipelines.pendientes.config import settings
from core.pipelines.pendientes.constants import (
    ANALYTIC_DEM_FILENAME,
    AOI_FILENAME,
    EXPERIMENT_BASELINE_SHA256,
    EXPERIMENT_BILATERAL_CONFIGS,
    EXPERIMENT_CHIP_INVENTORY_FILENAME,
    EXPERIMENT_DIRECTORY_NAME,
    EXPERIMENT_FEATURE_PRESERVING_CONFIGS,
    EXPERIMENT_FILTER_HALO_PIXELS,
    EXPERIMENT_GAUSSIAN_CONFIGS,
    EXPERIMENT_HILLSHADE_ALTITUDE_DEGREES,
    EXPERIMENT_HILLSHADE_AZIMUTH_DEGREES,
    EXPERIMENT_MANIFEST_FILENAME,
    FINAL_NODATA,
    PIPELINE_NAME,
    PIPELINE_VERSION,
    TARGET_RESOLUTION_M,
    TARGET_SRID,
)
from core.pipelines.pendientes.helpers.experimental_artifacts import (
    hillshade,
    write_comparison_png,
    write_float_raster,
)
from core.pipelines.pendientes.helpers.methodology.experimental_chips import (
    ChipWindow,
    manual_chip,
    scan_chip_candidates,
    select_representative_chips,
)
from core.pipelines.pendientes.helpers.methodology.experimental_filters import bilateral_smoothing, gaussian_smoothing
from core.pipelines.pendientes.helpers.experimental_metrics import (
    absolute_laplacian,
    distribution,
    experimental_metrics,
    local_neighbor_magnitude,
    valid_mask,
)
from core.pipelines.pendientes.helpers.experimental_whitebox import (
    inspect_whitebox_backend,
    run_feature_preserving_smoothing,
)
from core.pipelines.pendientes.helpers.slope import experimental_horn_slope
from core.utils.files import sha256_file, write_json_atomic


class PendientesExperiment:
    """Run phase-4 conditioning diagnostics on reproducible chips only."""

    def __init__(self) -> None:
        transform_dir = Path("data") / "transform" / PIPELINE_NAME
        self.baseline_path = transform_dir / ANALYTIC_DEM_FILENAME
        self.aoi_path = transform_dir / AOI_FILENAME
        self.output_dir = transform_dir / EXPERIMENT_DIRECTORY_NAME
        self.manifest_path = self.output_dir / EXPERIMENT_MANIFEST_FILENAME
        self.inventory_path = self.output_dir / EXPERIMENT_CHIP_INVENTORY_FILENAME

    def execute(self) -> dict[str, Any]:
        started = time.perf_counter()
        baseline_contract = self._validate_baseline()
        candidates = scan_chip_candidates(self.baseline_path, self.aoi_path)
        chips, selection = select_representative_chips(candidates)
        if settings.EXPERIMENT_MANUAL_X is not None and settings.EXPERIMENT_MANUAL_Y is not None:
            chips.append(
                manual_chip(
                    self.baseline_path,
                    settings.EXPERIMENT_MANUAL_X,
                    settings.EXPERIMENT_MANUAL_Y,
                )
            )

        backend = self._backend_contract()
        inventory: list[dict[str, Any]] = []
        comparisons: dict[str, Any] = {}
        self.output_dir.mkdir(parents=True, exist_ok=True)
        for chip in chips:
            chip_inventory, chip_comparison = self._run_chip(chip, backend)
            inventory.append(chip_inventory)
            comparisons[chip.chip_id] = chip_comparison
        if backend["status"] == "available":
            backend["executed"] = True

        inventory_manifest = {
            "baseline_path": str(self.baseline_path),
            "baseline_sha256": EXPERIMENT_BASELINE_SHA256,
            "selection": selection,
            "chips": inventory,
            "manual_problem_chip_status": "configured" if len(chips) > 3 else "pending_coordinate",
        }
        write_json_atomic(inventory_manifest, self.inventory_path)
        manifest = {
            "phase": "experimental_conditioning_on_representative_chips",
            "pipeline_version": PIPELINE_VERSION,
            "created_at": datetime.now().astimezone().isoformat(),
            "baseline": baseline_contract,
            "chip_inventory_path": str(self.inventory_path),
            "chip_inventory_sha256": sha256_file(self.inventory_path),
            "selection": selection,
            "methods": self._method_contract(backend),
            "comparisons": comparisons,
            "hillshade": {
                "algorithm": "Horn 3x3 gradient with Lambertian illumination",
                "azimuth_degrees": EXPERIMENT_HILLSHADE_AZIMUTH_DEGREES,
                "altitude_degrees": EXPERIMENT_HILLSHADE_ALTITUDE_DEGREES,
                "z_factor": 1.0,
            },
            "slope": {
                "algorithm": "Horn",
                "unit": "degrees",
                "role": "exploratory QA only",
                "promoted": False,
            },
            "ranking": {
                "winner_selected": False,
                "single_score_computed": False,
                "promotion_thresholds": None,
                "review_contract": "quantitative QA plus comparable visual inspection",
            },
            "outputs": {
                "role": "experimental QA artifacts",
                "publishable": False,
                "institutional_products_generated": [],
            },
            "elapsed_seconds": time.perf_counter() - started,
        }
        write_json_atomic(manifest, self.manifest_path)
        return manifest

    def _validate_baseline(self) -> dict[str, Any]:
        if not self.baseline_path.is_file():
            raise FileNotFoundError(f"Phase-3 baseline not found: {self.baseline_path}")
        observed_sha256 = sha256_file(self.baseline_path)
        if observed_sha256 != EXPERIMENT_BASELINE_SHA256:
            raise ValueError("Phase-3 baseline checksum does not match the frozen experiment input")
        with rasterio.open(self.baseline_path, "r") as dataset:
            if dataset.crs is None:
                raise ValueError("Phase-3 baseline has no CRS")
            raster_contract = {
                "path": str(self.baseline_path),
                "sha256": observed_sha256,
                "crs_epsg": dataset.crs.to_epsg(),
                "resolution_m": [abs(dataset.transform.a), abs(dataset.transform.e)],
                "shape": [dataset.height, dataset.width],
                "dtype": dataset.dtypes[0],
                "nodata": dataset.nodata,
                "bounds": list(dataset.bounds),
            }
            if (
                dataset.crs.to_epsg() != TARGET_SRID
                or dataset.res != (TARGET_RESOLUTION_M, TARGET_RESOLUTION_M)
                or dataset.dtypes != ("float32",)
                or dataset.nodata != FINAL_NODATA
            ):
                raise ValueError(f"Phase-3 baseline contract failed: {raster_contract}")
        return {**raster_contract, "immutable": True, "modified_by_experiment": False}

    def _backend_contract(self) -> dict[str, Any]:
        configured = settings.WHITEBOX_TOOLS_EXECUTABLE
        executable = configured.expanduser().resolve() if configured is not None else None
        discovered = executable if executable is not None and executable.is_file() else shutil.which("whitebox_tools")
        expected_version = settings.WHITEBOX_TOOLS_EXPECTED_VERSION
        expected_sha256 = settings.WHITEBOX_TOOLS_EXPECTED_SHA256
        available = discovered is not None and expected_version is not None and expected_sha256 is not None
        unavailable = {
            "name": "WhiteboxTools FeaturePreservingSmoothing",
            "status": "unavailable",
            "executable": str(discovered) if discovered is not None else None,
            "observed_version": None,
            "expected_exact_version": expected_version,
            "expected_sha256": expected_sha256,
            "license": None,
            "requirements": [
                "explicit executable path or discoverable whitebox_tools command",
                "exact expected version and executable SHA-256 configured and matched before execution",
                "captured command line, stdout, stderr, runtime and output checksum",
            ],
            "reason": "WhiteboxTools executable, expected version and expected SHA-256 are not all configured",
            "executed": False,
        }
        if not available:
            return unavailable
        inspected = inspect_whitebox_backend(Path(str(discovered)), expected_version, expected_sha256)
        return {
            "name": "WhiteboxTools FeaturePreservingSmoothing",
            **inspected,
            "python_frontend_contract": "whitebox==2.3.6",
            "binary_download_is_not_versioned_by_frontend": True,
            "validated": True,
            "executed": False,
        }

    def _method_contract(self, backend: dict[str, Any]) -> dict[str, Any]:
        return {
            "RAW": {"family": "unmodified baseline", "backend": "NumPy copy", "available": True},
            "gaussian": {
                "backend": "NumPy separable normalized convolution",
                "dependency_versions": {"numpy": np.__version__},
                "nodata_strategy": "normalized convolution over valid neighbors; original NoData preserved",
                "boundary_strategy": "reflect on the halo; only the 1024x1024 core is evaluated",
                "configurations": list(EXPERIMENT_GAUSSIAN_CONFIGS),
                "available": True,
            },
            "bilateral": {
                "backend": "NumPy spatial-range weighted convolution",
                "dependency_versions": {"numpy": np.__version__},
                "nodata_strategy": "invalid neighbors have zero weight; original NoData preserved",
                "boundary_strategy": "reflect on the halo; only the 1024x1024 core is evaluated",
                "configurations": list(EXPERIMENT_BILATERAL_CONFIGS),
                "available": True,
            },
            "feature_preserving": {
                "backend": backend,
                "configurations": list(EXPERIMENT_FEATURE_PRESERVING_CONFIGS),
                "z_factor": 1.0,
                "calibration_status": "product-specific calibration pending",
                "available": backend["status"] == "available",
            },
        }

    def _read_chip_context(self, dataset: rasterio.io.DatasetReader, chip: ChipWindow) -> np.ndarray:
        halo = EXPERIMENT_FILTER_HALO_PIXELS
        extended = Window(
            chip.column_offset - halo,
            chip.row_offset - halo,
            chip.width + 2 * halo,
            chip.height + 2 * halo,
        )
        return dataset.read(1, window=extended)

    def _inventory(self, chip: ChipWindow, raw: np.ndarray, nodata: float | None) -> dict[str, Any]:
        valid = valid_mask(raw, nodata)
        slope, _, slope_valid = experimental_horn_slope(raw, TARGET_RESOLUTION_M, nodata)
        laplacian, laplacian_valid = absolute_laplacian(raw, nodata)
        elevations = raw[valid].astype(np.float64, copy=False)
        return {
            **chip.to_dict(),
            "elevation_m": {
                "minimum": float(elevations.min()),
                "mean": float(elevations.mean()),
                "maximum": float(elevations.max()),
            },
            "exploratory_horn_slope_degrees": distribution(slope, slope_valid),
            "roughness_absolute_laplacian_m": distribution(laplacian, laplacian_valid),
            "valid_percentage": float(np.count_nonzero(valid) / valid.size * 100),
        }

    def _condition_candidates(
        self,
        context: np.ndarray,
        nodata: float | None,
        context_transform: Affine,
        crs: rasterio.crs.CRS,
        chip_dir: Path,
        backend: dict[str, Any],
    ) -> tuple[dict[str, np.ndarray], dict[str, float], dict[str, Any]]:
        outputs: dict[str, np.ndarray] = {}
        runtimes: dict[str, float] = {}
        backend_executions: dict[str, Any] = {}
        halo = EXPERIMENT_FILTER_HALO_PIXELS
        core_slice = np.s_[halo:-halo, halo:-halo]
        outputs["RAW"] = context[core_slice].astype(np.float32, copy=True)
        runtimes["RAW"] = 0.0
        for configuration in EXPERIMENT_GAUSSIAN_CONFIGS:
            candidate_id = str(configuration["id"])
            started = time.perf_counter()
            filtered = gaussian_smoothing(context, float(configuration["sigma_pixels"]), nodata)
            outputs[candidate_id] = filtered[core_slice]
            runtimes[candidate_id] = time.perf_counter() - started
        for configuration in EXPERIMENT_BILATERAL_CONFIGS:
            candidate_id = str(configuration["id"])
            started = time.perf_counter()
            filtered = bilateral_smoothing(
                context,
                float(configuration["sigma_dist_pixels"]),
                float(configuration["sigma_int_m"]),
                nodata,
            )
            outputs[candidate_id] = filtered[core_slice]
            runtimes[candidate_id] = time.perf_counter() - started
        if backend["status"] == "available":
            backend_dir = chip_dir / "whitebox_backend"
            context_path = backend_dir / "context_with_halo.tif"
            write_float_raster(
                context_path,
                context,
                valid_mask(context, nodata),
                context_transform,
                crs,
            )
            for configuration in EXPERIMENT_FEATURE_PRESERVING_CONFIGS:
                candidate_id = str(configuration["id"])
                output_path = backend_dir / f"{candidate_id}.tif"
                execution = run_feature_preserving_smoothing(
                    backend,
                    context_path,
                    output_path,
                    configuration,
                )
                with rasterio.open(output_path, "r") as result:
                    if (
                        result.shape != context.shape
                        or result.crs != crs
                        or result.transform != context_transform
                        or result.res != (TARGET_RESOLUTION_M, TARGET_RESOLUTION_M)
                    ):
                        raise ValueError(f"WhiteboxTools output grid changed for {candidate_id}")
                    filtered = result.read(1)
                outputs[candidate_id] = filtered[core_slice].astype(np.float32)
                runtimes[candidate_id] = execution["elapsed_seconds"]
                backend_executions[candidate_id] = execution
        return outputs, runtimes, backend_executions

    def _run_chip(self, chip: ChipWindow, backend: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        chip_dir = self.output_dir / "chips" / chip.chip_id
        with rasterio.open(self.baseline_path, "r") as dataset:
            context = self._read_chip_context(dataset, chip)
            transform = window_transform(chip.window, dataset.transform)
            halo = EXPERIMENT_FILTER_HALO_PIXELS
            context_window = Window(
                chip.column_offset - halo,
                chip.row_offset - halo,
                chip.width + 2 * halo,
                chip.height + 2 * halo,
            )
            context_transform = window_transform(context_window, dataset.transform)
            crs = dataset.crs
            nodata = dataset.nodata
        candidates, runtimes, backend_executions = self._condition_candidates(
            context,
            nodata,
            context_transform,
            crs,
            chip_dir,
            backend,
        )
        raw = candidates["RAW"]
        inventory = self._inventory(chip, raw, nodata)
        results: dict[str, Any] = {}
        hillshade_panels: list[tuple[str, np.ndarray, np.ndarray]] = []
        slope_panels: list[tuple[str, np.ndarray, np.ndarray]] = []
        difference_panels: list[tuple[str, np.ndarray, np.ndarray]] = []
        slope_visual_maximum = 0.0
        difference_visual_maximum = 0.0

        for candidate_id, elevation in candidates.items():
            candidate_started = time.perf_counter()
            metrics, slope, slope_valid = experimental_metrics(raw, elevation, TARGET_RESOLUTION_M, nodata)
            shade, shade_valid = hillshade(elevation, TARGET_RESOLUTION_M, nodata)
            neighbor, neighbor_valid = local_neighbor_magnitude(elevation, nodata)
            elevation_valid = valid_mask(elevation, nodata)
            difference_valid = elevation_valid & valid_mask(raw, nodata)
            difference = elevation.astype(np.float64) - raw.astype(np.float64)
            candidate_dir = chip_dir / candidate_id
            artifacts = {
                "dem": str(write_float_raster(candidate_dir / "dem.tif", elevation, elevation_valid, transform, crs)),
                "hillshade": str(
                    write_float_raster(candidate_dir / "hillshade.tif", shade, shade_valid, transform, crs)
                ),
                "slope_horn_degrees": str(
                    write_float_raster(
                        candidate_dir / "slope_horn_degrees.tif",
                        slope,
                        slope_valid,
                        transform,
                        crs,
                    )
                ),
                "neighbor_magnitude": str(
                    write_float_raster(
                        candidate_dir / "neighbor_magnitude.tif",
                        neighbor,
                        neighbor_valid,
                        transform,
                        crs,
                    )
                ),
                "difference_from_raw": str(
                    write_float_raster(
                        candidate_dir / "difference_from_raw.tif",
                        difference,
                        difference_valid,
                        transform,
                        crs,
                    )
                ),
            }
            results[candidate_id] = {
                "status": "executed",
                "conditioning_seconds": runtimes[candidate_id],
                "backend_execution": backend_executions.get(candidate_id),
                "total_metrics_and_artifacts_seconds": time.perf_counter() - candidate_started,
                "metrics": metrics,
                "artifacts": artifacts,
            }
            hillshade_panels.append((candidate_id, shade, shade_valid))
            slope_panels.append((candidate_id, slope, slope_valid))
            difference_panels.append((candidate_id, difference, difference_valid))
            slope_visual_maximum = max(
                slope_visual_maximum,
                float(np.percentile(slope[slope_valid], 99)),
            )
            difference_visual_maximum = max(
                difference_visual_maximum,
                float(np.percentile(np.abs(difference[difference_valid]), 99)),
            )

        if backend["status"] != "available":
            for configuration in EXPERIMENT_FEATURE_PRESERVING_CONFIGS:
                candidate_id = str(configuration["id"])
                results[candidate_id] = {
                    "status": "unavailable",
                    "configuration": configuration,
                    "backend": backend,
                    "metrics": None,
                    "artifacts": {},
                }

        visual_dir = chip_dir / "comparisons"
        compositions = {
            "hillshade": write_comparison_png(
                visual_dir / "hillshade.png",
                hillshade_panels,
                0.0,
                255.0,
            ),
            "slope_horn_degrees": write_comparison_png(
                visual_dir / "slope_horn_degrees.png",
                slope_panels,
                0.0,
                slope_visual_maximum,
            ),
            "difference_from_raw": write_comparison_png(
                visual_dir / "difference_from_raw.png",
                difference_panels,
                -difference_visual_maximum,
                difference_visual_maximum,
            ),
        }
        for composition in compositions.values():
            composition["shared_range_strategy"] = "maximum panel p99; values beyond the common range are clipped"
        return inventory, {
            "candidate_order": ["RAW", "A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"],
            "results": results,
            "visual_compositions": compositions,
            "feature_preserving_status": backend["status"],
            "winner_selected": False,
        }
