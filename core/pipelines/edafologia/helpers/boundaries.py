from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from core.pipelines.edafologia.constants import CANONICAL_SRID, CVEGEO_ENTITY_FILTER, CVEGEO_TABLE, JALISCO_CVE_ENT
from core.pipelines.edafologia.queries.boundaries import has_gist_index, read_boundary_layer
from core.utils.files import sha256_file


def validate_municipal_keys(
    gdf: gpd.GeoDataFrame,
    expected_count: int = 125,
    entity_id: int = JALISCO_CVE_ENT,
) -> dict[str, Any]:
    missing_fields = [field for field in ("cvegeo", "cve_ent", "cve_mun") if field not in gdf]
    if missing_fields:
        raise ValueError(f"Boundary layer is missing required municipal keys: {missing_fields}")

    cvegeo = pd.to_numeric(gdf["cvegeo"], errors="coerce")
    cve_ent = pd.to_numeric(gdf["cve_ent"], errors="coerce")
    cve_mun = pd.to_numeric(gdf["cve_mun"], errors="coerce")
    count = int(len(gdf))
    unique_cvegeo = int(cvegeo.nunique(dropna=True))
    unique_cve_mun = int(cve_mun.nunique(dropna=True))
    null_cvegeo = int(cvegeo.isna().sum())
    null_cve_ent = int(cve_ent.isna().sum())
    null_cve_mun = int(cve_mun.isna().sum())
    invalid_entity = int((cve_ent.dropna() != entity_id).sum())
    incoherent_cvegeo = int((cvegeo.dropna() != entity_id * 1000 + cve_mun.loc[cvegeo.notna()]).sum())
    key_frame = pd.DataFrame({"cvegeo": cvegeo, "cve_ent": cve_ent, "cve_mun": cve_mun}).dropna()
    ambiguous_cve_mun = int((key_frame.groupby(["cve_ent", "cve_mun"])["cvegeo"].nunique() != 1).sum())

    validations = {
        "expected_count": count == expected_count,
        "unique_cvegeo": unique_cvegeo == expected_count,
        "unique_cve_mun": unique_cve_mun == expected_count,
        "nonnull_cvegeo": null_cvegeo == 0,
        "nonnull_cve_ent": null_cve_ent == 0,
        "nonnull_cve_mun": null_cve_mun == 0,
        "jalisco_entity": invalid_entity == 0,
        "coherent_cvegeo": incoherent_cvegeo == 0,
        "unambiguous_cve_mun": ambiguous_cve_mun == 0,
    }
    return {
        "count": count,
        "unique_cvegeo": unique_cvegeo,
        "unique_cve_mun": unique_cve_mun,
        "null_cvegeo": null_cvegeo,
        "null_cve_ent": null_cve_ent,
        "null_cve_mun": null_cve_mun,
        "invalid_entity": invalid_entity,
        "incoherent_cvegeo": incoherent_cvegeo,
        "ambiguous_cve_mun": ambiguous_cve_mun,
        "validations": validations,
    }


def validate_boundary_layer(
    gdf: gpd.GeoDataFrame,
    source_geometry_column: str,
    gist_index_present: bool,
    expected_count: int = 125,
    expected_srid: int = CANONICAL_SRID,
    entity_id: int = JALISCO_CVE_ENT,
) -> dict[str, Any]:
    missing_fields = [field for field in ("cvegeo", "cve_ent", "cve_mun", "nomgeo", "nom_ent") if field not in gdf]
    if missing_fields:
        raise ValueError(f"Boundary layer is missing required fields: {missing_fields}")

    municipal_keys = validate_municipal_keys(gdf, expected_count=expected_count, entity_id=entity_id)
    count = municipal_keys["count"]
    unique_cvegeo = municipal_keys["unique_cvegeo"]
    null_geometries = int(gdf.geometry.isna().sum())
    invalid_geometries = int((~gdf.geometry.is_valid & gdf.geometry.notna()).sum())
    geometry_types = sorted(gdf.geometry.geom_type.dropna().unique().tolist())
    srid = gdf.crs.to_epsg() if gdf.crs is not None else None

    validations = {
        **municipal_keys["validations"],
        "srid": srid == expected_srid,
        "multipolygon": geometry_types == ["MultiPolygon"],
        "null_geometries": null_geometries == 0,
        "invalid_geometries": invalid_geometries == 0,
        "gist_index_present": bool(gist_index_present),
    }

    failed = [name for name, passed in validations.items() if not passed]
    if failed:
        raise ValueError(
            "Boundary layer validation failed for "
            f"{source_geometry_column}: {failed}; "
            f"count={count}, unique_cvegeo={unique_cvegeo}, srid={srid}, "
            f"geometry_types={geometry_types}, null_geometries={null_geometries}, "
            f"invalid_geometries={invalid_geometries}, gist_index_present={gist_index_present}"
        )

    return {
        "source_geometry_column": source_geometry_column,
        "count": count,
        "unique_cvegeo": unique_cvegeo,
        "unique_cve_mun": municipal_keys["unique_cve_mun"],
        "municipal_keys": {key: value for key, value in municipal_keys.items() if key != "validations"},
        "srid": srid,
        "geometry_type": "MultiPolygon",
        "bbox": [float(value) for value in gdf.total_bounds],
        "null_geometries": null_geometries,
        "invalid_geometries": invalid_geometries,
        "validations": validations,
    }


def write_boundary_layers_atomic(layers: dict[str, gpd.GeoDataFrame], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(".tmp.gpkg")
    temporary.unlink(missing_ok=True)

    try:
        for layer_name, gdf in layers.items():
            gdf.to_file(temporary, layer=layer_name, driver="GPKG")
        temporary.replace(output_path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    return output_path


def prepare_municipal_boundaries(
    database_url: str,
    database_name: str,
    output_path: Path,
    boundary_sources: dict[str, dict[str, str]],
    previous_manifest: dict[str, Any] | None,
    force: bool,
    table_name: str = CVEGEO_TABLE,
    entity_id: int = 14,
) -> dict[str, Any]:
    previous_hash = (previous_manifest or {}).get("gpkg_sha256")
    if output_path.exists() and not force and previous_hash and sha256_file(output_path) == previous_hash:
        return previous_manifest or {}

    engine = create_engine(database_url)
    layers: dict[str, gpd.GeoDataFrame] = {}
    layer_manifest: dict[str, Any] = {}

    try:
        for source_key, source in boundary_sources.items():
            geometry_column = source["geometry_column"]
            layer_name = source["layer"]
            index_present = has_gist_index(engine, table_name, geometry_column, source["expected_gist_index"])
            gdf = read_boundary_layer(engine, table_name, geometry_column, entity_id)
            validation = validate_boundary_layer(gdf, geometry_column, index_present, entity_id=entity_id)
            layers[layer_name] = gdf
            layer_manifest[layer_name] = {
                "boundary_source": source_key,
                **validation,
                "expected_gist_index": source["expected_gist_index"],
            }

        write_boundary_layers_atomic(layers, output_path)
    except SQLAlchemyError:
        raise ConnectionError("Could not read cvegeo municipal boundaries with configured credentials") from None
    finally:
        engine.dispose()

    return {
        "database": database_name,
        "table": table_name,
        "entity_filter": CVEGEO_ENTITY_FILTER,
        "output_gpkg": str(output_path),
        "gpkg_sha256": sha256_file(output_path),
        "layers": layer_manifest,
        "extracted_at": datetime.now().astimezone().isoformat(),
    }
