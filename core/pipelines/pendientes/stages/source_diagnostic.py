from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import bounds as window_bounds, from_bounds

from core.pipelines.pendientes.constants import (
    ANALYTIC_DEM_FILENAME,
    BANDING_REVIEW_DIRECTORY_NAME,
    BANDING_REVIEW_MANIFEST_FILENAME,
    CALIBRATION_DIRECTORY_NAME,
    CALIBRATION_MANIFEST_FILENAME,
    EXPERIMENT_BASELINE_SHA256,
    FINAL_NODATA,
    PIPELINE_NAME,
    PIPELINE_VERSION,
    SOURCE_DIAGNOSTIC_DIRECTORY_NAME,
    SOURCE_DIAGNOSTIC_EVIDENCE_LABELS,
    SOURCE_DIAGNOSTIC_MANIFEST_FILENAME,
    SOURCE_DIAGNOSTIC_PROFILE_ANGLE_DEGREES,
    SOURCE_DIAGNOSTIC_PROFILE_OFFSETS_PIXELS,
    SOURCE_EXPECTED_DTYPE,
    SOURCE_EXPECTED_NODATA,
    SOURCE_EXPECTED_RESOLUTION_DEGREES,
    TARGET_RESOLUTION_M,
    TARGET_SRID,
)
from core.pipelines.pendientes.helpers.experimental_artifacts import write_float_raster
from core.pipelines.pendientes.helpers.source_diagnostics import (
    elevation_distribution,
    equivalent_native_window,
    metric_derivatives,
    native_neighbor_differences,
    profile_coordinates,
    profile_step_summary,
    quantization_summary,
    sample_profile,
    spatial_difference_metrics,
    warp_native_to_grid,
    write_diagnostic_composition,
    write_native_raster,
    write_profile_comparison,
    write_profile_csv,
)
from core.utils.files import read_json, sha256_file, write_json_atomic


class PendientesSourceDiagnostic:
    """Separate published-source, ETL-reprojection and terrain-derivative evidence."""

    def __init__(self) -> None:
        self.extract_manifest_path = Path("data/extract/pendientes/manifest.json")
        self.transform_dir = Path("data") / "transform" / PIPELINE_NAME
        self.baseline_path = self.transform_dir / ANALYTIC_DEM_FILENAME
        self.calibration_manifest_path = (
            self.transform_dir / CALIBRATION_DIRECTORY_NAME / CALIBRATION_MANIFEST_FILENAME
        )
        self.banding_manifest_path = (
            self.transform_dir / BANDING_REVIEW_DIRECTORY_NAME / BANDING_REVIEW_MANIFEST_FILENAME
        )
        self.output_dir = self.transform_dir / SOURCE_DIAGNOSTIC_DIRECTORY_NAME
        self.manifest_path = self.output_dir / SOURCE_DIAGNOSTIC_MANIFEST_FILENAME

    def execute(self) -> dict[str, Any]:
        started = time.perf_counter()
        source_path, source_manifest, calibration_manifest = self._validate_inputs()
        sites = self._site_contracts(calibration_manifest)
        results: dict[str, Any] = {}
        with rasterio.open(source_path) as source, rasterio.open(self.baseline_path) as baseline:
            self._validate_rasters(source, baseline)
            for site in sites:
                results[site["site_id"]] = self._diagnose_site(source, baseline, site)

        evidence = self._classify_evidence(results)
        focal_comparison = self._focal_fp_comparison(calibration_manifest) if evidence["source_signal_present"] else None
        manifest = {
            "phase": "5C_source_reprojection_derivative_diagnostic",
            "pipeline_version": PIPELINE_VERSION,
            "created_at": datetime.now().astimezone().isoformat(),
            "status": "completed_diagnostic_not_promoted",
            "inputs": {
                "source_path": str(source_path),
                "source_sha256": source_manifest["tiff_sha256"],
                "source_manifest_path": str(self.extract_manifest_path),
                "source_manifest_sha256": sha256_file(self.extract_manifest_path),
                "baseline_path": str(self.baseline_path),
                "baseline_sha256": sha256_file(self.baseline_path),
                "calibration_manifest_path": str(self.calibration_manifest_path),
                "calibration_manifest_sha256": sha256_file(self.calibration_manifest_path),
            },
            "site_count": len(sites),
            "sites": results,
            "evidence": evidence,
            "phase5b_methodological_status": {
                "status": "superseded_for_binary_localization",
                "reason": (
                    "Visual review indicates a pervasive pattern; Phase 5B remains useful for characterization "
                    "but not for a localized present/absent mask."
                ),
                "existing_manifest_preserved": True,
                "manifest_path": str(self.banding_manifest_path),
                "manifest_sha256": sha256_file(self.banding_manifest_path),
            },
            "focal_fp1_fp2_fp3": focal_comparison,
            "methodological_implication": {
                "recommendation": "reconsider_light_global_conditioning_before_any_adaptive_mask",
                "raw_remains_reference": True,
                "no_method_promoted": True,
                "rationale": (
                    "The published native DEM must remain the evidential reference. Any conditioning should "
                    "reduce systematic derivative expression while preserving real geomorphology."
                ),
            },
            "prohibited_actions_confirmed": {
                "detector_trained": False,
                "chips_bulk_labeled": False,
                "adaptive_mask_generated": False,
                "statewide_fp3_executed": False,
                "conditioned_dem_generated": False,
                "institutional_slopes_generated": False,
                "load_executed": False,
                "dag_created": False,
            },
            "elapsed_seconds": time.perf_counter() - started,
        }
        write_json_atomic(manifest, self.manifest_path)
        return manifest

    def _validate_inputs(self) -> tuple[Path, dict[str, Any], dict[str, Any]]:
        source_manifest = read_json(self.extract_manifest_path)
        calibration_manifest = read_json(self.calibration_manifest_path)
        banding_manifest = read_json(self.banding_manifest_path)
        if source_manifest is None or calibration_manifest is None or banding_manifest is None:
            raise FileNotFoundError("Extract, Phase-4B and Phase-5B manifests are required")
        source_path = Path(source_manifest["tiff_path"])
        if not source_path.is_file():
            raise FileNotFoundError(f"Native CEM is missing: {source_path}")
        if sha256_file(source_path) != source_manifest["tiff_sha256"]:
            raise ValueError("Native source checksum changed")
        if sha256_file(self.baseline_path) != EXPERIMENT_BASELINE_SHA256:
            raise ValueError("Baseline checksum changed")
        return source_path, source_manifest, calibration_manifest

    def _validate_rasters(
        self,
        source: rasterio.io.DatasetReader,
        baseline: rasterio.io.DatasetReader,
    ) -> None:
        if source.crs is None or source.crs.to_epsg() != 6365:
            raise ValueError("Native source must use EPSG:6365")
        if source.dtypes != (SOURCE_EXPECTED_DTYPE.lower(),) or source.nodata != SOURCE_EXPECTED_NODATA:
            raise ValueError("Native source datatype or NoData changed")
        if not np.allclose(
            [abs(source.transform.a), abs(source.transform.e)],
            SOURCE_EXPECTED_RESOLUTION_DEGREES,
            atol=1e-10,
            rtol=0,
        ):
            raise ValueError("Native source resolution changed")
        if baseline.crs is None or baseline.crs.to_epsg() != TARGET_SRID:
            raise ValueError("Baseline must use EPSG:6368")
        if baseline.dtypes != ("float32",) or baseline.nodata != FINAL_NODATA:
            raise ValueError("Baseline datatype or NoData changed")
        if not np.allclose([abs(baseline.transform.a), abs(baseline.transform.e)], TARGET_RESOLUTION_M):
            raise ValueError("Baseline resolution changed")

    def _site_contracts(self, calibration_manifest: dict[str, Any]) -> list[dict[str, Any]]:
        controls = {item["chip_id"]: item for item in calibration_manifest["controls"]}
        manual = calibration_manifest["manual_problem_coordinate"]["chip"]
        if float(manual["center_x"]) != 750968.0 or float(manual["center_y"]) != 2329434.0:
            raise ValueError("Mandatory manual coordinate changed")
        return [
            {"site_id": "problema_manual", "role": "known_pattern", **manual},
            {"site_id": "plano", "role": "low_relief_control", **controls["plano"]},
            {"site_id": "montana", "role": "mountain_control", **controls["montana"]},
        ]

    def _diagnose_site(
        self,
        source: rasterio.io.DatasetReader,
        baseline: rasterio.io.DatasetReader,
        site: dict[str, Any],
    ) -> dict[str, Any]:
        site_dir = self.output_dir / "sites" / site["site_id"]
        requested_bounds = tuple(float(value) for value in site["bbox"])
        baseline_window = from_bounds(*requested_bounds, transform=baseline.transform).round_offsets().round_lengths()
        baseline_values = baseline.read(1, window=baseline_window)
        baseline_transform = baseline.window_transform(baseline_window)
        baseline_bounds = tuple(float(value) for value in window_bounds(baseline_window, baseline.transform))
        native_window, native_bounds = equivalent_native_window(source, baseline_bounds, baseline.crs)
        native_values = source.read(1, window=native_window)
        native_transform = source.window_transform(native_window)

        native_path = write_native_raster(
            site_dir / "source_native_epsg6365.tif",
            native_values,
            native_transform,
            source.crs,
        )
        baseline_valid = np.isfinite(baseline_values) & (baseline_values != FINAL_NODATA)
        baseline_path = write_float_raster(
            site_dir / "baseline_epsg6368.tif",
            baseline_values,
            baseline_valid,
            baseline_transform,
            baseline.crs,
        )
        source_nearest = warp_native_to_grid(
            native_values,
            native_transform,
            source.crs,
            baseline_values.shape,
            baseline_transform,
            baseline.crs,
            Resampling.nearest,
        )
        source_bilinear = warp_native_to_grid(
            native_values,
            native_transform,
            source.crs,
            baseline_values.shape,
            baseline_transform,
            baseline.crs,
            Resampling.bilinear,
        )
        nearest_valid = source_nearest != FINAL_NODATA
        nearest_path = write_float_raster(
            site_dir / "source_native_nearest_common_grid.tif",
            source_nearest,
            nearest_valid,
            baseline_transform,
            baseline.crs,
        )
        source_derivatives = metric_derivatives(source_nearest, TARGET_RESOLUTION_M, FINAL_NODATA)
        baseline_derivatives = metric_derivatives(baseline_values, TARGET_RESOLUTION_M, FINAL_NODATA)
        derivative_metrics = self._derivative_metrics(source_derivatives, baseline_derivatives)
        composition = write_diagnostic_composition(
            site_dir / "source_baseline_derivatives.png",
            source_nearest,
            baseline_values,
            source_derivatives,
            baseline_derivatives,
        )
        profiles = self._profiles(
            site_dir,
            site,
            native_values,
            native_transform,
            source.crs,
            baseline_values,
            baseline_transform,
            baseline.crs,
        )
        return {
            "site": {
                "site_id": site["site_id"],
                "role": site["role"],
                "center_epsg6368": [float(site["center_x"]), float(site["center_y"])],
            },
            "native_window": {
                "path": str(native_path),
                "sha256": sha256_file(native_path),
                "bbox_epsg6365": list(native_bounds),
                "kernel_margin_pixels": 2,
                "footprint_role": "equivalent target footprint plus two native pixels for resampling support",
                "dimensions": [int(native_values.shape[1]), int(native_values.shape[0])],
                "resolution_degrees": [abs(native_transform.a), abs(native_transform.e)],
                "dtype": str(native_values.dtype),
                "nodata": source.nodata,
                "elevation": elevation_distribution(native_values, source.nodata),
                "quantization": quantization_summary(native_values, source.nodata),
                "neighbor_differences": native_neighbor_differences(native_values, source.nodata),
            },
            "baseline_window": {
                "path": str(baseline_path),
                "sha256": sha256_file(baseline_path),
                "bbox_epsg6368": list(baseline_bounds),
                "dimensions": [int(baseline_values.shape[1]), int(baseline_values.shape[0])],
                "resolution_m": [abs(baseline_transform.a), abs(baseline_transform.e)],
                "dtype": str(baseline_values.dtype),
                "nodata": baseline.nodata,
                "elevation": elevation_distribution(baseline_values, baseline.nodata),
            },
            "spatial_comparison": {
                "reference": "native CEM sampled by nearest neighbour at EPSG:6368 baseline cell centres",
                "comparison": "existing EPSG:6368 / 15 m bilinear baseline",
                "direct_cross_grid_index_comparison": False,
                "nearest_reference_path": str(nearest_path),
                "nearest_reference_sha256": sha256_file(nearest_path),
                "baseline_minus_nearest_native": spatial_difference_metrics(source_nearest, baseline_values),
                "local_bilinear_qa_warp_minus_existing_baseline": spatial_difference_metrics(
                    source_bilinear,
                    baseline_values,
                ),
                "local_bilinear_qa_note": (
                    "This auxiliary chip-local warp is not treated as an exact reconstruction of the original "
                    "full-raster warp because GDAL transformation context can differ by warp extent."
                ),
            },
            "derivatives": {
                "metric_grid": "EPSG:6368 / 15 m",
                "native_copy_resampling": "nearest; preserves native whole-metre levels for derivative diagnosis",
                "source_native_file_overwritten": False,
                "hillshade": {"azimuth_degrees": 315.0, "altitude_degrees": 45.0},
                **derivative_metrics,
            },
            "profiles": profiles,
            "visualization": {
                "path": str(composition),
                "sha256": sha256_file(composition),
                "common_ranges_within_site": True,
                "independent_pair_autoscaling": False,
            },
        }

    def _derivative_metrics(
        self,
        source: dict[str, Any],
        baseline: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "slope_degrees": {
                "source": elevation_distribution(source["slope"], None),
                "baseline": elevation_distribution(baseline["slope"], None),
                "baseline_minus_source": spatial_difference_metrics(source["slope"], baseline["slope"], None),
            },
            "hillshade_0_255": {
                "source": elevation_distribution(source["hillshade"], None),
                "baseline": elevation_distribution(baseline["hillshade"], None),
                "baseline_minus_source": spatial_difference_metrics(
                    source["hillshade"],
                    baseline["hillshade"],
                    None,
                ),
            },
            "second_difference_magnitude_m": {
                "source": elevation_distribution(source["second_difference"], None),
                "baseline": elevation_distribution(baseline["second_difference"], None),
                "baseline_minus_source": spatial_difference_metrics(
                    source["second_difference"],
                    baseline["second_difference"],
                    None,
                ),
            },
        }

    def _profiles(
        self,
        site_dir: Path,
        site: dict[str, Any],
        native_values: np.ndarray,
        native_transform: rasterio.Affine,
        native_crs: rasterio.crs.CRS,
        baseline_values: np.ndarray,
        baseline_transform: rasterio.Affine,
        baseline_crs: rasterio.crs.CRS,
    ) -> dict[str, Any]:
        profile_records = []
        profile_contracts = []
        for index, offset_pixels in enumerate(SOURCE_DIAGNOSTIC_PROFILE_OFFSETS_PIXELS, start=1):
            distance, x, y = profile_coordinates(
                float(site["center_x"]),
                float(site["center_y"]),
                12_000.0,
                TARGET_RESOLUTION_M,
                SOURCE_DIAGNOSTIC_PROFILE_ANGLE_DEGREES,
                offset_pixels * TARGET_RESOLUTION_M,
            )
            records = sample_profile(
                distance,
                x,
                y,
                baseline_crs,
                native_values,
                native_transform,
                native_crs,
                baseline_values,
                baseline_transform,
            )
            csv_path = write_profile_csv(site_dir / "profiles" / f"transecto_{index}.csv", records)
            profile_records.append(records)
            profile_contracts.append(
                {
                    "profile_id": f"transecto_{index}",
                    "path": str(csv_path),
                    "sha256": sha256_file(csv_path),
                    "tangent_offset_pixels": offset_pixels,
                    "summary": profile_step_summary(records),
                }
            )
        comparison = write_profile_comparison(site_dir / "profiles" / "profiles_comparativos.png", profile_records)
        return {
            "orientation_degrees_from_easting": SOURCE_DIAGNOSTIC_PROFILE_ANGLE_DEGREES,
            "orientation_source": "Phase-5B dominant normal at problema_manual, frozen for all comparable sites",
            "sampling": "geographic coordinates transformed to each grid; no pixel-index pairing",
            "transects": profile_contracts,
            "comparison_path": str(comparison),
            "comparison_sha256": sha256_file(comparison),
        }

    def _classify_evidence(self, results: dict[str, Any]) -> dict[str, Any]:
        manual = results["problema_manual"]
        quantization = manual["native_window"]["quantization"]
        summaries = [item["summary"] for item in manual["profiles"]["transects"]]
        alternating = sum(item["alternating_plateau_step_sequences"] for item in summaries)
        plateau_percentage = float(np.mean([item["plateau_transition_percentage"] for item in summaries]))
        source_signal_present = (
            quantization["integer_value_percentage"] == 100.0 and alternating >= 6 and plateau_percentage >= 5.0
        )
        source_p95 = manual["derivatives"]["second_difference_magnitude_m"]["source"]["percentiles"]["p95"]
        baseline_p95 = manual["derivatives"]["second_difference_magnitude_m"]["baseline"]["percentiles"]["p95"]
        amplified_by_reprojection = baseline_p95 > source_p95 * 1.1
        if source_signal_present:
            categories = ["principalmente_presente_en_fuente"]
            if amplified_by_reprojection:
                categories.append("amplificado_por_reproyeccion")
        elif amplified_by_reprojection:
            categories = ["principalmente_inducido_por_reproyeccion"]
        else:
            categories = ["indeterminado"]
        if not set(categories).issubset(SOURCE_DIAGNOSTIC_EVIDENCE_LABELS):
            raise ValueError("Unsupported diagnostic evidence label")
        return {
            "categories": categories,
            "source_signal_present": source_signal_present,
            "manual_profile_alternating_plateau_step_sequences": alternating,
            "manual_profile_mean_plateau_percentage": plateau_percentage,
            "reprojection_amplifies_second_difference_p95": amplified_by_reprojection,
            "second_difference_p95_ratio_baseline_to_native_nearest": float(baseline_p95 / source_p95),
            "morphometric_derivatives_amplify_visibility": True,
            "institutional_resampling_separable_from_published_source": False,
            "interpretation": (
                "Quantization and any INEGI production resampling are already embedded in the published CEM. "
                "The ETL reprojection effect is evaluated separately against nearest sampling on a common grid; "
                "terrain derivatives can make weak source structure visually prominent without proving invalidity."
            ),
        }

    def _focal_fp_comparison(self, calibration_manifest: dict[str, Any]) -> dict[str, Any]:
        candidates = calibration_manifest["results"]["problema_manual"]["candidates"]
        summary = {}
        for candidate_id in ("RAW", "FP1", "FP2", "FP3"):
            candidate = candidates[candidate_id]
            metrics = candidate["metrics"]
            dem_path = Path(candidate["artifacts"]["dem"])
            summary[candidate_id] = {
                "dem_path": str(dem_path),
                "dem_sha256": sha256_file(dem_path),
                "reused_phase4b_artifact": True,
                "elevation_mae_m": metrics["elevation"]["mae_m"],
                "elevation_rmse_m": metrics["elevation"]["rmse_m"],
                "slope_difference_mae_degrees": metrics["slope_horn_degrees"]["difference_from_raw_degrees"]["mae"],
                "second_derivative_mean_m": metrics["absolute_laplacian_m"]["mean"],
                "second_derivative_p95_m": metrics["absolute_laplacian_m"]["p95"],
                "directed_high_second_difference_percentage": candidate["directed_banding"][
                    "high_second_difference_percentage"
                ],
                "previous_experimental_classification": candidate.get("classification"),
            }
        return {
            "executed_new_filters": False,
            "scope": "existing Phase-4B problema_manual artifacts only",
            "candidates": summary,
            "purpose": "compare derivative-expression reduction against geomorphological alteration; no promotion",
        }
