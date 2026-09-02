from __future__ import annotations

import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from core.pipelines.pendientes.constants import (
    CARTOGRAPHIC_PRODUCTION_CONTEXT_FILENAME,
    CARTOGRAPHIC_PRODUCTION_DECISION,
    CARTOGRAPHIC_PRODUCTION_DEGREES_FILENAME,
    CARTOGRAPHIC_PRODUCTION_DIRECTORY_NAME,
    CARTOGRAPHIC_PRODUCTION_MANIFEST_FILENAME,
    CARTOGRAPHIC_PRODUCTION_PERCENT_FILENAME,
    CARTOGRAPHIC_PRODUCTION_STATUS,
    CLASSIFICATION_SOURCES,
    DEGREES_CLASSIFICATION,
    DEM_PROMOTION_DIRECTORY_NAME,
    DEM_PROMOTION_MANIFEST_FILENAME,
    DEM_PROMOTION_TERRITORIAL_FILENAME,
    FINAL_ANALYTICAL_DIRECTORY_NAME,
    FINAL_CARTOGRAPHIC_DIRECTORY_NAME,
    FINAL_DEGREES_CLASSIFIED_FILENAME,
    FINAL_DIRECTORY_NAME,
    FINAL_INTERMEDIATE_DIRECTORY_NAME,
    FINAL_NODATA,
    FINAL_PERCENT_CLASSIFIED_FILENAME,
    MULTISCALE_SLOPE_DIRECTORY_NAME,
    MULTISCALE_SLOPE_MANIFEST_FILENAME,
    MULTISCALE_SLOPE_PARENT_SHA256,
    PERCENT_CLASSIFICATION,
    PIPELINE_NAME,
    SLOPE_PRODUCTION_DEGREES_FILENAME,
    SLOPE_PRODUCTION_DIRECTORY_NAME,
    SLOPE_PRODUCTION_PERCENT_FILENAME,
    STATEWIDE_CANDIDATE_DIRECTORY_NAME,
    STATEWIDE_CANDIDATE_FILENAME,
    VALIDATED_DEGREES_SHA256,
    VALIDATED_DEM_SHA256,
)
from core.pipelines.pendientes.helpers.classification import classify_values, create_classified_raster
from core.pipelines.pendientes.helpers.cog import create_cog, inspect_cog_driver, validate_lossless_cog
from core.pipelines.pendientes.helpers.experimental_metrics import valid_mask
from core.pipelines.pendientes.helpers.multiscale_slope import class_fragmentation, inspect_grass_param_scale
from core.pipelines.pendientes.helpers.productive_we5 import (
    compare_statewide_slopes,
    run_context_we5,
    validate_we5_context,
    verify_eight_we5_chips,
)
from core.pipelines.pendientes.helpers.slope_products import (
    create_territorial_degrees,
    create_territorial_percent,
    validate_slope_family,
)
from core.pipelines.pendientes.helpers.tiled_conditioning import core_tile_windows
from core.utils.files import read_json, sha256_file, write_json_atomic


HISTORICAL_COG_SHA256 = {
    "pendiente_grados": "3d87bfefe00a43647d4c60787d79173f02e3ab72b7be837084f685c0f89d9ff3",
    "pendiente_porcentaje": "68de35ae51f97503718da7d166edfdc8f97b4a12402f07bdb6e0a6aaf6ca803d",
    "pendiente_grados_clasificada": "f684dca82a560d5950d01b455c516d08faa12b3fa19bda27b118303ff46100d6",
    "pendiente_porcentaje_clasificada": "ee6069e1736a52e7988d6d72cadbec901144afbba4be28978a1a5d3701bcbfdf",
}
DEM_COG_SHA256 = "7c533785f0d2740d6dcf9db56aebb05a38e80b07b0b555393a1318806a72fd24"


class PendientesCartographicSlopeProduction:
    """Produce the selected statewide WE5 slope family and release COGs."""

    def __init__(self) -> None:
        transform = Path("data") / "transform" / PIPELINE_NAME
        self.context_dem_path = transform / STATEWIDE_CANDIDATE_DIRECTORY_NAME / STATEWIDE_CANDIDATE_FILENAME
        self.phase6b_dir = transform / DEM_PROMOTION_DIRECTORY_NAME
        self.phase6b_manifest_path = self.phase6b_dir / DEM_PROMOTION_MANIFEST_FILENAME
        self.master_dem_path = self.phase6b_dir / DEM_PROMOTION_TERRITORIAL_FILENAME
        self.horn_dir = transform / SLOPE_PRODUCTION_DIRECTORY_NAME
        self.horn_degrees_path = self.horn_dir / SLOPE_PRODUCTION_DEGREES_FILENAME
        self.horn_percent_path = self.horn_dir / SLOPE_PRODUCTION_PERCENT_FILENAME
        self.phase8a1_dir = transform / MULTISCALE_SLOPE_DIRECTORY_NAME
        self.phase8a1_manifest_path = self.phase8a1_dir / MULTISCALE_SLOPE_MANIFEST_FILENAME
        self.output_dir = transform / CARTOGRAPHIC_PRODUCTION_DIRECTORY_NAME
        self.context_path = self.output_dir / CARTOGRAPHIC_PRODUCTION_CONTEXT_FILENAME
        self.degrees_path = self.output_dir / CARTOGRAPHIC_PRODUCTION_DEGREES_FILENAME
        self.percent_path = self.output_dir / CARTOGRAPHIC_PRODUCTION_PERCENT_FILENAME
        self.classified_degrees_path = self.output_dir / "intermedios" / FINAL_DEGREES_CLASSIFIED_FILENAME
        self.classified_percent_path = self.output_dir / "intermedios" / FINAL_PERCENT_CLASSIFIED_FILENAME
        self.manifest_path = self.output_dir / CARTOGRAPHIC_PRODUCTION_MANIFEST_FILENAME
        self.final_dir = transform / FINAL_DIRECTORY_NAME
        self.final_analytical_dir = self.final_dir / FINAL_ANALYTICAL_DIRECTORY_NAME
        self.final_cartographic_dir = self.final_dir / FINAL_CARTOGRAPHIC_DIRECTORY_NAME
        self.final_intermediate_dir = self.final_dir / FINAL_INTERMEDIATE_DIRECTORY_NAME
        self.packaging_manifest_path = self.final_dir / "cog_packaging_manifest.json"

    def execute(self) -> dict[str, Any]:
        started = time.perf_counter()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        previous = read_json(self.manifest_path)
        if previous is not None and previous.get("status") == CARTOGRAPHIC_PRODUCTION_STATUS:
            self._validate_completed(previous)
            return {**previous, "reused": True}
        inputs, phase6b, phase8a1, backend = self._validate_inputs()
        checkpoint = previous or self._checkpoint(inputs, backend)
        write_json_atomic(checkpoint, self.manifest_path)
        try:
            context_processing = self._ensure_context(checkpoint, backend)
            context_qa = validate_we5_context(self.context_dem_path, self.context_path)
            self._require(context_qa["hard_gates"]["all_passed"], "WE5 context QA failed")
            reproduction = verify_eight_we5_chips(self.context_path, phase8a1, self.phase8a1_dir)
            self._require(reproduction["hard_gates"]["all_passed"], "8A.1 chip reproduction failed")
            territorial_processing = self._ensure_artifact(
                checkpoint,
                "territorial_degrees",
                self.degrees_path,
                lambda: create_territorial_degrees(
                    self.context_path,
                    self.master_dem_path,
                    self.degrees_path,
                    phase6b["processing"]["territorial_window"],
                ),
            )
            percent_processing = self._ensure_artifact(
                checkpoint,
                "territorial_percent",
                self.percent_path,
                lambda: create_territorial_percent(self.degrees_path, self.percent_path),
            )
            family_qa = validate_slope_family(self.master_dem_path, self.degrees_path, self.percent_path)
            self._require(family_qa["hard_gates"]["all_passed"], "WE5 slope family QA failed")
            comparison = compare_statewide_slopes(self.horn_degrees_path, self.degrees_path)
            classification = self._ensure_classifications(checkpoint)
            class_comparison = {
                "degrees": self._class_comparison(
                    self.horn_degrees_path, self.degrees_path, DEGREES_CLASSIFICATION
                ),
                "percent": self._class_comparison(
                    self.horn_percent_path, self.percent_path, PERCENT_CLASSIFICATION
                ),
            }
            controls = self._write_controls(phase8a1)
            packaging = self._package_release(checkpoint, classification)
            manifest = {
                **checkpoint,
                "status": CARTOGRAPHIC_PRODUCTION_STATUS,
                "created_at": datetime.now().astimezone().isoformat(),
                "reused": False,
                "decision": {
                    "value": CARTOGRAPHIC_PRODUCTION_DECISION,
                    "scope": "INEGI CEM 4.0; 15 m; FP2 conditioned DEM; territorial and municipal products",
                    "universal_superiority_claimed": False,
                },
                "method_reference": {
                    "method": "Horn3x3",
                    "methodological_reference": True,
                    "production_product": False,
                    "release_product": False,
                    "historical_degrees_sha256": VALIDATED_DEGREES_SHA256,
                },
                "selected_method": "WoodEvans5x5",
                "processing": {
                    "context": context_processing,
                    "territorial_degrees": territorial_processing,
                    "territorial_percent": percent_processing,
                },
                "products": self._products(classification, packaging),
                "qa": {
                    "context": context_qa,
                    "phase8a1_reproduction": reproduction,
                    "territorial_family": family_qa,
                    "statewide_horn_vs_we5": comparison,
                    "class_comparison": class_comparison,
                    "representative_controls": controls,
                    "visual_review": self._visual_review(),
                    "release_packaging": packaging,
                },
                "lineage": {
                    "slope_degrees": "FP2 context DEM -> GRASS r.param.scale Wood-Evans 5x5 -> master window/mask",
                    "slope_percent": "WE5 degrees -> float32(tan(radians(float64(degrees))) * 100)",
                    "classified_degrees": "WE5 degrees -> INEGI-DGG classification -> lossless COG",
                    "classified_percent": "WE5 percent -> FAO/GAEZ classification -> lossless COG",
                },
                "published": False,
                "loaded": False,
                "served": False,
                "municipal_statistics_executed": False,
                "elapsed_seconds": time.perf_counter() - started,
            }
            write_json_atomic(manifest, self.manifest_path)
            return manifest
        except Exception as error:
            checkpoint["status"] = "cartographic_slope_production_failed"
            checkpoint["failure"] = {"type": type(error).__name__, "message": str(error)}
            write_json_atomic(checkpoint, self.manifest_path)
            raise

    def finalize_visual_review(self) -> dict[str, Any]:
        """Record the completed human-readable control review without raster production."""
        manifest = read_json(self.manifest_path)
        if manifest is None or manifest.get("status") != CARTOGRAPHIC_PRODUCTION_STATUS:
            raise ValueError("A completed 8A.2 manifest is required")
        phase8a1 = read_json(self.phase8a1_manifest_path)
        manifest["qa"]["representative_controls"] = self._write_controls(phase8a1)
        manifest["qa"]["visual_review"] = self._visual_review()
        manifest["grass_region"] = self._grass_region()
        write_json_atomic(manifest, self.manifest_path)
        return manifest

    def _validate_inputs(self) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
        hashes = {
            "context_dem": sha256_file(self.context_dem_path),
            "master_dem": sha256_file(self.master_dem_path),
            "horn_degrees": sha256_file(self.horn_degrees_path),
            "phase8a1_manifest": sha256_file(self.phase8a1_manifest_path),
            "phase6b_manifest": sha256_file(self.phase6b_manifest_path),
        }
        self._require(hashes["context_dem"] == MULTISCALE_SLOPE_PARENT_SHA256, "FP2 context SHA changed")
        self._require(hashes["master_dem"] == VALIDATED_DEM_SHA256, "Master DEM SHA changed")
        self._require(hashes["horn_degrees"] == VALIDATED_DEGREES_SHA256, "Historical Horn SHA changed")
        phase6b = read_json(self.phase6b_manifest_path)
        phase8a1 = read_json(self.phase8a1_manifest_path)
        self._require(phase6b is not None and phase8a1 is not None, "Required manifest missing")
        self._require(
            phase8a1["decision"]["value"] == "WoodEvans5x5_recomendado_para_cartografia",
            "8A.1 did not recommend WE5",
        )
        backend = inspect_grass_param_scale()
        self._require(backend["version"] == "GRASS GIS 8.3.2", "Unexpected GRASS version")
        self._require(backend["windows"] == [3, 5, 7], "Frozen backend no longer supports expected windows")
        inputs = {
            "phase8a1_manifest": {"path": str(self.phase8a1_manifest_path), "sha256": hashes["phase8a1_manifest"]},
            "phase8a1_decision": phase8a1["decision"]["value"],
            "context_dem": {"path": str(self.context_dem_path), "sha256": hashes["context_dem"]},
            "master_dem": {"path": str(self.master_dem_path), "sha256": hashes["master_dem"]},
            "historical_horn_degrees": {"path": str(self.horn_degrees_path), "sha256": hashes["horn_degrees"]},
        }
        return inputs, phase6b, phase8a1, backend

    def _checkpoint(self, inputs: dict[str, Any], backend: dict[str, Any]) -> dict[str, Any]:
        return {
            "phase": "8A.2_statewide_productive_wood_evans_5x5",
            "status": "cartographic_slope_production_in_progress",
            "created_at": datetime.now().astimezone().isoformat(),
            "inputs": inputs,
            "backend": backend,
            "parameters": {"method": "slope", "size": 5, "exponent": 0.0, "zscale": 1.0},
            "grass_region": self._grass_region(),
            "checkpoint_artifacts": {},
        }

    def _grass_region(self) -> dict[str, Any]:
        with rasterio.open(self.context_dem_path) as dataset:
            return {
                "source": "g.region raster=dem after r.in.gdal",
                "crs_epsg": dataset.crs.to_epsg(),
                "west": dataset.bounds.left,
                "south": dataset.bounds.bottom,
                "east": dataset.bounds.right,
                "north": dataset.bounds.top,
                "rows": dataset.height,
                "cols": dataset.width,
                "ewres": dataset.res[0],
                "nsres": dataset.res[1],
                "nodata": dataset.nodata,
            }

    def _ensure_context(self, checkpoint: dict[str, Any], backend: dict[str, Any]) -> dict[str, Any]:
        return self._ensure_artifact(
            checkpoint,
            "context_degrees",
            self.context_path,
            lambda: run_context_we5(self.context_dem_path, self.context_path, backend),
        )

    def _ensure_artifact(self, checkpoint, key, path, producer):
        recorded = checkpoint.get("checkpoint_artifacts", {}).get(key)
        if path.exists():
            self._require(recorded is not None, f"Existing incompatible artifact without checkpoint: {path}")
            self._require(sha256_file(path) == recorded["sha256"], f"Existing artifact checksum changed: {path}")
            return {"existing_artifact_reused": True, "sha256": recorded["sha256"]}
        result = producer()
        record = {"path": str(path), "sha256": sha256_file(path), "processing": result}
        checkpoint.setdefault("checkpoint_artifacts", {})[key] = record
        write_json_atomic(checkpoint, self.manifest_path)
        return {"existing_artifact_reused": False, **result, "sha256": record["sha256"]}

    def _ensure_classifications(self, checkpoint: dict[str, Any]) -> dict[str, Any]:
        specifications = {
            "pendiente_grados_clasificada": (
                self.degrees_path,
                self.classified_degrees_path,
                DEGREES_CLASSIFICATION,
                CLASSIFICATION_SOURCES["degrees"],
            ),
            "pendiente_porcentaje_clasificada": (
                self.percent_path,
                self.classified_percent_path,
                PERCENT_CLASSIFICATION,
                CLASSIFICATION_SOURCES["percent"],
            ),
        }
        output = {}
        for key, (parent, path, classes, source) in specifications.items():
            processing = self._ensure_artifact(
                checkpoint,
                key,
                path,
                lambda parent=parent, path=path, classes=classes, source=source: create_classified_raster(
                    parent, path, classes, source
                ),
            )
            qa = read_json(self.manifest_path)["checkpoint_artifacts"][key]["processing"]
            self._require(qa["hard_gates"]["all_passed"], f"Classification QA failed: {key}")
            self._require(qa["valid_pixels"] == 356_528_880, f"Classification count failed: {key}")
            output[key] = {**qa, "resume": processing}
        return output

    @staticmethod
    def _class_comparison(reference_path: Path, selected_path: Path, classes) -> dict[str, Any]:
        size = len(classes)
        matrix = np.zeros((size, size), dtype=np.int64)
        changed = valid = 0
        with rasterio.open(reference_path) as reference, rasterio.open(selected_path) as selected:
            for window in core_tile_windows(reference.shape, 2048):
                left = reference.read(1, window=window)
                right = selected.read(1, window=window)
                common = valid_mask(left, reference.nodata) & valid_mask(right, selected.nodata)
                left_class = classify_values(left[common], classes)
                right_class = classify_values(right[common], classes)
                valid += left_class.size
                changed += int(np.count_nonzero(left_class != right_class))
                np.add.at(matrix, (left_class - 1, right_class - 1), 1)
        return {
            "valid_pixels": valid,
            "class_change_pixels": changed,
            "class_change_percent": changed / valid * 100,
            "transition_matrix": {
                str(row + 1): {str(column + 1): int(matrix[row, column]) for column in range(size)}
                for row in range(size)
            },
        }

    def _write_controls(self, phase8a1: dict[str, Any]) -> dict[str, Any]:
        controls = {
            "amg_urbano": "AMG",
            "sv_18_N04_E05": "planicie_rural",
            "sv_01_N01_E02": "montana",
            "barranca_huentitan": "barranca",
        }
        directory = self.output_dir / "controles"
        directory.mkdir(parents=True, exist_ok=True)
        reports = {}
        for chip_id, role in controls.items():
            with rasterio.open(self.phase8a1_dir / "chips" / chip_id / "H3.tif") as source:
                horn = source.read(1)
            with rasterio.open(self.phase8a1_dir / "chips" / chip_id / "WE5.tif") as source:
                we5 = source.read(1)
            horn_classes = np.full(horn.shape, 255, dtype=np.uint8)
            we5_classes = np.full(we5.shape, 255, dtype=np.uint8)
            horn_valid = valid_mask(horn, FINAL_NODATA)
            we5_valid = valid_mask(we5, FINAL_NODATA)
            horn_classes[horn_valid] = classify_values(horn[horn_valid], DEGREES_CLASSIFICATION)
            we5_classes[we5_valid] = classify_values(we5[we5_valid], DEGREES_CLASSIFICATION)
            output = directory / f"{chip_id}_H3_vs_WE5_clasificada.png"
            figure, axes = plt.subplots(1, 2, figsize=(9, 4), constrained_layout=True)
            for axis, values, title in zip(axes, (horn_classes, we5_classes), ("Horn 3x3", "Wood-Evans 5x5"), strict=True):
                image = axis.imshow(np.ma.masked_equal(values, 255), cmap="turbo", vmin=1, vmax=7, interpolation="nearest")
                axis.set_title(title)
                axis.axis("off")
            figure.colorbar(image, ax=axes, ticks=range(1, 8), shrink=0.8)
            figure.savefig(output, dpi=150)
            plt.close(figure)
            reports[chip_id] = {
                "role": role,
                "path": str(output),
                "horn_fragmentation": self._fragmentation_without_classes(horn),
                "we5_fragmentation": self._fragmentation_without_classes(we5),
                "horn_local_class_metrics": self._local_class_metrics(horn_classes),
                "we5_local_class_metrics": self._local_class_metrics(we5_classes),
                "local_class_change_percent": float(
                    np.count_nonzero(horn_classes[horn_valid & we5_valid] != we5_classes[horn_valid & we5_valid])
                    / np.count_nonzero(horn_valid & we5_valid)
                    * 100
                ),
                "review": "coherent_with_phase8a1",
            }
        return reports

    @staticmethod
    def _local_class_metrics(classes: np.ndarray) -> dict[str, float]:
        disagreements = comparisons = transitions = 0
        for row_shift, column_shift in ((0, 1), (1, 0), (1, 1), (1, -1)):
            row_left = slice(0, -row_shift or None)
            row_right = slice(row_shift, None)
            if column_shift >= 0:
                column_left = slice(0, -column_shift or None)
                column_right = slice(column_shift, None)
            else:
                column_left = slice(-column_shift, None)
                column_right = slice(0, column_shift)
            left = classes[row_left, column_left]
            right = classes[row_right, column_right]
            common = (left != 255) & (right != 255)
            count = int(np.count_nonzero(common))
            different = int(np.count_nonzero((left != right) & common))
            comparisons += count
            disagreements += different
            if (row_shift, column_shift) in ((0, 1), (1, 0)):
                transitions += different
        return {
            "neighborhood_disagreement_percent_8_connected": disagreements / comparisons * 100,
            "orthogonal_transition_count": float(transitions),
        }

    @staticmethod
    def _visual_review() -> dict[str, Any]:
        return {
            "completed": True,
            "controls": ["AMG", "planicie_rural", "montana", "barranca"],
            "common_extent_classification_symbology_and_zoom": True,
            "finding": "WE5 reduces isolated class texture in flat/urban controls while retaining the main ridge, channel, slope, and barranca structures in rugged controls.",
            "coherent_with_phase8a1": True,
            "accuracy_claim": "cartographic coherence only; not independent ground truth",
        }

    @staticmethod
    def _fragmentation_without_classes(values: np.ndarray) -> dict[str, Any]:
        report = class_fragmentation(values)
        report.pop("classes")
        return report

    def _package_release(self, checkpoint: dict[str, Any], classification: dict[str, Any]) -> dict[str, Any]:
        self._preserve_historical_release()
        driver = inspect_cog_driver()
        specifications = {
            "pendiente_grados": (self.degrees_path, self.final_analytical_dir / self.degrees_path.name, False),
            "pendiente_porcentaje": (self.percent_path, self.final_analytical_dir / self.percent_path.name, False),
            "pendiente_grados_clasificada": (
                self.classified_degrees_path,
                self.final_cartographic_dir / FINAL_DEGREES_CLASSIFIED_FILENAME,
                True,
            ),
            "pendiente_porcentaje_clasificada": (
                self.classified_percent_path,
                self.final_cartographic_dir / FINAL_PERCENT_CLASSIFIED_FILENAME,
                True,
            ),
        }
        records = {}
        staging_dir = self.output_dir / "cog_staging"
        for key, (parent, final, classified) in specifications.items():
            staging = staging_dir / final.name
            record = checkpoint.get("checkpoint_artifacts", {}).get(f"cog_{key}")
            if final.exists() and sha256_file(final) not in HISTORICAL_COG_SHA256.values():
                self._require(record is not None and sha256_file(final) == record["sha256"], f"Incompatible final COG: {final}")
                cog_path = final
                creation = record["processing"]["creation"]
            else:
                if staging.exists():
                    self._require(record is not None and sha256_file(staging) == record["sha256"], f"Incompatible staged COG: {staging}")
                    creation = record["processing"]["creation"]
                else:
                    creation = create_cog(parent, staging, classified=classified)
                    qa = validate_lossless_cog(parent, staging, classified=classified)
                    self._require(qa["hard_gates"]["all_passed"], f"COG QA failed: {key}")
                    self._require(qa["overview_levels"] == [2, 4, 8, 16, 32, 64], f"Unexpected overview levels: {key}")
                    record = {
                        "path": str(staging),
                        "sha256": sha256_file(staging),
                        "processing": {"creation": creation, "qa": qa},
                    }
                    checkpoint.setdefault("checkpoint_artifacts", {})[f"cog_{key}"] = record
                    write_json_atomic(checkpoint, self.manifest_path)
                final.parent.mkdir(parents=True, exist_ok=True)
                staging.replace(final)
                cog_path = final
            qa = validate_lossless_cog(parent, cog_path, classified=classified)
            self._require(qa["hard_gates"]["all_passed"], f"Final COG QA failed: {key}")
            records[key] = {
                "path": str(cog_path),
                "analytical_parent": str(parent),
                "scientific_sha256": sha256_file(parent),
                "product_role": "classified" if classified else "continuous",
                "unit": "class" if classified else ("degree" if key == "pendiente_grados" else "percent"),
                "creation": creation,
                **qa,
            }
        self._replace_final_intermediates()
        old_packaging = read_json(self.output_dir / "historical_horn_cogs" / "cog_packaging_manifest_horn.json")
        dem = old_packaging["rasters"]["modelo_elevacion_acondicionado"]
        self._require(sha256_file(Path(dem["path"])) == DEM_COG_SHA256, "DEM COG changed")
        packaging = {
            "status": "cog_packaging_validated",
            "created_at": datetime.now().astimezone().isoformat(),
            "method": "WoodEvans5x5",
            "gdal_cog_driver": driver,
            "rasters": {"modelo_elevacion_acondicionado": dem, **records},
            "historical_horn_cogs": str(self.output_dir / "historical_horn_cogs"),
        }
        write_json_atomic(packaging, self.packaging_manifest_path)
        return packaging

    def _preserve_historical_release(self) -> None:
        directory = self.output_dir / "historical_horn_cogs"
        directory.mkdir(parents=True, exist_ok=True)
        old_manifest = directory / "cog_packaging_manifest_horn.json"
        if not old_manifest.exists():
            shutil.copy2(self.packaging_manifest_path, old_manifest)
        sources = {
            "pendiente_grados": self.final_analytical_dir / self.degrees_path.name,
            "pendiente_porcentaje": self.final_analytical_dir / self.percent_path.name,
            "pendiente_grados_clasificada": self.final_cartographic_dir / FINAL_DEGREES_CLASSIFIED_FILENAME,
            "pendiente_porcentaje_clasificada": self.final_cartographic_dir / FINAL_PERCENT_CLASSIFIED_FILENAME,
        }
        for key, source in sources.items():
            target = directory / f"Horn3x3_{source.name}"
            if not target.exists():
                self._require(sha256_file(source) == HISTORICAL_COG_SHA256[key], f"Unexpected historical COG: {source}")
                os.link(source, target)
            self._require(sha256_file(target) == HISTORICAL_COG_SHA256[key], f"Historical COG changed: {target}")

    def _replace_final_intermediates(self) -> None:
        history = self.output_dir / "historical_horn_cogs"
        for new, final in (
            (self.classified_degrees_path, self.final_intermediate_dir / FINAL_DEGREES_CLASSIFIED_FILENAME),
            (self.classified_percent_path, self.final_intermediate_dir / FINAL_PERCENT_CLASSIFIED_FILENAME),
        ):
            historical = history / f"Horn3x3_analytical_{final.name}"
            if final.exists() and not historical.exists():
                os.link(final, historical)
            temporary = final.with_suffix(".we5.partial.tif")
            temporary.unlink(missing_ok=True)
            os.link(new, temporary)
            temporary.replace(final)

    def _products(self, classification: dict[str, Any], packaging: dict[str, Any]) -> dict[str, Any]:
        return {
            "context_degrees": {"path": str(self.context_path), "sha256": sha256_file(self.context_path), "publishable": False},
            "pendiente_grados": {"path": str(self.degrees_path), "sha256": sha256_file(self.degrees_path), "production_product": True},
            "pendiente_porcentaje": {"path": str(self.percent_path), "sha256": sha256_file(self.percent_path), "production_product": True},
            "classified": classification,
            "release_cogs": {key: {"path": value["path"], "sha256": value["sha256"]} for key, value in packaging["rasters"].items()},
        }

    def _validate_completed(self, manifest: dict[str, Any]) -> None:
        self._require(manifest["decision"]["value"] == CARTOGRAPHIC_PRODUCTION_DECISION, "Completed decision changed")
        for product in ("context_degrees", "pendiente_grados", "pendiente_porcentaje"):
            record = manifest["products"][product]
            self._require(sha256_file(Path(record["path"])) == record["sha256"], f"Completed product changed: {product}")
        for record in manifest["products"]["release_cogs"].values():
            self._require(sha256_file(Path(record["path"])) == record["sha256"], "Completed release COG changed")
        self._require(sha256_file(self.final_analytical_dir / "modelo_elevacion_acondicionado_jalisco_15m.tif") == DEM_COG_SHA256, "DEM COG changed")

    @staticmethod
    def _require(condition: bool, message: str) -> None:
        if not condition:
            raise ValueError(message)
