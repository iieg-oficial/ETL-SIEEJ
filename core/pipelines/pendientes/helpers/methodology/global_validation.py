from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import rasterio

from core.pipelines.pendientes.constants import (
    BANDING_REVIEW_DIRECTORY_NAME,
    BANDING_REVIEW_MANIFEST_FILENAME,
    CALIBRATION_FEATURE_PRESERVING_CONFIGS,
    EXPERIMENT_BASELINE_SHA256,
    FINAL_NODATA,
    GLOBAL_VALIDATION_CANDIDATE_IDS,
    GLOBAL_VALIDATION_DECISIONS,
    GLOBAL_VALIDATION_DIRECTORY_NAME,
    GLOBAL_VALIDATION_FLOAT_TOLERANCE_M,
    GLOBAL_VALIDATION_MANIFEST_FILENAME,
    GLOBAL_VALIDATION_PROFILE_CHIP_COUNT,
    PIPELINE_NAME,
    PIPELINE_VERSION,
    SOURCE_DIAGNOSTIC_DIRECTORY_NAME,
    SOURCE_DIAGNOSTIC_MANIFEST_FILENAME,
    STATE_VALIDATION_CHIP_COUNT_TARGET,
    STATE_VALIDATION_DIRECTORY_NAME,
    STATE_VALIDATION_INVENTORY_FILENAME,
    STATE_VALIDATION_MANIFEST_FILENAME,
    STATE_VALIDATION_MORPHOLOGY_CLASSES,
    TARGET_RESOLUTION_M,
    TARGET_SRID,
)
from core.pipelines.pendientes.helpers.methodology.calibration_profiles import (
    profile_lines_from_raw,
    profile_records,
    write_profile_csv,
    write_profile_png,
)
from core.pipelines.pendientes.helpers.experimental_artifacts import hillshade, write_comparison_png
from core.pipelines.pendientes.helpers.experimental_whitebox import (
    inspect_whitebox_backend,
    run_feature_preserving_smoothing,
)
from core.pipelines.pendientes.helpers.methodology.global_validation_qa import (
    aggregate_candidate_metrics,
    candidate_outliers,
    comparative_candidate_qa,
    pareto_comparison,
    profile_attenuation_metrics,
)
from core.utils.files import read_json, sha256_file, write_json_atomic


class PendientesGlobalConditioningValidation:
    """Compare frozen light global-conditioning candidates on the Phase-5A sample."""

    def __init__(self) -> None:
        transform_dir = Path("data") / "transform" / PIPELINE_NAME
        self.state_dir = transform_dir / STATE_VALIDATION_DIRECTORY_NAME
        self.inventory_path = self.state_dir / STATE_VALIDATION_INVENTORY_FILENAME
        self.state_manifest_path = self.state_dir / STATE_VALIDATION_MANIFEST_FILENAME
        self.banding_manifest_path = (
            transform_dir / BANDING_REVIEW_DIRECTORY_NAME / BANDING_REVIEW_MANIFEST_FILENAME
        )
        self.source_diagnostic_manifest_path = (
            transform_dir / SOURCE_DIAGNOSTIC_DIRECTORY_NAME / SOURCE_DIAGNOSTIC_MANIFEST_FILENAME
        )
        self.output_dir = transform_dir / GLOBAL_VALIDATION_DIRECTORY_NAME
        self.manifest_path = self.output_dir / GLOBAL_VALIDATION_MANIFEST_FILENAME

    def execute(self) -> dict[str, Any]:
        started = time.perf_counter()
        inventory, state_manifest, banding_manifest, source_diagnostic = self._validate_inputs()
        backend = self._whitebox_backend(state_manifest)
        configurations = self._candidate_configurations()
        raw_contracts = self._raw_contracts(inventory, state_manifest, banding_manifest)
        results = {}
        for chip in inventory["chips"]:
            results[chip["chip_id"]] = self._run_chip(
                chip,
                raw_contracts[chip["chip_id"]],
                configurations,
                backend,
            )

        representative = self._representative_chips(inventory)
        profiles = {chip_id: self._write_profiles(results[chip_id]) for chip_id in representative}
        visualizations = {chip_id: self._write_hillshade(results[chip_id]) for chip_id in representative}
        aggregate = {
            candidate_id: aggregate_candidate_metrics(results, candidate_id)
            for candidate_id in GLOBAL_VALIDATION_CANDIDATE_IDS
        }
        by_morphology = {
            morphology: {
                candidate_id: aggregate_candidate_metrics(results, candidate_id, morphology)
                for candidate_id in GLOBAL_VALIDATION_CANDIDATE_IDS
            }
            for morphology in STATE_VALIDATION_MORPHOLOGY_CLASSES
        }
        profile_aggregate = self._aggregate_profiles(profiles)
        pareto = pareto_comparison(aggregate, profile_aggregate)
        outliers = {
            candidate_id: candidate_outliers(results, candidate_id)
            for candidate_id in GLOBAL_VALIDATION_CANDIDATE_IDS
        }
        manifest = {
            "phase": "5D_state_comparative_light_global_conditioning",
            "pipeline_version": PIPELINE_VERSION,
            "created_at": datetime.now().astimezone().isoformat(),
            "status": "completed_pending_comparative_review",
            "inputs": {
                "state_inventory_path": str(self.inventory_path),
                "state_inventory_sha256": sha256_file(self.inventory_path),
                "state_manifest_path": str(self.state_manifest_path),
                "state_manifest_sha256": sha256_file(self.state_manifest_path),
                "phase5b_manifest_path": str(self.banding_manifest_path),
                "phase5b_manifest_sha256": sha256_file(self.banding_manifest_path),
                "phase5b_status": "superseded_for_binary_localization",
                "phase5c_manifest_path": str(self.source_diagnostic_manifest_path),
                "phase5c_manifest_sha256": sha256_file(self.source_diagnostic_manifest_path),
                "phase5c_status": source_diagnostic["status"],
                "source_pattern_origin": source_diagnostic["evidence"]["categories"][0],
                "baseline_sha256": state_manifest["baseline"]["sha256"],
            },
            "sample": {
                "chip_count": len(results),
                "same_phase5a_design": True,
                "raw_checksums_verified": len(raw_contracts),
                "mandatory_manual_coordinate": {"x": 750968.0, "y": 2329434.0, "epsg": TARGET_SRID},
                "old_banding_classes_used_for_decision": False,
            },
            "whitebox_backend": backend,
            "candidates": configurations,
            "processing": {
                "reference": "complete 1024x1024 chip processed directly by WhiteboxTools",
                "whitebox_executions": len(results) * len(GLOBAL_VALIDATION_CANDIDATE_IDS),
                "tiled_inside_chips": False,
                "phase5a_fp3_exact_tile_halo_pixels": 24,
                "halo_generalized_to_fp1_or_fp2": False,
            },
            "results": results,
            "aggregate_state_sample": aggregate,
            "aggregate_by_morphology": by_morphology,
            "profiles": {
                "selected_chip_ids": representative,
                "chip_count": len(representative),
                "results": profiles,
                "aggregate": profile_aggregate,
            },
            "hillshade": {
                "selected_chip_ids": representative,
                "chip_count": len(representative),
                "azimuth_degrees": 315.0,
                "altitude_degrees": 45.0,
                "series_order": ["RAW", *GLOBAL_VALIDATION_CANDIDATE_IDS],
                "independent_autoscaling": False,
                "visualizations": visualizations,
            },
            "pareto": pareto,
            "outliers": outliers,
            "reprojection_decision": {
                "source": "EPSG:6365 / 0.5 arcsec / Int16",
                "resampling": "bilinear",
                "target": "EPSG:6368 / 15 m / Float32",
                "changed": False,
                "interpretation": (
                    "Bilinear partially reduces discretization expression but cannot recover absent vertical information."
                ),
            },
            "decision": {
                "allowed": list(GLOBAL_VALIDATION_DECISIONS),
                "value": None,
                "status": "awaiting_pareto_and_visual_review",
            },
            "next_phase_contract": None,
            "statewide_baseline_processed": False,
            "institutional_products_generated": [],
            "elapsed_seconds": time.perf_counter() - started,
        }
        write_json_atomic(manifest, self.manifest_path)
        return manifest

    def record_decision(self, decision: str, evidence: dict[str, Any]) -> dict[str, Any]:
        if decision not in GLOBAL_VALIDATION_DECISIONS:
            raise ValueError(f"Unsupported Phase-5D decision: {decision}")
        manifest = read_json(self.manifest_path)
        if manifest is None or manifest.get("status") != "completed_pending_comparative_review":
            raise ValueError("A completed Phase-5D comparison is required")
        selected = None if decision in {"mantener_RAW", "requiere_otra_calibracion"} else decision.split("_", 1)[0]
        next_contract = None
        if selected is not None:
            selected_configuration = manifest["candidates"][selected]
            next_contract = {
                "selected_conditioning_method": "WhiteboxTools FeaturePreservingSmoothing",
                "selected_candidate_id": selected,
                "selected_parameters": selected_configuration,
                "required_tile_validation": {
                    "required": True,
                    "halo_pixels": None,
                    "must_demonstrate_exact_equivalence": True,
                    "phase5a_fp3_halo_24_must_not_be_assumed": selected != "FP3",
                },
                "required_statewide_QA": [
                    "grid and NoData preservation",
                    "maximum absolute elevation change",
                    "elevation and slope distributions",
                    "strong-gradient and surface-normal preservation",
                    "second-difference ratios by morphology",
                    "seam checks after tiled execution",
                    "Jalisco mask and absence of valid pixels outside state boundary",
                ],
            }
        manifest["decision"] = {
            "allowed": list(GLOBAL_VALIDATION_DECISIONS),
            "value": decision,
            "status": "reviewed_candidate_for_next_qa_only",
            "evidence": evidence,
            "reviewed_at": datetime.now().astimezone().isoformat(),
        }
        manifest["next_phase_contract"] = next_contract
        manifest["status"] = "completed_reviewed_no_statewide_execution"
        write_json_atomic(manifest, self.manifest_path)
        return manifest

    def refresh_analysis(self) -> dict[str, Any]:
        manifest = read_json(self.manifest_path)
        if manifest is None or manifest.get("status") != "completed_reviewed_no_statewide_execution":
            raise ValueError("A reviewed Phase-5D manifest is required for summary refresh")
        results = manifest["results"]
        aggregate = {
            candidate_id: aggregate_candidate_metrics(results, candidate_id)
            for candidate_id in GLOBAL_VALIDATION_CANDIDATE_IDS
        }
        manifest["aggregate_state_sample"] = aggregate
        manifest["aggregate_by_morphology"] = {
            morphology: {
                candidate_id: aggregate_candidate_metrics(results, candidate_id, morphology)
                for candidate_id in GLOBAL_VALIDATION_CANDIDATE_IDS
            }
            for morphology in STATE_VALIDATION_MORPHOLOGY_CLASSES
        }
        manifest["pareto"] = pareto_comparison(aggregate, manifest["profiles"]["aggregate"])
        manifest["outliers"] = {
            candidate_id: candidate_outliers(results, candidate_id)
            for candidate_id in GLOBAL_VALIDATION_CANDIDATE_IDS
        }
        manifest["analysis_refreshed_at"] = datetime.now().astimezone().isoformat()
        write_json_atomic(manifest, self.manifest_path)
        return manifest

    def _validate_inputs(self) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
        inventory = read_json(self.inventory_path)
        state_manifest = read_json(self.state_manifest_path)
        banding_manifest = read_json(self.banding_manifest_path)
        source_diagnostic = read_json(self.source_diagnostic_manifest_path)
        if any(item is None for item in (inventory, state_manifest, banding_manifest, source_diagnostic)):
            raise FileNotFoundError("Phase-5A, 5B and 5C manifests are required")
        if inventory["chip_count"] != STATE_VALIDATION_CHIP_COUNT_TARGET or len(inventory["chips"]) != 30:
            raise ValueError("Phase-5D requires exactly the 30 Phase-5A chips")
        manual = next((chip for chip in inventory["chips"] if chip["chip_id"] == "problema_manual"), None)
        if manual is None or float(manual["center_x"]) != 750968.0 or float(manual["center_y"]) != 2329434.0:
            raise ValueError("Mandatory manual site changed")
        if state_manifest["status"] != "completed_reviewed_not_promoted":
            raise ValueError("Phase 5A must remain reviewed and unchanged")
        if state_manifest["baseline"]["sha256"] != EXPERIMENT_BASELINE_SHA256:
            raise ValueError("Frozen baseline checksum changed")
        if banding_manifest["status"] != "completed_awaiting_human_review":
            raise ValueError("Phase-5B experimental manifest changed")
        if source_diagnostic["status"] != "completed_diagnostic_not_promoted":
            raise ValueError("Phase-5C diagnostic status changed")
        if source_diagnostic["evidence"]["categories"] != ["principalmente_presente_en_fuente"]:
            raise ValueError("Phase-5C source-pattern conclusion changed")
        return inventory, state_manifest, banding_manifest, source_diagnostic

    def _whitebox_backend(self, state_manifest: dict[str, Any]) -> dict[str, Any]:
        previous = state_manifest["whitebox_backend"]
        backend = inspect_whitebox_backend(
            Path(previous["executable"]),
            previous["expected_exact_version"],
            previous["executable_sha256"],
        )
        return {
            **backend,
            "python_frontend_contract": "whitebox==2.3.6",
            "revalidated_before_phase5d": True,
        }

    def _candidate_configurations(self) -> dict[str, dict[str, Any]]:
        configurations = {
            str(item["id"]): dict(item)
            for item in CALIBRATION_FEATURE_PRESERVING_CONFIGS
            if item["id"] in GLOBAL_VALIDATION_CANDIDATE_IDS
        }
        if tuple(configurations) != GLOBAL_VALIDATION_CANDIDATE_IDS:
            raise ValueError("Frozen FP1/FP2/FP3 configurations are incomplete")
        return configurations

    def _raw_contracts(
        self,
        inventory: dict[str, Any],
        state_manifest: dict[str, Any],
        banding_manifest: dict[str, Any],
    ) -> dict[str, Any]:
        contracts = {}
        for chip in inventory["chips"]:
            chip_id = chip["chip_id"]
            raw_path = Path(state_manifest["results"][chip_id]["artifacts"]["RAW"])
            checksum = sha256_file(raw_path)
            previous = banding_manifest["raw_artifacts"][chip_id]
            if Path(previous["path"]) != raw_path or previous["sha256"] != checksum:
                raise ValueError(f"RAW artifact changed for {chip_id}")
            contracts[chip_id] = {"path": str(raw_path), "sha256": checksum}
        return contracts

    def _run_chip(
        self,
        chip: dict[str, Any],
        raw_contract: dict[str, Any],
        configurations: dict[str, dict[str, Any]],
        backend: dict[str, Any],
    ) -> dict[str, Any]:
        raw_path = Path(raw_contract["path"])
        with rasterio.open(raw_path) as dataset:
            raw = dataset.read(1)
            transform = dataset.transform
            crs = dataset.crs
            nodata = dataset.nodata
            profile = dataset.profile
        if crs is None or crs.to_epsg() != TARGET_SRID or nodata != FINAL_NODATA or raw.shape != (1024, 1024):
            raise ValueError(f"RAW contract changed for {chip['chip_id']}")
        candidates: dict[str, Any] = {
            "RAW": {
                "artifact": raw_contract,
                "qa": comparative_candidate_qa(raw, raw, TARGET_RESOLUTION_M, nodata),
                "execution": None,
                "max_diff_verification": {"limit_m": 0.0, "observed_m": 0.0, "passed": True},
            }
        }
        chip_dir = self.output_dir / "chips" / chip["chip_id"]
        for candidate_id, configuration in configurations.items():
            output_path = chip_dir / candidate_id / "dem.tif"
            execution = run_feature_preserving_smoothing(backend, raw_path, output_path, configuration)
            with rasterio.open(output_path) as dataset:
                candidate = dataset.read(1)
                if (
                    dataset.transform != transform
                    or dataset.crs != crs
                    or dataset.shape != raw.shape
                    or dataset.nodata != nodata
                    or dataset.dtypes != (profile["dtype"],)
                ):
                    raise ValueError(f"Whitebox grid contract changed for {chip['chip_id']} {candidate_id}")
            qa = comparative_candidate_qa(raw, candidate, TARGET_RESOLUTION_M, nodata)
            observed = qa["elevation"]["absolute_difference_m"]["maximum"]
            limit = float(configuration["max_diff_m"])
            passed = observed <= limit + GLOBAL_VALIDATION_FLOAT_TOLERANCE_M
            if not passed:
                raise ValueError(f"{candidate_id} exceeded max_diff in {chip['chip_id']}: {observed}")
            candidates[candidate_id] = {
                "artifact": {"path": str(output_path), "sha256": sha256_file(output_path)},
                "qa": qa,
                "execution": {
                    "elapsed_seconds": execution["elapsed_seconds"],
                    "return_code": execution["return_code"],
                    "command": execution["command"],
                    "output_sha256": execution["output_sha256"],
                },
                "max_diff_verification": {
                    "limit_m": limit,
                    "float32_tolerance_m": GLOBAL_VALIDATION_FLOAT_TOLERANCE_M,
                    "observed_m": observed,
                    "passed": passed,
                },
            }
        return {
            "chip": {
                "chip_id": chip["chip_id"],
                "center_x": chip["center_x"],
                "center_y": chip["center_y"],
                "bbox": chip["bbox"],
                "morphology_class": chip["morphology_class"],
                "valid_percentage": chip["valid_percentage"],
            },
            "candidates": candidates,
        }

    def _representative_chips(self, inventory: dict[str, Any]) -> list[str]:
        groups = {
            morphology: sorted(
                chip["chip_id"] for chip in inventory["chips"] if chip["morphology_class"] == morphology
            )
            for morphology in STATE_VALIDATION_MORPHOLOGY_CLASSES
        }
        selected = [
            "problema_manual",
            *[chip_id for chip_id in groups["plano"] if chip_id != "problema_manual"][:2],
            *groups["valle"][:2],
            *groups["lomerio"][:2],
            *groups["montana"][:2],
            *groups["transicion_valle_sierra"][:1],
        ]
        if len(selected) != GLOBAL_VALIDATION_PROFILE_CHIP_COUNT or len(set(selected)) != len(selected):
            raise ValueError("Representative profile/hillshade selection must contain exactly 10 unique chips")
        return selected

    def _read_candidate_arrays(self, result: dict[str, Any]) -> tuple[dict[str, np.ndarray], Any, Any]:
        arrays = {}
        transform = None
        crs = None
        for candidate_id in ("RAW", *GLOBAL_VALIDATION_CANDIDATE_IDS):
            with rasterio.open(result["candidates"][candidate_id]["artifact"]["path"]) as dataset:
                arrays[candidate_id] = dataset.read(1)
                transform = dataset.transform
                crs = dataset.crs
        return arrays, transform, crs

    def _write_profiles(self, result: dict[str, Any]) -> dict[str, Any]:
        arrays, transform, _ = self._read_candidate_arrays(result)
        lines, contract = profile_lines_from_raw(arrays["RAW"], FINAL_NODATA)
        output = {}
        for line in lines:
            records = profile_records(
                line,
                arrays["RAW"],
                {candidate_id: arrays[candidate_id] for candidate_id in GLOBAL_VALIDATION_CANDIDATE_IDS},
                transform,
            )
            directory = self.output_dir / "profiles" / result["chip"]["chip_id"]
            csv_path = write_profile_csv(directory / f"{line.profile_id}.csv", records)
            png = write_profile_png(
                directory / f"{line.profile_id}.png",
                records,
                ("RAW", *GLOBAL_VALIDATION_CANDIDATE_IDS),
            )
            rows = np.asarray(line.rows)
            columns = np.asarray(line.columns)
            raw_values = arrays["RAW"][rows, columns]
            output[line.profile_id] = {
                "csv_path": str(csv_path),
                "csv_sha256": sha256_file(csv_path),
                "visualization": png,
                "metrics": {
                    candidate_id: profile_attenuation_metrics(
                        raw_values,
                        arrays[candidate_id][rows, columns],
                    )
                    for candidate_id in GLOBAL_VALIDATION_CANDIDATE_IDS
                },
            }
        return {"contract": contract, "transects": output}

    def _write_hillshade(self, result: dict[str, Any]) -> dict[str, Any]:
        arrays, _, _ = self._read_candidate_arrays(result)
        panels = []
        for candidate_id in ("RAW", *GLOBAL_VALIDATION_CANDIDATE_IDS):
            shade, valid = hillshade(arrays[candidate_id], TARGET_RESOLUTION_M, FINAL_NODATA, 315.0, 45.0)
            panels.append((candidate_id, shade, valid))
        return write_comparison_png(
            self.output_dir / "hillshade" / f"{result['chip']['chip_id']}.png",
            panels,
            0.0,
            255.0,
        )

    def _aggregate_profiles(self, profiles: dict[str, Any]) -> dict[str, dict[str, float]]:
        output = {}
        for candidate_id in GLOBAL_VALIDATION_CANDIDATE_IDS:
            metrics = [
                transect["metrics"][candidate_id]
                for profile in profiles.values()
                for transect in profile["transects"].values()
            ]
            output[candidate_id] = {
                key: float(np.median([float(item[key]) for item in metrics]))
                for key in (
                    "strong_step_amplitude_candidate_to_raw_median",
                    "strong_step_retained_above_half_percentage",
                    "endpoint_trend_error_m",
                    "mean_z_change_m",
                    "maximum_absolute_z_change_m",
                )
            }
        return output
