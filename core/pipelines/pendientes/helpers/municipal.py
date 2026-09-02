from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import geometry_mask, geometry_window
from rasterio.windows import transform as window_transform
from shapely.geometry import mapping
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from core.pipelines.pendientes.constants import (
    CVEGEO_MUNICIPALITY_TABLE,
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
    checks = {
        "count": len(frame) == EXPECTED_MUNICIPALITY_COUNT,
        "unique_cvegeo": frame["cvegeo"].nunique() == EXPECTED_MUNICIPALITY_COUNT,
        "unique_cve_mun": frame["cve_mun"].nunique() == EXPECTED_MUNICIPALITY_COUNT,
        "cve_ent": bool((pd.to_numeric(frame["cve_ent"]) == JALISCO_CVE_ENT).all()),
        "municipality_id_is_cve_mun": bool(
            (pd.to_numeric(frame["cvegeo"]) == JALISCO_CVE_ENT * 1000 + pd.to_numeric(frame["cve_mun"])).all()
        ),
        "crs": frame.crs is not None and frame.crs.to_epsg() == TARGET_SRID,
        "nonnull_geometry": bool(frame.geometry.notna().all()),
        "valid_geometry": bool(frame.geometry.is_valid.all()),
        "polygonal": set(frame.geometry.geom_type.unique()) <= {"Polygon", "MultiPolygon"},
    }
    if not all(checks.values()):
        raise ValueError(f"Municipal boundary contract failed: {checks}")
    return {"checks": checks, "count": len(frame), "bounds": [float(value) for value in frame.total_bounds]}


def write_municipal_boundaries_atomic(layers: dict[str, gpd.GeoDataFrame], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    partial = output_path.with_suffix(".partial.gpkg")
    partial.unlink(missing_ok=True)
    try:
        for source_key, frame in layers.items():
            frame.to_file(partial, layer=MUNICIPAL_BOUNDARY_SOURCES[source_key]["layer"], driver="GPKG")
        partial.replace(output_path)
    except Exception:
        partial.unlink(missing_ok=True)
        raise


def prepare_municipal_boundaries(
    database_url: str,
    output_path: Path,
    previous_manifest: dict[str, Any] | None,
    force: bool,
) -> dict[str, Any]:
    if output_path.exists() and not force and previous_manifest:
        if sha256_file(output_path) != previous_manifest.get("sha256"):
            raise ValueError("Existing municipal boundary artifact checksum changed")
        for source in MUNICIPAL_BOUNDARY_SOURCES.values():
            validate_municipal_boundary_frame(gpd.read_file(output_path, layer=source["layer"]))
        return {**previous_manifest, "reused": True}
    engine = create_engine(database_url)
    layers = {}
    validations = {}
    try:
        for source_key, source in MUNICIPAL_BOUNDARY_SOURCES.items():
            geometry_column = source["geometry_column"]
            query = f"""
                SELECT cvegeo, cve_ent, cve_mun, nomgeo, nom_ent,
                       {geometry_column} AS geometry
                FROM {CVEGEO_MUNICIPALITY_TABLE}
                WHERE cve_ent = {JALISCO_CVE_ENT}
                ORDER BY cve_mun
            """
            frame = gpd.read_postgis(query, engine, geom_col="geometry")
            layers[source_key] = frame
            validations[source_key] = validate_municipal_boundary_frame(frame)
        write_municipal_boundaries_atomic(layers, output_path)
    except SQLAlchemyError as error:
        raise ConnectionError("Could not freeze cvegeo municipal boundaries") from error
    finally:
        engine.dispose()
    return {
        "path": str(output_path),
        "sha256": sha256_file(output_path),
        "database_table": CVEGEO_MUNICIPALITY_TABLE,
        "cve_ent": JALISCO_CVE_ENT,
        "sources": validations,
        "extracted_at": datetime.now().astimezone().isoformat(),
        "reused": False,
    }


def _selected_values(dataset: rasterio.io.DatasetReader, geometry: Any) -> tuple[np.ndarray, int]:
    window = geometry_window(dataset, [mapping(geometry)])
    values = dataset.read(1, window=window)
    inside = geometry_mask(
        [mapping(geometry)],
        out_shape=values.shape,
        transform=window_transform(window, dataset.transform),
        invert=True,
        all_touched=False,
    )
    selected = values[inside & valid_mask(values, dataset.nodata)].astype(np.float64)
    return selected, int(np.count_nonzero(inside))


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
    percent_path: Path,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    rows = []
    source_summaries = {}
    with (
        rasterio.open(elevation_path) as elevation,
        rasterio.open(degrees_path) as degrees,
        rasterio.open(percent_path) as percent,
    ):
        for source_key, source in MUNICIPAL_BOUNDARY_SOURCES.items():
            boundaries = gpd.read_file(boundaries_path, layer=source["layer"])
            validation = validate_municipal_boundary_frame(boundaries)
            source_valid_pixels = 0
            for record in boundaries.itertuples(index=False):
                elevation_values, inside_pixels = _selected_values(elevation, record.geometry)
                degree_values, degree_inside = _selected_values(degrees, record.geometry)
                percent_values, percent_inside = _selected_values(percent, record.geometry)
                if inside_pixels != degree_inside or inside_pixels != percent_inside:
                    raise ValueError("Municipal rasterization windows disagree between continuous products")
                if not (elevation_values.size == degree_values.size == percent_values.size):
                    raise ValueError("Municipal continuous products do not share their valid mask")
                if elevation_values.size == 0:
                    raise ValueError(f"Municipality has no valid raster coverage: {record.cve_mun}")
                source_valid_pixels += elevation_values.size
                rows.append(
                    {
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
                        "valid_area_ha": float(elevation_values.size * 225.0 / 10_000.0),
                        "coverage_percent": float(elevation_values.size / inside_pixels * 100.0),
                    }
                )
            source_summaries[source_key] = {**validation, "sum_municipal_valid_pixels": source_valid_pixels}
    frame = pd.DataFrame(rows).sort_values(["fuente_limite_municipal_id", "municipality_id"]).reset_index(drop=True)
    if len(frame) != EXPECTED_MUNICIPALITY_COUNT * len(MUNICIPAL_BOUNDARY_SOURCES):
        raise ValueError("Municipal statistics do not contain both 125-municipality boundary sources")
    return frame, {"row_count": len(frame), "sources": source_summaries}


def write_parquet_atomic(frame: pd.DataFrame, output_path: Path) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    partial = output_path.with_suffix(".partial.parquet")
    partial.unlink(missing_ok=True)
    try:
        frame.to_parquet(partial, index=False)
        observed = pd.read_parquet(partial)
        if not frame.equals(observed):
            raise ValueError("Municipal Parquet round-trip changed values")
        partial.replace(output_path)
    except Exception:
        partial.unlink(missing_ok=True)
        raise
    return {"path": str(output_path), "sha256": sha256_file(output_path), "rows": len(frame)}
