from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Any

import rasterio

from core.pipelines.pendientes.constants import (
    DEM_PROMOTION_DIRECTORY_NAME,
    DEM_PROMOTION_MANIFEST_FILENAME,
    DEM_PROMOTION_TERRITORIAL_FILENAME,
    PIPELINE_NAME,
    PIPELINE_VERSION,
    SLOPE_PRODUCTION_CONTEXT_FILENAME,
    SLOPE_PRODUCTION_DEGREES_FILENAME,
    SLOPE_PRODUCTION_DIRECTORY_NAME,
    SLOPE_PRODUCTION_MANIFEST_FILENAME,
    SLOPE_PRODUCTION_PERCENT_FILENAME,
    SLOPE_PRODUCTION_PHASE7A_SHA256,
    SLOPE_SELECTION_DIRECTORY_NAME,
    SLOPE_SELECTION_MANIFEST_FILENAME,
    SLOPE_SELECTION_PARENT_MANIFEST_SHA256,
    STATE_VALIDATION_DIRECTORY_NAME,
    STATE_VALIDATION_INVENTORY_FILENAME,
    STATEWIDE_CANDIDATE_DIRECTORY_NAME,
    STATEWIDE_CANDIDATE_FILENAME,
    STATEWIDE_CANDIDATE_SHA256,
)
from core.pipelines.pendientes.helpers.slope_products import (
    create_territorial_degrees,
    create_territorial_percent,
    run_context_horn_slope,
    validate_context_slope,
    validate_frozen_backend,
    validate_slope_family,
    verify_phase7a_chips,
)
from core.utils.files import read_json, sha256_file, write_json_atomic


class PendientesSlopeProduction:
    """Produce and validate the degree/percent territorial slope family."""

    def __init__(self) -> None:
        transform_dir = Path("data") / "transform" / PIPELINE_NAME
        self.context_dem_path = transform_dir / STATEWIDE_CANDIDATE_DIRECTORY_NAME / STATEWIDE_CANDIDATE_FILENAME
        self.phase6b_dir = transform_dir / DEM_PROMOTION_DIRECTORY_NAME
        self.phase6b_manifest_path = self.phase6b_dir / DEM_PROMOTION_MANIFEST_FILENAME
        self.master_dem_path = self.phase6b_dir / DEM_PROMOTION_TERRITORIAL_FILENAME
        self.phase7a_dir = transform_dir / SLOPE_SELECTION_DIRECTORY_NAME
        self.phase7a_manifest_path = self.phase7a_dir / SLOPE_SELECTION_MANIFEST_FILENAME
        self.inventory_path = transform_dir / STATE_VALIDATION_DIRECTORY_NAME / STATE_VALIDATION_INVENTORY_FILENAME
        self.output_dir = transform_dir / SLOPE_PRODUCTION_DIRECTORY_NAME
        self.context_slope_path = self.output_dir / SLOPE_PRODUCTION_CONTEXT_FILENAME
        self.degrees_path = self.output_dir / SLOPE_PRODUCTION_DEGREES_FILENAME
        self.percent_path = self.output_dir / SLOPE_PRODUCTION_PERCENT_FILENAME
        self.manifest_path = self.output_dir / SLOPE_PRODUCTION_MANIFEST_FILENAME

    def execute(self) -> dict[str, Any]:
        started = time.perf_counter()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        inputs = self._validate_inputs()
        phase6b = inputs.pop("_phase6b")
        phase7a = inputs.pop("_phase7a")
        inventory = inputs.pop("_inventory")
        backend = phase7a["next_phase_contract"]["backend"]
        backend_validation = validate_frozen_backend(backend)
        try:
            context_processing = self._ensure_context_slope(backend)
            context_qa = validate_context_slope(self.context_dem_path, self.context_slope_path)
            if not context_qa["passed"]:
                raise ValueError(f"Context slope QA failed: {context_qa}")
            chip_reproduction = verify_phase7a_chips(
                self.context_slope_path,
                inventory,
                phase7a,
            )
            if not chip_reproduction["passed"]:
                raise ValueError(f"Phase 7A chip reproduction failed: {chip_reproduction}")
            territorial_window = phase6b["processing"]["territorial_window"]
            degree_processing = self._ensure_territorial_degrees(territorial_window)
            percent_processing = self._ensure_territorial_percent()
            family_qa = validate_slope_family(self.master_dem_path, self.degrees_path, self.percent_path)
            if not family_qa["hard_gates"]["all_passed"]:
                raise ValueError(f"Slope-family hard gates failed: {family_qa['hard_gates']}")
            products = self._products()
            manifest = self._manifest(
                status="slope_family_validated_not_published",
                started=started,
                inputs=inputs,
                backend=backend,
                backend_validation=backend_validation,
                processing={
                    "context_slope": context_processing,
                    "territorial_degrees": degree_processing,
                    "territorial_percent": percent_processing,
                },
                qa={
                    "context_slope": context_qa,
                    "phase7a_chip_reproduction": chip_reproduction,
                    "slope_family": family_qa,
                },
                products=products,
                phase6b=phase6b,
            )
        except Exception as error:
            manifest = self._manifest(
                status="slope_production_failed",
                started=started,
                inputs=inputs,
                backend=backend,
                backend_validation=backend_validation,
                processing={},
                qa={"failure": {"type": type(error).__name__, "message": str(error)}},
                products=self._existing_products(),
                phase6b=phase6b,
            )
            write_json_atomic(manifest, self.manifest_path)
            raise
        write_json_atomic(manifest, self.manifest_path)
        return manifest

    def _validate_inputs(self) -> dict[str, Any]:
        phase6b_sha = sha256_file(self.phase6b_manifest_path)
        phase7a_sha = sha256_file(self.phase7a_manifest_path)
        context_sha = sha256_file(self.context_dem_path)
        master_sha = sha256_file(self.master_dem_path)
        if phase6b_sha != SLOPE_SELECTION_PARENT_MANIFEST_SHA256:
            raise ValueError("Phase 6B manifest checksum changed")
        if phase7a_sha != SLOPE_PRODUCTION_PHASE7A_SHA256:
            raise ValueError("Phase 7A manifest checksum changed")
        if context_sha != STATEWIDE_CANDIDATE_SHA256:
            raise ValueError("Validated context DEM checksum changed")
        phase6b = read_json(self.phase6b_manifest_path)
        phase7a = read_json(self.phase7a_manifest_path)
        inventory = read_json(self.inventory_path)
        if phase6b is None or phase7a is None or inventory is None:
            raise ValueError("A required Phase 6B/7A input could not be read")
        if phase6b["status"] != "conditioned_dem_validated_for_derivatives":
            raise ValueError("Phase 6B is not validated for derivatives")
        if phase7a["decision"]["value"] != "Horn_recomendado_para_produccion":
            raise ValueError("Phase 7A decision is not Horn_recomendado_para_produccion")
        contract = phase7a["next_phase_contract"]
        if contract["selected_slope_algorithm"] != "Horn":
            raise ValueError("Phase 7A production contract did not select Horn")
        if contract["parent_context_dem_sha256"] != context_sha:
            raise ValueError("Phase 7A parent context SHA does not match")
        if master_sha != phase6b["territorial_dem"]["sha256"]:
            raise ValueError("Territorial master DEM checksum changed")
        if master_sha != contract["master_territorial_grid"]["master_dem_sha256"]:
            raise ValueError("Phase 7A master grid SHA does not match Phase 6B")
        if len(inventory["chips"]) != 30 or len(phase7a["real_chip_results"]) != 30:
            raise ValueError("Phase 7B requires the exact 30-chip inventory")
        with rasterio.open(self.context_dem_path) as context, rasterio.open(self.master_dem_path) as master:
            if context.shape != (29255, 30533) or context.res != (15.0, 15.0):
                raise ValueError("Context DEM dimensions/resolution changed")
            master_grid = phase6b["master_grid"]
            if (
                master.width != master_grid["width"]
                or master.height != master_grid["height"]
                or list(master.transform) != master_grid["transform"]
                or list(master.bounds) != master_grid["bounds"]
            ):
                raise ValueError("Territorial master grid differs from Phase 6B manifest")
        return {
            "phase6b_manifest": {"path": str(self.phase6b_manifest_path), "sha256": phase6b_sha},
            "phase7a_manifest": {"path": str(self.phase7a_manifest_path), "sha256": phase7a_sha},
            "validated_context_dem": {"path": str(self.context_dem_path), "sha256": context_sha},
            "master_territorial_dem": {"path": str(self.master_dem_path), "sha256": master_sha},
            "inventory": {"path": str(self.inventory_path), "sha256": sha256_file(self.inventory_path)},
            "_phase6b": phase6b,
            "_phase7a": phase7a,
            "_inventory": inventory,
        }

    def _ensure_context_slope(self, backend: dict[str, Any]) -> dict[str, Any]:
        if self.context_slope_path.exists():
            return self._resumed_processing("context_slope")
        result = run_context_horn_slope(backend, self.context_dem_path, self.context_slope_path)
        return {"existing_artifact_reused": False, **result}

    def _ensure_territorial_degrees(self, territorial_window: dict[str, int]) -> dict[str, Any]:
        if self.degrees_path.exists():
            return self._resumed_processing("territorial_degrees")
        result = create_territorial_degrees(
            self.context_slope_path,
            self.master_dem_path,
            self.degrees_path,
            territorial_window,
        )
        return {"existing_artifact_reused": False, **result}

    def _ensure_territorial_percent(self) -> dict[str, Any]:
        if self.percent_path.exists():
            return self._resumed_processing("territorial_percent")
        result = create_territorial_percent(self.degrees_path, self.percent_path)
        return {"existing_artifact_reused": False, **result}

    def _resumed_processing(self, key: str) -> dict[str, Any]:
        previous = read_json(self.manifest_path)
        if previous is None or key not in previous.get("processing", {}):
            return {"existing_artifact_reused_on_resume": True}
        return {**previous["processing"][key], "existing_artifact_reused_on_resume": True}

    def _products(self) -> dict[str, Any]:
        degrees_sha = sha256_file(self.degrees_path)
        return {
            "context_degrees": {
                "path": str(self.context_slope_path),
                "sha256": sha256_file(self.context_slope_path),
                "parent_context_dem_sha256": STATEWIDE_CANDIDATE_SHA256,
                "publishable": False,
            },
            "pendiente_grados": {
                "path": str(self.degrees_path),
                "sha256": degrees_sha,
                "parent_product": "modelo_elevacion_acondicionado_contexto",
                "parent_context_dem_sha256": STATEWIDE_CANDIDATE_SHA256,
                "unit": "degree",
            },
            "pendiente_porcentaje": {
                "path": str(self.percent_path),
                "sha256": sha256_file(self.percent_path),
                "parent_product": "pendiente_grados",
                "parent_sha256": degrees_sha,
                "unit": "percent",
            },
        }

    def _existing_products(self) -> dict[str, Any]:
        return {
            name: {"path": str(path), "exists": path.exists()}
            for name, path in (
                ("context_degrees", self.context_slope_path),
                ("pendiente_grados", self.degrees_path),
                ("pendiente_porcentaje", self.percent_path),
            )
        }

    def _manifest(
        self,
        *,
        status: str,
        started: float,
        inputs: dict[str, Any],
        backend: dict[str, Any],
        backend_validation: dict[str, Any],
        processing: dict[str, Any],
        qa: dict[str, Any],
        products: dict[str, Any],
        phase6b: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "phase": "7B_statewide_slope_degree_percent_production",
            "pipeline_version": PIPELINE_VERSION,
            "created_at": datetime.now().astimezone().isoformat(),
            "status": status,
            "published": False,
            "loaded": False,
            "served": False,
            "inputs": inputs,
            "backend": {**backend, "production_validation": backend_validation},
            "algorithm": "Horn",
            "edge_policy": backend["edge_policy"],
            "nodata_policy": backend["nodata_policy"],
            "effective_z_factor": backend["parameters"]["effective_z_factor"],
            "mathematical_contract": {
                "Horn_dz_dx": "((z3 + 2*z6 + z9) - (z1 + 2*z4 + z7)) / (8*dx)",
                "Horn_dz_dy": "((z7 + 2*z8 + z9) - (z1 + 2*z2 + z3)) / (8*dy)",
                "slope_degrees": "atan(sqrt(dz_dx^2 + dz_dy^2)) * 180/pi",
                "slope_percent": "float32(tan(radians(float64(slope_degrees))) * 100)",
                "dx_m": 15.0,
                "dy_m": 15.0,
            },
            "master_grid": phase6b["master_grid"],
            "processing": processing,
            "products": products,
            "qa": qa,
            "lineage": {
                "source": phase6b["lineage"]["source"],
                "baseline": phase6b["lineage"]["baseline"],
                "conditioned_context_dem": {
                    "sha256": STATEWIDE_CANDIDATE_SHA256,
                    "conditioning": "FP2",
                },
                "pendiente_grados": [
                    "conditioned_context_dem",
                    f"{backend['version']} Horn degrees",
                    "context_slope",
                    "Phase 6B master window and mask",
                ],
                "pendiente_porcentaje": [
                    "pendiente_grados SHA-256",
                    "float32(tan(radians(float64(degrees))) * 100)",
                ],
            },
            "elapsed_seconds": time.perf_counter() - started,
        }
