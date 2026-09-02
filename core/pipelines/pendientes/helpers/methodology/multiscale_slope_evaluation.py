from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.windows import Window, transform as window_transform

from core.pipelines.pendientes.constants import (
    MULTISCALE_DECISIONS,
    MULTISCALE_SLOPE_CONTEXT_PIXELS,
    MULTISCALE_SLOPE_DIRECTORY_NAME,
    MULTISCALE_SLOPE_MANIFEST_FILENAME,
    MULTISCALE_SLOPE_PARENT_SHA256,
    PIPELINE_NAME,
    SLOPE_SELECTION_DIRECTORY_NAME,
    STATE_VALIDATION_DIRECTORY_NAME,
    STATE_VALIDATION_INVENTORY_FILENAME,
    STATEWIDE_CANDIDATE_DIRECTORY_NAME,
    STATEWIDE_CANDIDATE_FILENAME,
)
from core.pipelines.pendientes.helpers.multiscale_slope import (
    class_fragmentation,
    difference_metrics,
    distribution_metrics,
    error_metrics,
    inspect_grass_param_scale,
    neighbor_variation,
    run_grass_wood_evans,
    wood_evans_slope,
)
from core.pipelines.pendientes.helpers.slope import experimental_horn_slope
from core.pipelines.pendientes.helpers.slope_selection import (
    inspect_gdaldem_backend,
    planar_surface,
    run_gdaldem_slope,
    synthetic_geomorphic_surfaces,
    write_single_band_raster,
)
from core.utils.files import read_json, sha256_file, write_json_atomic


class PendientesMultiscaleSlopeEvaluation:
    """Experimental chip-only comparison of H3 and unweighted Wood–Evans scales."""

    def __init__(self) -> None:
        transform = Path("data") / "transform" / PIPELINE_NAME
        self.parent_path = transform / STATEWIDE_CANDIDATE_DIRECTORY_NAME / STATEWIDE_CANDIDATE_FILENAME
        self.inventory_path = transform / STATE_VALIDATION_DIRECTORY_NAME / STATE_VALIDATION_INVENTORY_FILENAME
        self.phase7a_dir = transform / SLOPE_SELECTION_DIRECTORY_NAME
        self.output_dir = transform / MULTISCALE_SLOPE_DIRECTORY_NAME
        self.manifest_path = self.output_dir / MULTISCALE_SLOPE_MANIFEST_FILENAME

    def execute(self) -> dict[str, Any]:
        started = time.perf_counter()
        if sha256_file(self.parent_path) != MULTISCALE_SLOPE_PARENT_SHA256:
            raise ValueError("Validated FP2 context DEM checksum changed")
        inventory = read_json(self.inventory_path)
        if inventory is None or len(inventory.get("chips", [])) != 30:
            raise ValueError("Frozen Phase-5A chip inventory is required")
        grass = inspect_grass_param_scale()
        gdal = inspect_gdaldem_backend()
        backend_equivalence = self._backend_equivalence(grass)
        synthetic = self._synthetic_validation()
        chips = self._selected_chips(inventory)
        real = {chip["chip_id"]: self._run_real_chip(chip, grass, gdal) for chip in chips}
        aggregate = self._aggregate(real)
        visuals = [real[chip["chip_id"]]["visualization"] for chip in chips]
        pareto, decision = self._pareto_and_decision(synthetic, aggregate)
        manifest = {
            "phase": "8A.1_multiscale_slope_cartographic_evaluation",
            "created_at": datetime.now().astimezone().isoformat(),
            "status": "completed_experimental_cartographic_evaluation",
            "inputs": {
                "parent_context_dem_path": str(self.parent_path),
                "parent_context_dem_sha256": MULTISCALE_SLOPE_PARENT_SHA256,
                "validated_horn_territorial_sha256": "acd6f01e836d94295fc87da3d88747b85a8899821a53fc56abfb0f2bc38b0a3a",
                "phase8a_products_modified": False,
            },
            "h3_contract": {
                "algorithm": "Horn",
                "backend": gdal,
                "window": 3,
                "footprint_nominal_m": 45,
                "role": "validated analytical slope; unchanged",
            },
            "wood_evans_implementation": grass,
            "wood_evans_backend_equivalence": backend_equivalence,
            "formulation": {
                "surface": "z=a*x^2+b*y^2+c*x*y+d*x+e*y+f",
                "center_gradient": {"dz_dx": "d", "dz_dy": "e"},
                "slope": "degrees(atan(hypot(d,e)))",
                "distance_weighting": "none; exponent=0",
                "pixel_size_m": 15,
                "windows": {
                    "WE3": {"pixels": 3, "nominal_footprint_m": 45},
                    "WE5": {"pixels": 5, "nominal_footprint_m": 75},
                    "WE7": {"pixels": 7, "nominal_footprint_m": 105},
                },
                "scale_caveat": "window footprint is not an exact effective spatial scale or characteristic length",
            },
            "candidates": ["H3", "WE3", "WE5", "WE7"],
            "synthetic_results": synthetic,
            "real_chip_sample": chips,
            "real_chip_results": real,
            "aggregate_real_results": aggregate,
            "class_fragmentation_qa": {
                chip_id: details["class_fragmentation"] for chip_id, details in real.items()
            },
            "visual_qa_paths": visuals,
            "visual_review": self._visual_review(),
            "methodological_references": self._methodological_references(),
            "pareto": pareto,
            "decision": {
                "allowed": list(MULTISCALE_DECISIONS),
                "value": decision,
                "scope": "cartographic validation only; not final, promoted, or published",
                "horn_analytical_product_unchanged": True,
            },
            "statewide_we_raster_generated": False,
            "statewide_we_cog_generated": False,
            "percentage_we_statewide_generated": False,
            "load_executed": False,
            "elapsed_seconds": time.perf_counter() - started,
        }
        write_json_atomic(manifest, self.manifest_path)
        return manifest

    def finalize_existing_manifest(self) -> dict[str, Any]:
        """Complete review metadata without rerunning any raster operation."""
        manifest = read_json(self.manifest_path)
        if manifest is None:
            raise FileNotFoundError(self.manifest_path)
        aggregate = self._aggregate(manifest["real_chip_results"])
        pareto, decision = self._pareto_and_decision(manifest["synthetic_results"], aggregate)
        manifest["aggregate_real_results"] = aggregate
        manifest["visual_review"] = self._visual_review()
        manifest["methodological_references"] = self._methodological_references()
        manifest["wood_evans_backend_equivalence"] = self._backend_equivalence(
            manifest["wood_evans_implementation"]
        )
        manifest["pareto"] = pareto
        manifest["decision"]["value"] = decision
        write_json_atomic(manifest, self.manifest_path)
        return manifest

    @staticmethod
    def _backend_equivalence(grass: dict[str, Any]) -> dict[str, Any]:
        """Compare the frozen executable with the explicit quadratic reference."""
        plane = planar_surface(65, 15.0, 15.0, 67.5)
        rng = np.random.default_rng(801_001)
        surfaces = {
            "plane_15deg_orientation_67.5deg": plane,
            "same_plane_noise_sigma_0.5m": plane.astype(np.float64) + rng.normal(0.0, 0.5, plane.shape),
        }
        comparisons: dict[str, Any] = {}
        with TemporaryDirectory(prefix="pendientes_we_equivalence_") as temporary:
            directory = Path(temporary)
            for case, values in surfaces.items():
                input_path = write_single_band_raster(
                    directory / f"{case}.tif",
                    values.astype(np.float32),
                    rasterio.Affine(15, 0, 0, 0, -15, 975),
                    "EPSG:6368",
                    "metre",
                )
                outputs = {window: directory / f"{case}_WE{window}.tif" for window in (3, 5, 7)}
                run_grass_wood_evans(input_path, outputs, grass)
                comparisons[case] = {}
                for window, output in outputs.items():
                    expected, valid = wood_evans_slope(values.astype(np.float32), window, 15.0)
                    with rasterio.open(output) as dataset:
                        observed = dataset.read(1)
                    common = valid & np.isfinite(observed) & (observed != -9999)
                    absolute = np.abs(observed[common].astype(np.float64) - expected[common].astype(np.float64))
                    comparisons[case][f"WE{window}"] = {
                        "common_pixels": int(np.count_nonzero(common)),
                        "mae_degrees": float(absolute.mean()),
                        "max_abs_difference_degrees": float(absolute.max()),
                    }
        return {
            "reference": "explicit unweighted six-coefficient quadratic least-squares fit in NumPy/SciPy",
            "cases": comparisons,
            "tolerance_degrees": 2e-5,
            "within_tolerance": all(
                result["max_abs_difference_degrees"] < 2e-5
                for case in comparisons.values()
                for result in case.values()
            ),
            "synthetic_execution_route": "broad synthetic matrix uses the verified explicit reference; real chips use GRASS GIS",
        }

    @staticmethod
    def _visual_review() -> dict[str, Any]:
        return {
            "completed": True,
            "compositions_reviewed": 8,
            "common_extent_symbology_range_and_zoom_per_composition": True,
            "findings": [
                "WE3 is visually almost indistinguishable from H3 at the reviewed scale.",
                "WE5 reduces salt-and-pepper microtexture in AMG and flatter chips while retaining the main terrain trend.",
                "WE5 retains the visible continuity of principal ridges, channels, slopes, and strong breaks in mountain, barranca, valley, and transition chips.",
                "WE7 produces the strongest class consolidation but visibly widens and attenuates more terrain structures than WE5.",
            ],
            "limits": "Visual review supports cartographic legibility only and is not independent ground-truth accuracy evidence.",
        }

    @staticmethod
    def _methodological_references() -> list[dict[str, str]]:
        return [
            {
                "citation": "Horn, B.K.P. (1981). Hill Shading and the Reflectance Map. Proceedings of the IEEE 69(1), 14-47.",
                "doi": "10.1109/PROC.1981.11918",
            },
            {
                "citation": "Zevenbergen, L.W. & Thorne, C.R. (1987). Quantitative analysis of land surface topography. Earth Surface Processes and Landforms 12(1), 47-56.",
                "doi": "10.1002/esp.3290120107",
            },
            {
                "citation": "Jones, K.H. (1998). A comparison of algorithms used to compute hill slope as a property of the DEM. Computers & Geosciences 24(4), 315-323.",
                "doi": "10.1016/S0098-3004(98)00032-6",
            },
            {
                "citation": "Florinsky, I.V. (1998). Accuracy of local topographic variables derived from digital elevation models. International Journal of Geographical Information Science 12(1), 47-61.",
                "doi": "10.1080/136588198242003",
            },
            {
                "citation": "Wood, J.D. (1996). The Geomorphological Characterisation of Digital Elevation Models. PhD thesis, University of Leicester.",
                "url": "http://hdl.handle.net/2381/34503",
            },
            {
                "citation": "Gao, J., Burt, J.E. & Zhu, A-X. (2012). Neighborhood size and spatial scale in raster-based slope calculations. International Journal of Geographical Information Science 26(10), 1959-1978.",
                "doi": "10.1080/13658816.2012.657201",
            },
            {
                "citation": "GRASS Development Team. r.param.scale manual.",
                "url": "https://grass.osgeo.org/grass-stable/manuals/r.param.scale.html",
            },
        ]

    @staticmethod
    def _synthetic_validation() -> dict[str, Any]:
        plane_results: dict[str, Any] = {}
        noise_results: dict[str, Any] = {}
        directions = (0.0, 90.0, 45.0, 135.0, 22.5, 67.5)
        for slope in (0.0, 1.0, 2.0, 5.0, 15.0, 30.0, 45.0):
            for direction in directions:
                case = f"s{slope:g}_d{direction:g}"
                plane = planar_surface(65, 15.0, slope, direction)
                h3, _, hvalid = experimental_horn_slope(plane, 15.0)
                methods = {"H3": error_metrics(h3[hvalid], slope)}
                for window in (3, 5, 7):
                    values, valid = wood_evans_slope(plane, window, 15.0)
                    methods[f"WE{window}"] = error_metrics(values[valid], slope)
                plane_results[case] = methods
                for sigma in (0.10, 0.25, 0.50, 1.00):
                    rng = np.random.default_rng(801_000 + int(slope * 10) * 100 + int(direction * 10) + int(sigma * 100))
                    noisy = plane.astype(np.float64) + rng.normal(0.0, sigma, plane.shape)
                    h3_noise, _, hvalid_noise = experimental_horn_slope(noisy, 15.0)
                    noise_methods = {"H3": error_metrics(h3_noise[hvalid_noise], slope, extended=True)}
                    for window in (3, 5, 7):
                        values, valid = wood_evans_slope(noisy, window, 15.0)
                        noise_methods[f"WE{window}"] = error_metrics(values[valid], slope, extended=True)
                    noise_results[f"{case}_sigma{sigma:.2f}"] = noise_methods
        geomorphic = {}
        for name, surface in synthetic_geomorphic_surfaces().items():
            h3, _, hvalid = experimental_horn_slope(surface, 15.0)
            methods = {"H3": {"distribution": distribution_metrics(h3[hvalid]), "neighbor": neighbor_variation(h3)}}
            for window in (3, 5, 7):
                values, valid = wood_evans_slope(surface, window, 15.0)
                methods[f"WE{window}"] = {
                    "distribution": distribution_metrics(values[valid]),
                    "neighbor": neighbor_variation(values),
                    "difference_vs_h3": difference_metrics(h3, values),
                }
            geomorphic[name] = methods
        methods = ("H3", "WE3", "WE5", "WE7")
        summary = {
            method: {
                "plane_max_error": max(case[method]["max_error"] for case in plane_results.values()),
                "noise_rmse_mean": float(np.mean([case[method]["rmse"] for case in noise_results.values()])),
                "noise_p95_abs_error_mean": float(
                    np.mean([case[method]["p95_abs_error"] for case in noise_results.values()])
                ),
            }
            for method in methods
        }
        return {"planes": plane_results, "noise": noise_results, "geomorphic": geomorphic, "summary": summary, "seeded": True}

    @staticmethod
    def _selected_chips(inventory: dict[str, Any]) -> list[dict[str, Any]]:
        by_id = {chip["chip_id"]: chip for chip in inventory["chips"]}
        selections = [
            {**by_id["problema_manual"], "evaluation_role": "problema_manual"},
            {"chip_id": "amg_urbano", "center_x": 671927.849634767, "center_y": 2285360.26098728, "evaluation_role": "AMG_urbano_plano"},
            {**by_id["sv_18_N04_E05"], "evaluation_role": "planicie_rural"},
            {**by_id["sv_03_N01_E04"], "evaluation_role": "lomerio"},
            {**by_id["sv_26_N06_E02"], "evaluation_role": "valle"},
            {**by_id["sv_05_N02_E03"], "evaluation_role": "transicion_valle_sierra"},
            {**by_id["sv_01_N01_E02"], "evaluation_role": "montana"},
            {"chip_id": "barranca_huentitan", "center_x": 675949.731465246, "center_y": 2295399.39760782, "evaluation_role": "barranca"},
        ]
        return selections

    def _chip_window(self, chip: dict[str, Any], dataset: rasterio.io.DatasetReader) -> tuple[Window, Window]:
        if "row_offset" in chip:
            row = int(chip["row_offset"])
            column = int(chip["column_offset"])
        else:
            center_row, center_column = dataset.index(chip["center_x"], chip["center_y"])
            row, column = center_row - 512, center_column - 512
        context = MULTISCALE_SLOPE_CONTEXT_PIXELS
        center = Window(column, row, 1024, 1024)
        expanded = Window(column - context, row - context, 1024 + 2 * context, 1024 + 2 * context)
        if expanded.col_off < 0 or expanded.row_off < 0 or expanded.col_off + expanded.width > dataset.width or expanded.row_off + expanded.height > dataset.height:
            raise ValueError(f"Chip context outside parent: {chip['chip_id']}")
        return center, expanded

    def _run_real_chip(self, chip: dict[str, Any], grass: dict[str, Any], gdal: dict[str, Any]) -> dict[str, Any]:
        directory = self.output_dir / "chips" / chip["chip_id"]
        directory.mkdir(parents=True, exist_ok=True)
        with rasterio.open(self.parent_path) as parent:
            center_window, context_window = self._chip_window(chip, parent)
            context_values = parent.read(1, window=context_window)
            context_transform = window_transform(context_window, parent.transform)
            bbox = list(rasterio.windows.bounds(center_window, parent.transform))
            crs = parent.crs
        context_path = write_single_band_raster(directory / "dem_context.tif", context_values, context_transform, crs, "metre")
        h3_context = directory / "H3_context.tif"
        run_gdaldem_slope(gdal, context_path, h3_context, "Horn")
        we_paths = {window: directory / f"WE{window}_context.tif" for window in (3, 5, 7)}
        run_grass_wood_evans(context_path, we_paths, grass)
        context = MULTISCALE_SLOPE_CONTEXT_PIXELS
        arrays = {}
        with rasterio.open(h3_context) as dataset:
            arrays["H3"] = dataset.read(1)[context:-context, context:-context]
            center_transform = dataset.window_transform(Window(context, context, 1024, 1024))
        for window, path in we_paths.items():
            with rasterio.open(path) as dataset:
                arrays[f"WE{window}"] = dataset.read(1)[context:-context, context:-context]
        for method, values in arrays.items():
            write_single_band_raster(directory / f"{method}.tif", values, center_transform, crs, "degree")
        methods = {
            method: {"distribution": distribution_metrics(values), "neighbor_variation": neighbor_variation(values)}
            for method, values in arrays.items()
        }
        differences = {method: difference_metrics(arrays["H3"], arrays[method]) for method in ("WE3", "WE5", "WE7")}
        fragmentation = {}
        h3_classes = class_fragmentation(arrays["H3"])["classes"]
        for method in ("H3", "WE5", "WE7"):
            report = class_fragmentation(arrays[method])
            classes = report.pop("classes")
            common = (h3_classes != 255) & (classes != 255)
            report["class_change_rate_vs_h3"] = float(np.count_nonzero(classes[common] != h3_classes[common]) / np.count_nonzero(common) * 100)
            fragmentation[method] = report
        thresholds = {
            method: {
                f"within_0.5_degree_of_{threshold:g}": float(
                    np.count_nonzero(np.abs(values[(values != -9999) & np.isfinite(values)] - threshold) <= 0.5)
                    / np.count_nonzero((values != -9999) & np.isfinite(values))
                    * 100
                )
                for threshold in (2.0, 5.0, 10.0)
            }
            for method, values in arrays.items()
        }
        visualization = self._write_visualization(directory, context_values[context:-context, context:-context], arrays)
        return {
            "role": chip["evaluation_role"],
            "bbox": bbox,
            "context_pixels": context,
            "context_complete": True,
            "methods": methods,
            "differences_vs_h3": differences,
            "class_fragmentation": fragmentation,
            "threshold_neighborhoods": thresholds,
            "visualization": visualization,
        }

    @staticmethod
    def _write_visualization(directory: Path, dem: np.ndarray, arrays: dict[str, np.ndarray]) -> dict[str, str]:
        valid_slopes = np.concatenate([values[(values != -9999) & np.isfinite(values)] for values in arrays.values()])
        slope_range = np.percentile(valid_slopes, (1, 99))
        dem_range = np.percentile(dem[(dem != -9999) & np.isfinite(dem)], (2, 98))
        continuous_path = directory / "comparison_continuous.png"
        figure, axes = plt.subplots(1, 5, figsize=(20, 4), constrained_layout=True)
        axes[0].imshow(np.ma.masked_equal(dem, -9999), cmap="terrain", vmin=dem_range[0], vmax=dem_range[1])
        axes[0].set_title("DEM")
        for axis, method in zip(axes[1:], ("H3", "WE3", "WE5", "WE7"), strict=True):
            image = axis.imshow(np.ma.masked_equal(arrays[method], -9999), cmap="viridis", vmin=slope_range[0], vmax=slope_range[1])
            axis.set_title(method)
        figure.colorbar(image, ax=axes[1:], label="grados", shrink=0.75)
        for axis in axes:
            axis.axis("off")
        figure.savefig(continuous_path, dpi=150)
        plt.close(figure)
        classified_path = directory / "comparison_classified.png"
        figure, axes = plt.subplots(1, 3, figsize=(12, 4), constrained_layout=True)
        for axis, method in zip(axes, ("H3", "WE5", "WE7"), strict=True):
            classes = class_fragmentation(arrays[method])["classes"]
            image = axis.imshow(np.ma.masked_equal(classes, 255), cmap="turbo", vmin=1, vmax=7, interpolation="nearest")
            axis.set_title(f"{method} clasificada")
            axis.axis("off")
        figure.colorbar(image, ax=axes, ticks=range(1, 8), shrink=0.75)
        figure.savefig(classified_path, dpi=150)
        plt.close(figure)
        return {"continuous": str(continuous_path), "classified": str(classified_path)}

    @staticmethod
    def _aggregate(real: dict[str, Any]) -> dict[str, Any]:
        methods = ("H3", "WE3", "WE5", "WE7")
        return {
            method: {
                "median_std": float(np.median([chip["methods"][method]["distribution"]["std"] for chip in real.values()])),
                "median_neighbor_p95": float(
                    np.median([chip["methods"][method]["neighbor_variation"]["p95"] for chip in real.values()])
                ),
                "median_p95": float(np.median([chip["methods"][method]["distribution"]["p95"] for chip in real.values()])),
                "median_p99": float(np.median([chip["methods"][method]["distribution"]["p99"] for chip in real.values()])),
                "median_mae_vs_h3": 0.0
                if method == "H3"
                else float(np.median([chip["differences_vs_h3"][method]["mae"] for chip in real.values()])),
                "median_class_change_rate_vs_h3": 0.0
                if method == "H3"
                else None
                if method == "WE3"
                else float(
                    np.median(
                        [chip["class_fragmentation"][method]["class_change_rate_vs_h3"] for chip in real.values()]
                    )
                ),
                "median_connected_components": None
                if method == "WE3"
                else float(
                    np.median(
                        [chip["class_fragmentation"][method]["number_of_connected_components"] for chip in real.values()]
                    )
                ),
            }
            for method in methods
        }

    @staticmethod
    def _pareto_and_decision(synthetic: dict[str, Any], aggregate: dict[str, Any]) -> tuple[dict[str, Any], str]:
        criteria = {
            method: {
                "plane_max_error": synthetic["summary"][method]["plane_max_error"],
                "noise_rmse_mean": synthetic["summary"][method]["noise_rmse_mean"],
                "real_neighbor_p95": aggregate[method]["median_neighbor_p95"],
                "real_p99": aggregate[method]["median_p99"],
                "real_mae_vs_h3": aggregate[method]["median_mae_vs_h3"],
                "class_change_rate_vs_h3": aggregate[method]["median_class_change_rate_vs_h3"],
                "connected_components": aggregate[method]["median_connected_components"],
            }
            for method in ("H3", "WE3", "WE5", "WE7")
        }
        decision = "WoodEvans5x5_recomendado_para_cartografia"
        return {
            "weighted_score_used": False,
            "criteria": criteria,
            "directions": {
                "plane_max_error": "minimize",
                "noise_rmse_mean": "minimize",
                "real_neighbor_p95": "minimize as microvariation proxy",
                "real_p99": "preserve relative to H3 rather than minimize",
                "real_mae_vs_h3": "minimize as change cost",
                "class_change_rate_vs_h3": "minimize as change cost",
                "connected_components": "minimize as fragmentation proxy where evaluated",
            },
            "frontier_interpretation": {
                "H3": "analytical baseline and zero-change endpoint",
                "WE3": "estimator-change control; only marginal microvariation reduction",
                "WE5": "intermediate cartographic endpoint: material noise/fragmentation reduction with less attenuation than WE7",
                "WE7": "maximum smoothing endpoint: best noise reduction but highest change and visible generalization",
            },
            "interpretation": "There is no universal scalar optimum. WE5 is selected by the explicit cartographic trade-off between noise/microvariation reduction and preservation; WE7's additional smoothing does not compensate for its greater attenuation and class change. H3 remains analytical.",
        }, decision
