from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
from shapely import make_valid
from shapely.geometry import MultiPolygon
from shapely.ops import unary_union

from core.pipelines.edafologia.constants import (
    CANONICAL_SRID,
    LIMIT_SOURCE_KEYS,
    MUNICIPAL_BOUNDARY_SOURCES,
    MUNICIPAL_OVERLAY_OUTPUT_LAYER,
    OVERLAY_COLUMNS,
    PIPELINE_VERSION,
    SMALL_FRAGMENT_THRESHOLDS_M2,
)
from core.pipelines.edafologia.helpers.load_inputs import (
    read_transform_manifest,
    read_transformed_layer,
    validate_transform_manifest,
    validate_transformed_frame,
)
from core.pipelines.edafologia.helpers.boundaries import validate_municipal_keys
from core.pipelines.edafologia.helpers.transform_geometry import polygonal_part
from core.pipelines.edafologia.helpers.transform_inputs import read_boundary_layers
from core.utils.files import sha256_file


def valid_multipolygon(geometry: Any) -> tuple[MultiPolygon | None, bool]:
    if geometry is None or geometry.is_empty:
        return None, False
    repaired = False
    value = geometry
    if not value.is_valid:
        value = make_valid(value)
        repaired = True
    polygonal = polygonal_part(value)
    if polygonal is None or polygonal.is_empty:
        return None, repaired
    if not polygonal.is_valid:
        polygonal = make_valid(polygonal)
        repaired = True
        polygonal = polygonal_part(polygonal)
    if polygonal is None or polygonal.is_empty or not polygonal.is_valid or polygonal.area <= 0:
        return None, repaired
    return polygonal, repaired


def source_identity(gdf: gpd.GeoDataFrame) -> tuple[str, str]:
    versions = gdf["source_version"].dropna().astype(str).unique().tolist()
    hashes = gdf["source_file_sha256"].dropna().astype(str).unique().tolist()
    if len(versions) != 1 or len(hashes) != 1:
        raise ValueError("Overlay input must contain exactly one source_version and source_file_sha256")
    return versions[0], hashes[0]


def read_overlay_inputs(transform_manifest_path: Path) -> dict[str, Any]:
    transform_manifest = read_transform_manifest(transform_manifest_path)
    validate_transform_manifest(transform_manifest, transform_manifest_path)
    edafologias = read_transformed_layer(transform_manifest)
    validate_transformed_frame(edafologias, transform_manifest)

    extract_manifest_path = Path(str(transform_manifest["extract_manifest_path"]))
    extract_manifest = json.loads(extract_manifest_path.read_text(encoding="utf-8"))
    boundaries_iieg, boundaries_inegi, boundary_validations = read_boundary_layers(extract_manifest)
    return {
        "transform_manifest": transform_manifest,
        "transform_manifest_path": transform_manifest_path,
        "extract_manifest": extract_manifest,
        "extract_manifest_path": extract_manifest_path,
        "edafologias": edafologias,
        "boundaries": {"iieg": boundaries_iieg, "inegi": boundaries_inegi},
        "boundary_validations": boundary_validations,
    }


def _candidate_pairs(source: gpd.GeoDataFrame, municipalities: gpd.GeoDataFrame) -> list[tuple[int, int]]:
    query = source.sindex.query(municipalities.geometry, predicate="intersects")
    if query.size == 0:
        return []
    return [(int(source_idx), int(municipality_idx)) for municipality_idx, source_idx in zip(query[0], query[1])]


def _municipal_overlap_area(municipalities: gpd.GeoDataFrame) -> float:
    overlaps: list[float] = []
    index_pairs = municipalities.sindex.query(municipalities.geometry, predicate="intersects")
    for left_idx, right_idx in zip(index_pairs[0], index_pairs[1]):
        if int(left_idx) >= int(right_idx):
            continue
        area = (
            municipalities.geometry.iloc[int(left_idx)].intersection(municipalities.geometry.iloc[int(right_idx)]).area
        )
        if area > 0:
            overlaps.append(float(area))
    return float(sum(overlaps))


def _dissolve_records(records: list[dict[str, Any]]) -> gpd.GeoDataFrame:
    if not records:
        return gpd.GeoDataFrame(
            columns=[*OVERLAY_COLUMNS, "geometry"], geometry="geometry", crs=f"EPSG:{CANONICAL_SRID}"
        )
    frame = gpd.GeoDataFrame(records, geometry="geometry", crs=f"EPSG:{CANONICAL_SRID}")
    keys = ["source_version", "source_objectid", "source_file_sha256", "fuente_limite_clave", "municipality_id"]
    dissolved = frame.dissolve(
        by=keys, as_index=False, aggfunc={"source_area_m2": "first", "municipality_area_m2": "first"}
    )
    dissolved["geometry"] = dissolved.geometry.map(lambda geometry: polygonal_part(unary_union([geometry])))
    dissolved = dissolved.loc[~(dissolved.geometry.isna() | dissolved.geometry.is_empty)].copy()
    dissolved["area_m2"] = dissolved.geometry.area.astype(float)
    dissolved = dissolved.loc[dissolved["area_m2"] > 0].copy()
    dissolved["area_ha"] = dissolved["area_m2"] / 10_000
    dissolved["pct_poligono_fuente"] = 100 * dissolved["area_m2"] / dissolved["source_area_m2"]
    dissolved["pct_municipio_total"] = 100 * dissolved["area_m2"] / dissolved["municipality_area_m2"]
    dissolved["pct_cobertura_edafologica"] = dissolved["pct_municipio_total"]
    return dissolved[[*OVERLAY_COLUMNS, "geometry"]]


def calculate_overlay_for_source(
    edafologias: gpd.GeoDataFrame,
    municipalities: gpd.GeoDataFrame,
    fuente_limite_clave: str,
) -> tuple[gpd.GeoDataFrame, dict[str, Any]]:
    if edafologias.crs is None or edafologias.crs.to_epsg() != CANONICAL_SRID:
        raise ValueError("Edafologia overlay input must be EPSG:6368")
    if municipalities.crs is None or municipalities.crs.to_epsg() != CANONICAL_SRID:
        raise ValueError(f"Municipal boundary input {fuente_limite_clave} must be EPSG:6368")
    if fuente_limite_clave not in LIMIT_SOURCE_KEYS:
        raise ValueError(f"Unsupported boundary source: {fuente_limite_clave}")
    validate_municipal_keys(municipalities, expected_count=len(municipalities))

    municipal_overlap_area = _municipal_overlap_area(municipalities)
    if municipal_overlap_area > 0:
        raise ValueError(
            f"Municipal boundary layer {fuente_limite_clave} has positive overlaps: {municipal_overlap_area}"
        )

    source = edafologias.reset_index(drop=True).copy()
    muni = municipalities.reset_index(drop=True).copy()
    source["source_area_m2"] = source.geometry.area.astype(float)
    muni["municipality_area_m2"] = muni.geometry.area.astype(float)
    if (source["source_area_m2"] <= 0).any() or (muni["municipality_area_m2"] <= 0).any():
        raise ValueError("Overlay denominators must be positive")

    records: list[dict[str, Any]] = []
    repaired_count = 0
    non_polygonal_discarded = 0
    non_positive_discarded = 0
    null_empty_discarded = 0
    for source_idx, municipality_idx in _candidate_pairs(source, muni):
        source_row = source.iloc[source_idx]
        muni_row = muni.iloc[municipality_idx]
        intersection = source_row.geometry.intersection(muni_row.geometry)
        if intersection is None or intersection.is_empty:
            null_empty_discarded += 1
            continue
        polygonal, repaired = valid_multipolygon(intersection)
        repaired_count += int(repaired)
        if polygonal is None:
            non_polygonal_discarded += 1
            continue
        if polygonal.area <= 0:
            non_positive_discarded += 1
            continue
        records.append(
            {
                "source_version": str(source_row["source_version"]),
                "source_objectid": int(source_row["source_objectid"]),
                "source_file_sha256": str(source_row["source_file_sha256"]),
                "fuente_limite_clave": fuente_limite_clave,
                "municipality_id": int(muni_row["cve_mun"]),
                "source_area_m2": float(source_row["source_area_m2"]),
                "municipality_area_m2": float(muni_row["municipality_area_m2"]),
                "geometry": polygonal,
            }
        )

    output = _dissolve_records(records)
    validate_overlay_frame(output)
    metrics = {
        "input_features": int(len(source)),
        "municipalities": int(len(muni)),
        "candidate_pairs": len(_candidate_pairs(source, muni)),
        "raw_polygonal_fragments": len(records),
        "final_fragments": int(len(output)),
        "null_empty_discarded": null_empty_discarded,
        "non_polygonal_discarded": non_polygonal_discarded,
        "non_positive_discarded": non_positive_discarded,
        "geometries_repaired": repaired_count,
        "municipal_positive_overlap_area_m2": municipal_overlap_area,
        "small_fragments": small_fragment_profile(output, float(muni["municipality_area_m2"].sum())),
        "territorial_closure": territorial_closure(output, muni),
    }
    return output, metrics


def validate_overlay_frame(gdf: gpd.GeoDataFrame) -> None:
    if gdf.crs is None or gdf.crs.to_epsg() != CANONICAL_SRID:
        raise ValueError("Overlay output must be EPSG:6368")
    if gdf.geometry.isna().any() or gdf.geometry.is_empty.any():
        raise ValueError("Overlay output contains null or empty geometries")
    if (~gdf.geometry.is_valid).any():
        raise ValueError("Overlay output contains invalid geometries")
    if (gdf.geometry.area <= 0).any() or (gdf["area_m2"] <= 0).any():
        raise ValueError("Overlay output contains non-positive areas")
    geometry_types = sorted(gdf.geometry.geom_type.unique().tolist())
    if geometry_types != ["MultiPolygon"]:
        raise ValueError(f"Overlay output must contain only MultiPolygon geometries: {geometry_types}")
    key_columns = ["source_version", "source_objectid", "fuente_limite_clave", "municipality_id"]
    if gdf.duplicated(key_columns).any():
        raise ValueError("Overlay output contains duplicated logical keys")
    if (gdf[["pct_poligono_fuente", "pct_municipio_total", "pct_cobertura_edafologica"]] < 0).any().any():
        raise ValueError("Overlay output contains negative percentages")


def small_fragment_profile(gdf: gpd.GeoDataFrame, territorial_area_m2: float) -> dict[str, Any]:
    areas = gdf["area_m2"].astype(float)
    total_area = float(areas.sum())
    profile: dict[str, Any] = {
        "total_fragments": int(len(gdf)),
        "total_area_m2": total_area,
        "thresholds": {},
        "distribution_m2": {},
    }
    for threshold in SMALL_FRAGMENT_THRESHOLDS_M2:
        mask = areas < threshold
        area_sum = float(areas.loc[mask].sum())
        profile["thresholds"][str(threshold)] = {
            "count": int(mask.sum()),
            "pct_fragments": float(100 * mask.sum() / len(gdf)) if len(gdf) else 0.0,
            "area_m2": area_sum,
            "pct_territorial_area": float(100 * area_sum / territorial_area_m2) if territorial_area_m2 else 0.0,
        }
    percentiles = [0, 1, 5, 25, 50, 75, 95, 99, 100]
    values = areas.quantile([p / 100 for p in percentiles]).to_dict() if len(areas) else {}
    for percentile in percentiles:
        key = str(percentile)
        profile["distribution_m2"][key] = float(values.get(percentile / 100, 0.0))
    return profile


def territorial_closure(gdf: gpd.GeoDataFrame, municipalities: gpd.GeoDataFrame) -> dict[str, Any]:
    municipal_areas = municipalities.assign(municipality_id=municipalities["cve_mun"].astype(int)).set_index(
        "municipality_id"
    )
    municipal_area_by_id = municipal_areas.geometry.area.astype(float)
    area_by_municipality = gdf.groupby("municipality_id")["area_m2"].sum()
    coverage = (100 * area_by_municipality / municipal_area_by_id).fillna(0.0)
    total_area = float(municipal_area_by_id.sum())
    intersected_area = float(area_by_municipality.sum())
    over_100 = coverage[coverage > 100.000001]
    return {
        "municipal_area_total_m2": total_area,
        "intersected_area_m2": intersected_area,
        "coverage_pct": float(100 * intersected_area / total_area) if total_area else 0.0,
        "uncovered_area_m2": float(total_area - intersected_area),
        "municipalities_over_100_pct": {str(key): float(value) for key, value in over_100.items()},
        "coverage_min_pct": float(coverage.min()) if len(coverage) else 0.0,
        "coverage_max_pct": float(coverage.max()) if len(coverage) else 0.0,
        "coverage_distribution_pct": {
            str(percentile): float(coverage.quantile(percentile / 100))
            for percentile in (0, 1, 5, 25, 50, 75, 95, 99, 100)
        },
        "sum_pct_municipio_total_by_municipality": {
            str(key): float(value) for key, value in gdf.groupby("municipality_id")["pct_municipio_total"].sum().items()
        },
    }


def calculate_municipal_overlay(inputs: dict[str, Any]) -> tuple[gpd.GeoDataFrame, dict[str, Any]]:
    source_version, source_hash = source_identity(inputs["edafologias"])
    frames: list[gpd.GeoDataFrame] = []
    metrics_by_source: dict[str, Any] = {}
    for key in LIMIT_SOURCE_KEYS:
        frame, metrics = calculate_overlay_for_source(inputs["edafologias"], inputs["boundaries"][key], key)
        frames.append(frame)
        metrics_by_source[key] = metrics
    output = pd.concat(frames, ignore_index=True)
    output = gpd.GeoDataFrame(output, geometry="geometry", crs=f"EPSG:{CANONICAL_SRID}")
    validate_overlay_frame(output)
    manifest = build_overlay_manifest(inputs, output, metrics_by_source, source_version, source_hash)
    return output, manifest


def build_overlay_manifest(
    inputs: dict[str, Any],
    output: gpd.GeoDataFrame,
    metrics_by_source: dict[str, Any],
    source_version: str,
    source_hash: str,
) -> dict[str, Any]:
    transform_manifest_path = inputs["transform_manifest_path"]
    extract_manifest_path = inputs["extract_manifest_path"]
    transform_manifest = inputs["transform_manifest"]
    extract_manifest = inputs["extract_manifest"]
    boundaries = extract_manifest["auxiliary_inputs"]["municipal_boundaries"]
    return {
        "extract_manifest_path": str(extract_manifest_path),
        "extract_manifest_sha256": sha256_file(extract_manifest_path),
        "transform_manifest_path": str(transform_manifest_path),
        "transform_manifest_sha256": sha256_file(transform_manifest_path),
        "edafologia_gpkg": transform_manifest["output_path"],
        "edafologia_gpkg_sha256": sha256_file(Path(str(transform_manifest["output_path"]))),
        "municipal_boundaries_gpkg": boundaries["output_gpkg"],
        "municipal_boundaries_gpkg_sha256": sha256_file(Path(str(boundaries["output_gpkg"]))),
        "source_version": source_version,
        "source_file_sha256": source_hash,
        "pipeline_version": PIPELINE_VERSION,
        "crs": CANONICAL_SRID,
        "municipal_layers": {
            key: {
                "layer": MUNICIPAL_BOUNDARY_SOURCES[key]["layer"],
                "geometry_column": MUNICIPAL_BOUNDARY_SOURCES[key]["geometry_column"],
            }
            for key in LIMIT_SOURCE_KEYS
        },
        "input_counts": {
            "edafologias": int(len(inputs["edafologias"])),
            "municipios_iieg": int(len(inputs["boundaries"]["iieg"])),
            "municipios_inegi": int(len(inputs["boundaries"]["inegi"])),
        },
        "sources": metrics_by_source,
        "final_fragments": int(len(output)),
        "fragments_by_source": {key: int((output["fuente_limite_clave"] == key).sum()) for key in LIMIT_SOURCE_KEYS},
        "processed_at": datetime.now().astimezone().isoformat(),
    }


def write_overlay_artifacts(
    gdf: gpd.GeoDataFrame,
    manifest: dict[str, Any],
    output_path: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_output = output_path.with_suffix(".tmp.gpkg")
    if tmp_output.exists():
        tmp_output.unlink()
    gdf.to_file(tmp_output, layer=MUNICIPAL_OVERLAY_OUTPUT_LAYER, driver="GPKG", engine="pyogrio")
    tmp_output.replace(output_path)
    manifest["output_path"] = str(output_path)
    manifest["output_layer"] = MUNICIPAL_OVERLAY_OUTPUT_LAYER
    manifest["output_sha256"] = sha256_file(output_path)
    tmp_manifest = manifest_path.with_suffix(".tmp.json")
    tmp_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    tmp_manifest.replace(manifest_path)
    return manifest


def read_overlay_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Overlay manifest not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_overlay_manifest(manifest: dict[str, Any]) -> None:
    required = (
        "extract_manifest_path",
        "extract_manifest_sha256",
        "transform_manifest_path",
        "transform_manifest_sha256",
        "edafologia_gpkg",
        "edafologia_gpkg_sha256",
        "municipal_boundaries_gpkg",
        "municipal_boundaries_gpkg_sha256",
        "source_version",
        "source_file_sha256",
        "output_path",
        "output_sha256",
        "output_layer",
        "sources",
    )
    missing = [field for field in required if field not in manifest]
    if missing:
        raise ValueError(f"Overlay manifest is missing required fields: {missing}")
    checks = {
        "extract_manifest_sha256": Path(str(manifest["extract_manifest_path"])),
        "transform_manifest_sha256": Path(str(manifest["transform_manifest_path"])),
        "edafologia_gpkg_sha256": Path(str(manifest["edafologia_gpkg"])),
        "municipal_boundaries_gpkg_sha256": Path(str(manifest["municipal_boundaries_gpkg"])),
        "output_sha256": Path(str(manifest["output_path"])),
    }
    for hash_field, path in checks.items():
        if not path.exists():
            raise FileNotFoundError(f"Overlay manifest references missing file: {path}")
        if sha256_file(path) != manifest[hash_field]:
            raise ValueError(f"Overlay manifest hash mismatch: {hash_field}")
    if manifest["output_layer"] != MUNICIPAL_OVERLAY_OUTPUT_LAYER:
        raise ValueError(f"Unexpected overlay output layer: {manifest['output_layer']}")


def read_overlay_layer(manifest: dict[str, Any]) -> gpd.GeoDataFrame:
    frame = gpd.read_file(manifest["output_path"], layer=manifest["output_layer"], engine="pyogrio")
    validate_overlay_frame(frame)
    return frame
