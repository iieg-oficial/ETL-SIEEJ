from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import rasterio
from rasterio.features import geometry_mask, geometry_window
from rasterio.windows import Window
from rasterio.windows import transform as window_transform
from shapely.geometry import box, mapping
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from core.pipelines.edafologia.queries.boundaries import has_gist_index
from core.pipelines.pendientes.constants import (
    CVEGEO_MUNICIPALITY_TABLE,
    CVEGEO_STATE_BOUNDARY_TABLE,
    EXPECTED_MUNICIPALITY_COUNT,
    JALISCO_CVE_ENT,
    MUNICIPAL_BOUNDARY_SOURCES,
    TARGET_SRID,
)
from core.pipelines.pendientes.helpers.experimental_metrics import valid_mask
from core.utils.files import sha256_file


def validate_municipal_boundary_frame(frame: gpd.GeoDataFrame) -> dict[str, Any]:
    required = {"cvegeo", "cve_ent", "cve_mun", "nomgeo", "nom_ent"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Municipal boundaries lack fields: {missing}")

    cvegeo = pd.to_numeric(frame["cvegeo"], errors="coerce")
    cve_ent = pd.to_numeric(frame["cve_ent"], errors="coerce")
    cve_mun = pd.to_numeric(frame["cve_mun"], errors="coerce")
    keys = pd.DataFrame({"cvegeo": cvegeo, "cve_ent": cve_ent, "cve_mun": cve_mun})
    null_keys = int(keys.isna().any(axis=1).sum())
    duplicate_keys = int(frame.duplicated(["cve_ent", "cve_mun"], keep=False).sum())
    duplicate_cvegeo = int(cvegeo.duplicated(keep=False).sum())
    invalid_geometries = int((frame.geometry.notna() & ~frame.geometry.is_valid).sum())
    empty_geometries = int((frame.geometry.notna() & frame.geometry.is_empty).sum())
    null_geometries = int(frame.geometry.isna().sum())
    geometry_types = sorted(frame.geometry.geom_type.dropna().unique().tolist())
    areas = frame.geometry.area
    nonpositive_areas = int((areas <= 0).sum())
    srid = frame.crs.to_epsg() if frame.crs is not None else None

    checks = {
        "municipality_count": len(frame) == EXPECTED_MUNICIPALITY_COUNT,
        "unique_cvegeo": cvegeo.nunique(dropna=True) == EXPECTED_MUNICIPALITY_COUNT,
        "unique_cve_mun": cve_mun.nunique(dropna=True) == EXPECTED_MUNICIPALITY_COUNT,
        "nonnull_keys": null_keys == 0,
        "cve_ent": bool((cve_ent == JALISCO_CVE_ENT).all()),
        "municipality_id_is_cve_mun": bool((cvegeo == JALISCO_CVE_ENT * 1000 + cve_mun).all()),
        "crs": srid == TARGET_SRID,
        "nonnull_geometry": null_geometries == 0,
        "nonempty_geometry": empty_geometries == 0,
        "valid_geometry": invalid_geometries == 0,
        "multipolygon": geometry_types == ["MultiPolygon"],
        "positive_area": nonpositive_areas == 0,
        "no_duplicate_keys": duplicate_keys == 0 and duplicate_cvegeo == 0,
    }
    if not all(checks.values()):
        raise ValueError(f"Municipal boundary contract failed: {checks}")
    return {
        "checks": checks,
        "municipality_count": int(len(frame)),
        "total_area_km2": float(areas.sum() / 1_000_000.0),
        "min_municipality_area_km2": float(areas.min() / 1_000_000.0),
        "max_municipality_area_km2": float(areas.max() / 1_000_000.0),
        "invalid_geometries": invalid_geometries,
        "empty_geometries": empty_geometries,
        "null_geometries": null_geometries,
        "duplicate_keys": duplicate_keys + duplicate_cvegeo,
        "srid": srid,
        "geometry_type": "MultiPolygon",
        "bounds": [float(value) for value in frame.total_bounds],
    }


def write_municipal_boundaries_atomic(
    layers: dict[str, gpd.GeoDataFrame],
    output_path: Path,
    state_layers: dict[str, gpd.GeoDataFrame] | None = None,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    partial = output_path.with_suffix(".partial.gpkg")
    partial.unlink(missing_ok=True)
    try:
        for source_key, frame in layers.items():
            layer = str(MUNICIPAL_BOUNDARY_SOURCES[source_key]["layer"])
            frame.to_file(partial, layer=layer, driver="GPKG")
        for source_key, frame in (state_layers or {}).items():
            layer = str(MUNICIPAL_BOUNDARY_SOURCES[source_key]["state_layer"])
            frame.to_file(partial, layer=layer, driver="GPKG")
        partial.replace(output_path)
    except Exception:
        partial.unlink(missing_ok=True)
        raise


def _read_municipal_layer(engine: Any, geometry_column: str) -> gpd.GeoDataFrame:
    query = text(
        f"""
        SELECT cvegeo, cve_ent, cve_mun, nomgeo, nom_ent,
               {geometry_column} AS geometry
        FROM {CVEGEO_MUNICIPALITY_TABLE}
        WHERE cve_ent = :cve_ent
        ORDER BY cvegeo
        """
    )
    return gpd.read_postgis(query, engine, geom_col="geometry", params={"cve_ent": JALISCO_CVE_ENT})


def _read_state_boundary(engine: Any, geometry_column: str) -> gpd.GeoDataFrame:
    query = text(
        f"""
        SELECT {geometry_column} AS geometry
        FROM {CVEGEO_STATE_BOUNDARY_TABLE}
        WHERE {geometry_column} IS NOT NULL
        ORDER BY id
        """
    )
    return gpd.read_postgis(query, engine, geom_col="geometry")


def _validate_reusable_snapshot(output_path: Path, previous_manifest: dict[str, Any]) -> dict[str, Any]:
    if sha256_file(output_path) != previous_manifest.get("sha256"):
        raise ValueError("Existing municipal boundary artifact checksum changed")
    validations = {}
    for source_key, source in MUNICIPAL_BOUNDARY_SOURCES.items():
        validation = validate_municipal_boundary_frame(gpd.read_file(output_path, layer=str(source["layer"])))
        state = gpd.read_file(output_path, layer=str(source["state_layer"]))
        if len(state) != 1 or state.crs is None or state.crs.to_epsg() != TARGET_SRID:
            raise ValueError(f"Existing state boundary snapshot is invalid: {source_key}")
        expected = previous_manifest.get("sources", {}).get(source_key, {})
        if expected.get("geometry_column") not in {None, source["geometry_column"]}:
            raise ValueError(f"Existing municipal snapshot source identity changed: {source_key}")
        validations[source_key] = {**expected, **validation}
    return {**previous_manifest, "sources": validations, "reused": True}


def prepare_municipal_boundaries(
    database_url: str,
    output_path: Path,
    previous_manifest: dict[str, Any] | None,
    force: bool,
) -> dict[str, Any]:
    if output_path.exists() and not force and previous_manifest:
        return _validate_reusable_snapshot(output_path, previous_manifest)

    engine = create_engine(database_url)
    layers: dict[str, gpd.GeoDataFrame] = {}
    state_layers: dict[str, gpd.GeoDataFrame] = {}
    validations: dict[str, dict[str, Any]] = {}
    try:
        for source_key, source in MUNICIPAL_BOUNDARY_SOURCES.items():
            geometry_column = str(source["geometry_column"])
            index_present = has_gist_index(
                engine,
                CVEGEO_MUNICIPALITY_TABLE,
                geometry_column,
                str(source["expected_gist_index"]),
            )
            frame = _read_municipal_layer(engine, geometry_column)
            validation = validate_municipal_boundary_frame(frame)
            state = _read_state_boundary(engine, str(source["state_geometry_column"]))
            if len(state) != 1 or state.crs is None or state.crs.to_epsg() != TARGET_SRID:
                raise ValueError(f"cvegeo state boundary contract failed: {source_key}")
            state_area_km2 = float(state.geometry.area.sum() / 1_000_000.0) if not state.empty else None
            municipal_area_km2 = float(validation["total_area_km2"])
            layers[source_key] = frame
            state_layers[source_key] = state
            validations[source_key] = {
                **validation,
                "boundary_source": source_key,
                "geometry_column": geometry_column,
                "layer": source["layer"],
                "state_layer": source["state_layer"],
                "source_version": source["version"],
                "expected_gist_index": source["expected_gist_index"],
                "gist_index_present": index_present,
                "state_boundary_area_km2": state_area_km2,
                "municipal_minus_state_area_km2": (
                    municipal_area_km2 - state_area_km2 if state_area_km2 is not None else None
                ),
                "state_comparison_is_descriptive": True,
            }
            if not index_present:
                raise ValueError(f"Expected cvegeo GiST index is missing: {source['expected_gist_index']}")
        write_municipal_boundaries_atomic(layers, output_path, state_layers)
    except SQLAlchemyError as error:
        raise ConnectionError("Could not freeze cvegeo municipal boundaries") from error
    finally:
        engine.dispose()
    return {
        "status": "municipal_snapshot_validated",
        "path": str(output_path),
        "sha256": sha256_file(output_path),
        "database": "cvegeo",
        "database_table": CVEGEO_MUNICIPALITY_TABLE,
        "state_boundary_table": CVEGEO_STATE_BOUNDARY_TABLE,
        "entity_filter": f"cve_ent = {JALISCO_CVE_ENT}",
        "municipality_identity": "municipality_id = cve_mun within cve_ent = 14",
        "remote_cvegeo_id_is_not_municipality_id": True,
        "sources": validations,
        "source_count": len(validations),
        "municipality_source_combinations": sum(item["municipality_count"] for item in validations.values()),
        "extracted_at": datetime.now().astimezone().isoformat(),
        "reused": False,
    }


def _assert_shared_context_grid(
    elevation: rasterio.io.DatasetReader,
    degrees: rasterio.io.DatasetReader,
) -> None:
    properties = ("crs", "transform", "width", "height", "bounds")
    mismatches = [name for name in properties if getattr(elevation, name) != getattr(degrees, name)]
    if mismatches:
        raise ValueError(f"Context DEM and WE5 degrees grids differ: {mismatches}")
    if elevation.crs is None or elevation.crs.to_epsg() != TARGET_SRID:
        raise ValueError("Context rasters must use EPSG:6368")


def _common_selected_values(
    elevation: rasterio.io.DatasetReader,
    degrees: rasterio.io.DatasetReader,
    geometry: Any,
) -> tuple[np.ndarray, np.ndarray, int, int]:
    raw_window = geometry_window(elevation, [mapping(geometry)]).round_offsets().round_lengths()
    window = Window(
        int(raw_window.col_off),
        int(raw_window.row_off),
        int(raw_window.width),
        int(raw_window.height),
    )
    transform = window_transform(window, elevation.transform)
    inside = geometry_mask(
        [mapping(geometry)],
        out_shape=(int(window.height), int(window.width)),
        transform=transform,
        invert=True,
        all_touched=False,
    )
    elevation_data = elevation.read(1, window=window)
    degree_data = degrees.read(1, window=window)
    selected = inside & valid_mask(elevation_data, elevation.nodata) & valid_mask(degree_data, degrees.nodata)
    return (
        elevation_data[selected].astype(np.float64),
        degree_data[selected].astype(np.float64),
        int(np.count_nonzero(inside)),
        int(np.count_nonzero(selected)),
    )


def _continuous_statistics(
    values: np.ndarray,
    prefix: str,
    fields: tuple[str, ...],
    suffix: str = "",
) -> dict[str, float]:
    available = {
        "min": float(values.min()),
        "max": float(values.max()),
        "mean": float(values.mean()),
        "median": float(np.median(values)),
        "std": float(values.std()),
        "p05": float(np.percentile(values, 5)),
        "p95": float(np.percentile(values, 95)),
    }
    return {f"{prefix}_{field}{suffix}": available[field] for field in fields}


def calculate_municipal_statistics(
    boundaries_path: Path,
    elevation_path: Path,
    degrees_path: Path,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    source_summaries: dict[str, Any] = {}
    with rasterio.open(elevation_path) as elevation, rasterio.open(degrees_path) as degrees:
        _assert_shared_context_grid(elevation, degrees)
        context_extent = box(*elevation.bounds)
        context_bounds = [float(value) for value in elevation.bounds]
        for source_key, source in MUNICIPAL_BOUNDARY_SOURCES.items():
            boundaries = gpd.read_file(boundaries_path, layer=str(source["layer"]))
            validation = validate_municipal_boundary_frame(boundaries)
            outside = [
                int(row.cve_mun) for row in boundaries.itertuples() if not context_extent.intersects(row.geometry)
            ]
            partial = [int(row.cve_mun) for row in boundaries.itertuples() if not context_extent.covers(row.geometry)]
            if outside or partial:
                raise ValueError(
                    "Municipal boundaries exceed contextual raster coverage: "
                    f"source={source_key}, outside={outside}, partially_outside={partial}"
                )

            source_valid_pixels = 0
            incomplete_valid_coverage: list[int] = []
            source_rows: list[dict[str, Any]] = []
            for record in boundaries.itertuples(index=False):
                elevation_values, degree_values, inside_pixels, selected_pixels = _common_selected_values(
                    elevation,
                    degrees,
                    record.geometry,
                )
                if selected_pixels != inside_pixels:
                    incomplete_valid_coverage.append(int(record.cve_mun))
                    continue
                if elevation_values.size == 0:
                    raise ValueError(f"Municipality has no valid raster coverage: {record.cve_mun}")
                if not np.all(np.isfinite(elevation_values)) or not np.all(np.isfinite(degree_values)):
                    raise ValueError(f"Municipality has non-finite continuous input: {record.cve_mun}")
                if np.any(degree_values < 0):
                    raise ValueError(f"Municipality has negative WE5 slope values: {record.cve_mun}")

                percent_values = np.tan(np.radians(degree_values)) * 100.0
                vector_area_ha = float(record.geometry.area / 10_000.0)
                valid_area_ha = float(elevation_values.size * 225.0 / 10_000.0)
                source_valid_pixels += elevation_values.size
                row = {
                    "municipality_id": int(record.cve_mun),
                    "cve_mun": int(record.cve_mun),
                    "cve_ent": int(record.cve_ent),
                    "cvegeo": str(record.cvegeo).zfill(5),
                    "municipio": str(record.nomgeo),
                    "fuente_limite_municipal_id": int(source["id"]),
                    "fuente_limite_clave": source_key,
                    **_continuous_statistics(
                        elevation_values,
                        "elevation",
                        ("min", "max", "mean", "median", "std", "p05", "p95"),
                        "_m",
                    ),
                    **_continuous_statistics(
                        degree_values,
                        "slope_degrees",
                        ("min", "max", "mean", "median", "std", "p05", "p95"),
                    ),
                    **_continuous_statistics(
                        percent_values,
                        "slope_percent",
                        ("mean", "median", "p95", "max"),
                    ),
                    "valid_pixel_count": int(elevation_values.size),
                    "valid_area_ha": valid_area_ha,
                    "municipality_vector_area_ha": vector_area_ha,
                    "rasterized_area_difference_ha": valid_area_ha - vector_area_ha,
                    "coverage_percent": valid_area_ha / vector_area_ha * 100.0,
                }
                source_rows.append(row)
                rows.append(row)
            if incomplete_valid_coverage:
                raise ValueError(
                    "Municipalities are partially outside the valid contextual raster footprint: "
                    f"source={source_key}, municipalities={incomplete_valid_coverage}"
                )
            source_summaries[source_key] = {
                **validation,
                "sum_municipal_valid_pixels": int(source_valid_pixels),
                "municipalities_outside_context": 0,
                "municipalities_partially_outside_context": 0,
                "minimum_coverage_percent": min(row["coverage_percent"] for row in source_rows),
                "maximum_coverage_percent": max(row["coverage_percent"] for row in source_rows),
                "coverage_below_95_percent": sum(row["coverage_percent"] < 95.0 for row in source_rows),
            }

    frame = pd.DataFrame(rows).sort_values(["fuente_limite_municipal_id", "municipality_id"]).reset_index(drop=True)
    expected_rows = sum(item["municipality_count"] for item in source_summaries.values())
    duplicated = int(frame.duplicated(["municipality_id", "fuente_limite_municipal_id"]).sum())
    numeric = frame.select_dtypes(include=[np.number])
    slope_values = frame.filter(regex=r"^slope_(degrees|percent)_")
    validations = {
        "row_count_matches_snapshot": len(frame) == expected_rows,
        "unique_source_municipality_key": duplicated == 0,
        "nonnull_municipality": bool(frame["municipality_id"].notna().all()),
        "statistics_finite": bool(np.isfinite(numeric.to_numpy(dtype=np.float64)).all()),
        "slope_nonnegative": bool((slope_values >= 0).to_numpy().all()),
        "context_coverage_hard_gate": all(
            item["municipalities_outside_context"] == 0 and item["municipalities_partially_outside_context"] == 0
            for item in source_summaries.values()
        ),
    }
    if not all(validations.values()):
        raise ValueError(f"Municipal statistics contract failed: {validations}")
    return frame, {
        "row_count": len(frame),
        "expected_row_count_from_snapshot": expected_rows,
        "duplicate_source_municipality_keys": duplicated,
        "pixel_inclusion_rule": "pixel_center",
        "all_touched": False,
        "percentile_method": "numpy exact over all selected municipality pixels",
        "slope_percent_derivation": "tan(radians(WoodEvans5x5_degrees))*100 per pixel",
        "context_grid": {"epsg": TARGET_SRID, "resolution_m": 15.0, "bounds": context_bounds},
        "sources": source_summaries,
        "validations": validations,
    }


def write_parquet_atomic(
    frame: pd.DataFrame,
    output_path: Path,
    metadata: dict[str, str] | None = None,
) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    partial = output_path.with_suffix(".partial.parquet")
    partial.unlink(missing_ok=True)
    provenance = {f"pendientes:{key}".encode(): value.encode() for key, value in (metadata or {}).items()}
    try:
        table = pa.Table.from_pandas(frame, preserve_index=False)
        table = table.replace_schema_metadata({**(table.schema.metadata or {}), **provenance})
        pq.write_table(table, partial)
        observed = pd.read_parquet(partial)
        if not frame.equals(observed):
            raise ValueError("Municipal Parquet round-trip changed values")
        observed_metadata = pq.read_metadata(partial).metadata or {}
        if any(observed_metadata.get(key) != value for key, value in provenance.items()):
            raise ValueError("Municipal Parquet provenance metadata changed")
        partial.replace(output_path)
    except Exception:
        partial.unlink(missing_ok=True)
        raise
    return {
        "path": str(output_path),
        "sha256": sha256_file(output_path),
        "rows": len(frame),
        "metadata": metadata or {},
    }
