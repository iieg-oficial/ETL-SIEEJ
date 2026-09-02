from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from affine import Affine
from rasterio.windows import Window, transform as window_transform

from core.pipelines.pendientes.constants import (
    DEM_PROMOTION_DIRECTORY_NAME,
    DEM_PROMOTION_MANIFEST_FILENAME,
    PIPELINE_NAME,
    PIPELINE_VERSION,
    SLOPE_SELECTION_ALGORITHMS,
    SLOPE_SELECTION_CONTEXT_PIXELS,
    SLOPE_SELECTION_DECISIONS,
    SLOPE_SELECTION_DIRECTORY_NAME,
    SLOPE_SELECTION_MANIFEST_FILENAME,
    SLOPE_SELECTION_PARENT_MANIFEST_SHA256,
    STATE_VALIDATION_DIRECTORY_NAME,
    STATE_VALIDATION_INVENTORY_FILENAME,
    STATEWIDE_CANDIDATE_DIRECTORY_NAME,
    STATEWIDE_CANDIDATE_FILENAME,
    STATEWIDE_CANDIDATE_SHA256,
)
from core.pipelines.pendientes.helpers.methodology.slope_selection import (
    contextual_chip_window,
    difference_metrics,
    distribution,
    inspect_gdaldem_backend,
    planar_error_metrics,
    planar_surface,
    roughness_difference_relationship,
    run_gdaldem_slope,
    slope_class_distribution,
    stability_metrics,
    synthetic_geomorphic_surfaces,
    write_comparison_figure,
    write_profile_figure,
    write_single_band_raster,
)
from core.utils.files import read_json, sha256_file, write_json_atomic


class PendientesSlopeAlgorithmValidation:
    """Compare only Horn and Zevenbergen–Thorne before statewide slope production."""

    def __init__(self) -> None:
        transform_dir = Path("data") / "transform" / PIPELINE_NAME
        self.context_path = transform_dir / STATEWIDE_CANDIDATE_DIRECTORY_NAME / STATEWIDE_CANDIDATE_FILENAME
        self.inventory_path = transform_dir / STATE_VALIDATION_DIRECTORY_NAME / STATE_VALIDATION_INVENTORY_FILENAME
        self.parent_manifest_path = transform_dir / DEM_PROMOTION_DIRECTORY_NAME / DEM_PROMOTION_MANIFEST_FILENAME
        self.output_dir = transform_dir / SLOPE_SELECTION_DIRECTORY_NAME
        self.manifest_path = self.output_dir / SLOPE_SELECTION_MANIFEST_FILENAME

    def execute(self) -> dict[str, Any]:
        started = time.perf_counter()
        inventory, parent_manifest = self._validate_inputs()
        backend = inspect_gdaldem_backend()
        planar = self._run_planar_synthetics(backend)
        geomorphic = self._run_geomorphic_synthetics(backend)
        real_results = self._run_real_chips(inventory, backend)
        by_morphology = self._aggregate_by_morphology(real_results)
        aggregate = self._aggregate_chips(list(real_results.values()))
        selected_visuals = self._visual_chip_ids(inventory)
        visualizations = self._write_visualizations(real_results, selected_visuals)
        profile_ids = [
            "problema_manual",
            *[
                chip["chip_id"]
                for chip in inventory["chips"]
                if chip["morphology_class"] == "plano" and chip["chip_id"] != "problema_manual"
            ][:3],
        ]
        profiles = self._write_profiles(real_results, profile_ids)
        residual = {
            chip_id: {
                algorithm: real_results[chip_id]["algorithms"][algorithm]["stability"]
                for algorithm in SLOPE_SELECTION_ALGORITHMS
            }
            for chip_id in profile_ids
        }
        pareto = self._pareto(planar, geomorphic, real_results, by_morphology)
        manifest = {
            "phase": "7A_slope_algorithm_selection_Horn_vs_ZevenbergenThorne",
            "pipeline_version": PIPELINE_VERSION,
            "created_at": datetime.now().astimezone().isoformat(),
            "status": "completed_pending_methodological_decision",
            "inputs": {
                "validated_context_dem_path": str(self.context_path),
                "validated_context_dem_sha256": STATEWIDE_CANDIDATE_SHA256,
                "phase6b_manifest_path": str(self.parent_manifest_path),
                "phase6b_manifest_sha256": SLOPE_SELECTION_PARENT_MANIFEST_SHA256,
                "phase6b_status": parent_manifest["status"],
                "master_territorial_grid": parent_manifest["master_grid"],
                "territorial_dem_used_as_slope_parent": False,
            },
            "backend": backend,
            "mathematical_contract": self._mathematical_contract(),
            "synthetic_planar_validation": planar,
            "synthetic_geomorphic_comparison": geomorphic,
            "sample": {
                "chip_count": len(real_results),
                "source": "same 30 Phase-5A windows extracted from validated_context_dem",
                "context_margin_pixels": SLOPE_SELECTION_CONTEXT_PIXELS,
                "old_banding_classes_used": False,
            },
            "real_chip_results": real_results,
            "aggregate_all_chips": aggregate,
            "aggregate_by_morphology": by_morphology,
            "residual_discretization_review": {
                "chip_ids": profile_ids,
                "stability": residual,
                "profiles": profiles,
                "interpretation_scope": "comparative stability only; no independent ground truth",
            },
            "visual_review": {
                "chip_ids": selected_visuals,
                "compositions": visualizations,
                "panel_order": ["DEM", "Horn", "ZevenbergenThorne", "ZT_minus_Horn"],
                "common_scales_across_compositions": True,
                "human_review_completed": False,
            },
            "pareto": pareto,
            "decision": {
                "allowed": list(SLOPE_SELECTION_DECISIONS),
                "value": None,
                "status": "awaiting_metric_and_visual_review",
            },
            "next_phase_contract": None,
            "statewide_slopes_generated": False,
            "percentage_slope_generated": False,
            "elapsed_seconds": time.perf_counter() - started,
        }
        write_json_atomic(manifest, self.manifest_path)
        return manifest

    def record_decision(
        self,
        decision: str,
        evidence: dict[str, Any],
    ) -> dict[str, Any]:
        if decision not in SLOPE_SELECTION_DECISIONS:
            raise ValueError(f"Unsupported slope selection decision: {decision}")
        manifest = read_json(self.manifest_path)
        if manifest is None or manifest["status"] != "completed_pending_methodological_decision":
            raise ValueError("Completed Phase-7A evidence is required")
        recommended = (
            decision.removesuffix("_recomendado_para_produccion")
            if decision != "requiere_revision_metodologica"
            else None
        )
        contract = None
        if recommended is not None:
            contract = {
                "selected_slope_algorithm": recommended,
                "backend": manifest["backend"],
                "parameters": {
                    "output_unit": "degree",
                    "scale_xy_to_z": 1.0,
                    "effective_z_factor": 1.0,
                    "compute_edges": False,
                },
                "parent_context_dem_sha256": STATEWIDE_CANDIDATE_SHA256,
                "master_territorial_grid": manifest["inputs"]["master_territorial_grid"],
                "percentage_derivation": "tan(radians(degrees)) * 100; values are not capped at 100",
                "required_workflow": [
                    "slope from validated context DEM",
                    "territorial window",
                    "Jalisco master mask",
                ],
            }
        manifest["decision"] = {
            "allowed": list(SLOPE_SELECTION_DECISIONS),
            "value": decision,
            "status": "reviewed_for_next_statewide_production_only",
            "evidence": evidence,
            "reviewed_at": datetime.now().astimezone().isoformat(),
            "promoted": False,
            "published": False,
        }
        manifest["next_phase_contract"] = contract
        manifest["visual_review"]["human_review_completed"] = True
        manifest["status"] = (
            "completed_algorithm_recommended_for_production" if contract else "completed_requires_review"
        )
        write_json_atomic(manifest, self.manifest_path)
        return manifest

    def _validate_inputs(self) -> tuple[dict[str, Any], dict[str, Any]]:
        if sha256_file(self.context_path) != STATEWIDE_CANDIDATE_SHA256:
            raise ValueError("Validated context DEM checksum changed")
        if sha256_file(self.parent_manifest_path) != SLOPE_SELECTION_PARENT_MANIFEST_SHA256:
            raise ValueError("Phase-6B manifest checksum changed")
        inventory = read_json(self.inventory_path)
        parent = read_json(self.parent_manifest_path)
        if inventory is None or parent is None:
            raise FileNotFoundError("Phase-5A inventory and Phase-6B manifest are required")
        if inventory["chip_count"] != 30 or len(inventory["chips"]) != 30:
            raise ValueError("Phase 7A requires exactly the 30 frozen chips")
        if parent["status"] != "conditioned_dem_validated_for_derivatives":
            raise ValueError("Conditioned DEM is not validated for derivatives")
        if parent["derivative_contract"]["slope_parent"] != "validated_context_dem":
            raise ValueError("Phase-6B slope parent contract changed")
        return inventory, parent

    def _run_planar_synthetics(self, backend: dict[str, Any]) -> dict[str, Any]:
        cases = [("horizontal", 0.0, 0.0)]
        for slope in (1.0, 5.0, 15.0, 30.0, 45.0):
            cases.extend(((f"x_{slope:g}", slope, 0.0), (f"y_{slope:g}", slope, 90.0)))
        for direction in (45.0, 135.0):
            for slope in (1.0, 5.0, 15.0, 30.0, 45.0):
                cases.append((f"diagonal_{direction:g}_{slope:g}", slope, direction))
        for direction in (22.5, 67.5):
            for slope in (5.0, 15.0, 30.0):
                cases.append((f"azimuth_{direction:g}_{slope:g}", slope, direction))
        results = {}
        transform = Affine(15, 0, 0, 0, -15, 65 * 15)
        for case_id, expected, direction in cases:
            directory = self.output_dir / "synthetic" / "planes" / case_id
            dem_path = write_single_band_raster(
                directory / "dem.tif",
                planar_surface(65, 15.0, expected, direction),
                transform,
                "EPSG:6368",
                "metre",
            )
            algorithms = {}
            for algorithm in SLOPE_SELECTION_ALGORITHMS:
                output_path = directory / f"{algorithm}.tif"
                execution = run_gdaldem_slope(backend, dem_path, output_path, algorithm)
                with rasterio.open(output_path) as dataset:
                    values = dataset.read(1)
                algorithms[algorithm] = {
                    "error": planar_error_metrics(values, expected),
                    "execution_seconds": execution["elapsed_seconds"],
                    "artifact_sha256": sha256_file(output_path),
                }
            results[case_id] = {
                "expected_slope_degrees": expected,
                "gradient_direction_degrees": direction,
                "algorithms": algorithms,
            }
        aggregate = {
            algorithm: {
                metric: float(
                    max(result["algorithms"][algorithm]["error"][metric] for result in results.values())
                    if metric == "max_error_degrees"
                    else np.mean([result["algorithms"][algorithm]["error"][metric] for result in results.values()])
                )
                for metric in ("bias_degrees", "mae_degrees", "rmse_degrees", "max_error_degrees")
            }
            for algorithm in SLOPE_SELECTION_ALGORITHMS
        }
        return {
            "resolution_m": 15.0,
            "case_count": len(results),
            "cases": results,
            "aggregate": aggregate,
            "interior_only": True,
            "passed": all(item["max_error_degrees"] <= 1e-3 for item in aggregate.values()),
            "tolerance_degrees": 1e-3,
        }

    def _run_geomorphic_synthetics(self, backend: dict[str, Any]) -> dict[str, Any]:
        results = {}
        arrays = synthetic_geomorphic_surfaces()
        transform = Affine(15, 0, 0, 0, -15, 257 * 15)
        output_arrays = {}
        for case_id, elevation in arrays.items():
            directory = self.output_dir / "synthetic" / "geomorphic" / case_id
            dem_path = write_single_band_raster(directory / "dem.tif", elevation, transform, "EPSG:6368", "metre")
            algorithms = {}
            output_arrays[case_id] = {}
            for algorithm in SLOPE_SELECTION_ALGORITHMS:
                output_path = directory / f"{algorithm}.tif"
                run_gdaldem_slope(backend, dem_path, output_path, algorithm)
                with rasterio.open(output_path) as dataset:
                    values = dataset.read(1)
                output_arrays[case_id][algorithm] = values
                algorithms[algorithm] = {
                    "distribution": distribution(values),
                    "stability": stability_metrics(values),
                }
            results[case_id] = {
                "algorithms": algorithms,
                "difference": difference_metrics(
                    output_arrays[case_id]["Horn"], output_arrays[case_id]["ZevenbergenThorne"]
                ),
            }
        noise_sensitivity = {}
        for algorithm in SLOPE_SELECTION_ALGORITHMS:
            clean = output_arrays["tendencia_sin_ruido"][algorithm]
            noisy = output_arrays["tendencia_con_ruido"][algorithm]
            noise_sensitivity[algorithm] = difference_metrics(clean, noisy)
        return {
            "cases": results,
            "noise_sensitivity": noise_sensitivity,
            "interpretation_scope": "controlled differential response; non-planar cases have no claimed raster truth",
        }

    def _run_real_chips(
        self,
        inventory: dict[str, Any],
        backend: dict[str, Any],
    ) -> dict[str, Any]:
        results = {}
        margin = SLOPE_SELECTION_CONTEXT_PIXELS
        with rasterio.open(self.context_path) as source:
            for index, chip in enumerate(inventory["chips"], start=1):
                context_window = contextual_chip_window(chip, margin, source.shape)
                context = source.read(1, window=context_window)
                context_transform = window_transform(context_window, source.transform)
                chip_transform = window_transform(
                    Window(chip["column_offset"], chip["row_offset"], chip["width"], chip["height"]),
                    source.transform,
                )
                directory = self.output_dir / "chips" / chip["chip_id"]
                input_path = write_single_band_raster(
                    directory / "dem_context.tif",
                    context,
                    context_transform,
                    source.crs,
                    "metre",
                )
                dem = context[margin : margin + chip["height"], margin : margin + chip["width"]]
                algorithms = {}
                arrays = {}
                for algorithm in SLOPE_SELECTION_ALGORITHMS:
                    context_output = directory / f"{algorithm}_context.tif"
                    execution = run_gdaldem_slope(backend, input_path, context_output, algorithm)
                    with rasterio.open(context_output) as dataset:
                        context_slope = dataset.read(1)
                    values = context_slope[
                        margin : margin + chip["height"],
                        margin : margin + chip["width"],
                    ]
                    output_path = write_single_band_raster(
                        directory / f"{algorithm}.tif",
                        values,
                        chip_transform,
                        source.crs,
                        "degree",
                    )
                    arrays[algorithm] = values
                    algorithms[algorithm] = {
                        "artifact": {"path": str(output_path), "sha256": sha256_file(output_path)},
                        "distribution": distribution(values),
                        "classes_percentage": slope_class_distribution(values),
                        "stability": stability_metrics(values),
                        "execution_seconds": execution["elapsed_seconds"],
                    }
                results[chip["chip_id"]] = {
                    "chip": {
                        "chip_id": chip["chip_id"],
                        "morphology_class": chip["morphology_class"],
                        "bbox": chip["bbox"],
                        "context_margin_pixels": margin,
                        "artificial_chip_edge_pixels_evaluated": 0,
                    },
                    "dem_artifact": {"path": str(input_path), "sha256": sha256_file(input_path)},
                    "algorithms": algorithms,
                    "difference_ZT_minus_Horn": difference_metrics(arrays["Horn"], arrays["ZevenbergenThorne"]),
                    "roughness_relationship": roughness_difference_relationship(
                        dem,
                        arrays["Horn"],
                        arrays["ZevenbergenThorne"],
                        float(source.nodata),
                    ),
                }
                print(f"Phase 7A real chip {index}/{len(inventory['chips'])}", flush=True)
        return results

    def _aggregate_by_morphology(self, results: dict[str, Any]) -> dict[str, Any]:
        morphologies = sorted({item["chip"]["morphology_class"] for item in results.values()})
        return {
            morphology: self._aggregate_chips(
                [item for item in results.values() if item["chip"]["morphology_class"] == morphology]
            )
            for morphology in morphologies
        }

    def _aggregate_chips(self, items: list[dict[str, Any]]) -> dict[str, Any]:
        output: dict[str, Any] = {"chip_count": len(items), "algorithms": {}}
        for algorithm in SLOPE_SELECTION_ALGORITHMS:
            output["algorithms"][algorithm] = {
                "distribution_median_of_chips": {
                    key: float(np.median([item["algorithms"][algorithm]["distribution"][key] for item in items]))
                    for key in (
                        "minimum",
                        "mean",
                        "stddev",
                        "p01",
                        "p05",
                        "p25",
                        "p50",
                        "p75",
                        "p90",
                        "p95",
                        "p99",
                        "maximum",
                    )
                },
                "stability_median_of_chips": {
                    key: float(np.median([item["algorithms"][algorithm]["stability"][key] for item in items]))
                    for key in (
                        "neighbor_abs_difference_mean_degrees",
                        "neighbor_abs_difference_p95_degrees",
                        "neighbor_continuity_le_0.1_degrees_percentage",
                    )
                },
            }
        output["difference_ZT_minus_Horn_median_of_chips"] = {
            "bias_degrees": float(np.median([item["difference_ZT_minus_Horn"]["bias_degrees"] for item in items])),
            "mae_degrees": float(np.median([item["difference_ZT_minus_Horn"]["mae_degrees"] for item in items])),
            "rmse_degrees": float(np.median([item["difference_ZT_minus_Horn"]["rmse_degrees"] for item in items])),
            "p95_absolute_degrees": float(
                np.median([item["difference_ZT_minus_Horn"]["absolute_difference_degrees"]["p95"] for item in items])
            ),
            "p99_absolute_degrees": float(
                np.median([item["difference_ZT_minus_Horn"]["absolute_difference_degrees"]["p99"] for item in items])
            ),
            "maximum_absolute_degrees": float(
                max(item["difference_ZT_minus_Horn"]["absolute_difference_degrees"]["maximum"] for item in items)
            ),
            "threshold_percentages": {
                key: float(
                    np.median([item["difference_ZT_minus_Horn"]["threshold_percentages"][key] for item in items])
                )
                for key in next(iter(items))["difference_ZT_minus_Horn"]["threshold_percentages"]
            },
        }
        output["roughness_relationship_median_of_chips"] = {
            key: float(np.median([item["roughness_relationship"][key] for item in items]))
            for key in next(iter(items))["roughness_relationship"]
        }
        return output

    def _visual_chip_ids(self, inventory: dict[str, Any]) -> list[str]:
        groups = {
            morphology: sorted(chip["chip_id"] for chip in inventory["chips"] if chip["morphology_class"] == morphology)
            for morphology in ("plano", "valle", "lomerio", "montana", "transicion_valle_sierra")
        }
        selected = [
            "problema_manual",
            *[chip_id for chip_id in groups["plano"] if chip_id != "problema_manual"][:2],
            *groups["valle"][:2],
            *groups["lomerio"][:2],
            *groups["montana"][:2],
            *groups["transicion_valle_sierra"][:1],
        ]
        if len(selected) != 10 or len(set(selected)) != 10:
            raise ValueError("Visual selection must contain ten unique chips")
        return selected

    def _read_chip_arrays(self, result: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        with rasterio.open(result["dem_artifact"]["path"]) as dataset:
            context = dataset.read(1)
        margin = result["chip"]["context_margin_pixels"]
        dem = context[margin:-margin, margin:-margin]
        arrays = []
        for algorithm in SLOPE_SELECTION_ALGORITHMS:
            with rasterio.open(result["algorithms"][algorithm]["artifact"]["path"]) as dataset:
                arrays.append(dataset.read(1))
        return dem, arrays[0], arrays[1]

    def _write_visualizations(
        self,
        results: dict[str, Any],
        chip_ids: list[str],
    ) -> dict[str, Any]:
        slope_max = max(
            result["algorithms"][algorithm]["distribution"]["p99"]
            for result in results.values()
            for algorithm in SLOPE_SELECTION_ALGORITHMS
        )
        difference_limit = max(
            result["difference_ZT_minus_Horn"]["absolute_difference_degrees"]["p99"] for result in results.values()
        )
        output = {}
        for chip_id in chip_ids:
            dem, horn, zt = self._read_chip_arrays(results[chip_id])
            path = write_comparison_figure(
                self.output_dir / "visual" / f"{chip_id}.png",
                dem,
                horn,
                zt,
                slope_max,
                difference_limit,
            )
            output[chip_id] = {"path": str(path), "sha256": sha256_file(path)}
        return {
            "slope_display_range_degrees": [0.0, slope_max],
            "difference_display_range_degrees": [-difference_limit, difference_limit],
            "artifacts": output,
        }

    def _write_profiles(
        self,
        results: dict[str, Any],
        chip_ids: list[str],
    ) -> dict[str, Any]:
        output = {}
        for chip_id in chip_ids:
            dem, horn, zt = self._read_chip_arrays(results[chip_id])
            profile = write_profile_figure(
                self.output_dir / "profiles" / f"{chip_id}.png",
                dem,
                horn,
                zt,
            )
            profile["sha256"] = sha256_file(Path(profile["path"]))
            output[chip_id] = profile
        return output

    def _pareto(
        self,
        planar: dict[str, Any],
        geomorphic: dict[str, Any],
        real_results: dict[str, Any],
        by_morphology: dict[str, Any],
    ) -> dict[str, Any]:
        manual = real_results["problema_manual"]
        dimensions = {}
        for algorithm in SLOPE_SELECTION_ALGORITHMS:
            dimensions[algorithm] = {
                "synthetic_planar_max_error_degrees": planar["aggregate"][algorithm]["max_error_degrees"],
                "synthetic_noise_mae_degrees": geomorphic["noise_sensitivity"][algorithm]["mae_degrees"],
                "manual_neighbor_p95_degrees": manual["algorithms"][algorithm]["stability"][
                    "neighbor_abs_difference_p95_degrees"
                ],
                "flat_neighbor_p95_degrees": by_morphology["plano"]["algorithms"][algorithm][
                    "stability_median_of_chips"
                ]["neighbor_abs_difference_p95_degrees"],
                "mountain_p99_degrees": by_morphology["montana"]["algorithms"][algorithm][
                    "distribution_median_of_chips"
                ]["p99"],
                "mountain_maximum_degrees": by_morphology["montana"]["algorithms"][algorithm][
                    "distribution_median_of_chips"
                ]["maximum"],
            }
        return {
            "weighted_score": None,
            "dimensions": dimensions,
            "strict_dominance_claimed": False,
            "interpretation": (
                "Planar accuracy and noise stability are objective synthetic dimensions; real-terrain extremes "
                "and continuity are comparative product-behaviour dimensions without independent ground truth."
            ),
        }

    def _mathematical_contract(self) -> dict[str, Any]:
        return {
            "neighborhood_labels": "z1 z2 z3 / z4 z5 z6 / z7 z8 z9, rows top to bottom",
            "Horn": {
                "dz_dx": "((z3 + 2*z6 + z9) - (z1 + 2*z4 + z7)) / (8*dx)",
                "dz_dy": "((z7 + 2*z8 + z9) - (z1 + 2*z2 + z3)) / (8*dy)",
            },
            "ZevenbergenThorne": {
                "dz_dx": "(z6 - z4) / (2*dx)",
                "dz_dy": "(z8 - z2) / (2*dy)",
            },
            "slope_degrees": "atan(sqrt(dz_dx^2 + dz_dy^2)) * 180/pi",
            "future_slope_percentage": "tan(radians(slope_degrees)) * 100",
            "xy_unit": "metre",
            "z_unit": "metre",
            "effective_z_factor": 1.0,
            "documentation": "https://gdal.org/en/stable/programs/gdaldem.html",
        }
