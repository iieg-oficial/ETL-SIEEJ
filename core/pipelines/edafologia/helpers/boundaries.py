from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import geopandas as gpd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from core.pipelines.edafologia.constants import CANONICAL_SRID, CVEGEO_ENTITY_FILTER, CVEGEO_TABLE
from core.pipelines.edafologia.helpers.download import sha256_file


def _validate_identifier(value: str) -> str:
    if not value.replace("_", "").isalnum():
        raise ValueError(f"Unsafe SQL identifier: {value}")
    return value


def _split_table_name(table_name: str) -> tuple[str, str]:
    schema, table = table_name.split(".", 1)
    return _validate_identifier(schema), _validate_identifier(table)


def has_gist_index(engine: Engine, table_name: str, geometry_column: str, expected_index: str) -> bool:
    schema, table = _split_table_name(table_name)
    query = text(
        """
        SELECT EXISTS (
            SELECT 1
            FROM pg_indexes
            WHERE schemaname = :schema
              AND tablename = :table
              AND indexname = :expected_index
              AND indexdef ILIKE '%USING gist%'
              AND indexdef ILIKE :geometry_pattern
        )
        """
    )
    with engine.connect() as connection:
        return bool(
            connection.execute(
                query,
                {
                    "schema": schema,
                    "table": table,
                    "expected_index": expected_index,
                    "geometry_pattern": f"%{geometry_column}%",
                },
            ).scalar()
        )


def read_boundary_layer(
    engine: Engine,
    table_name: str,
    geometry_column: str,
    entity_id: int,
) -> gpd.GeoDataFrame:
    schema, table = _split_table_name(table_name)
    geometry_column = _validate_identifier(geometry_column)
    sql = text(
        f"""
        SELECT
            cvegeo,
            cve_ent,
            cve_mun,
            nomgeo,
            nom_ent,
            {geometry_column} AS geom
        FROM {schema}.{table}
        WHERE cve_ent::text = :entity_id
        ORDER BY cvegeo
        """
    )
    return gpd.read_postgis(sql, engine, geom_col="geom", params={"entity_id": str(entity_id)})


def validate_boundary_layer(
    gdf: gpd.GeoDataFrame,
    source_geometry_column: str,
    gist_index_present: bool,
    expected_count: int = 125,
    expected_srid: int = CANONICAL_SRID,
) -> dict[str, Any]:
    missing_fields = [field for field in ("cvegeo", "cve_ent", "cve_mun", "nomgeo", "nom_ent") if field not in gdf]
    if missing_fields:
        raise ValueError(f"Boundary layer is missing required fields: {missing_fields}")

    count = int(len(gdf))
    unique_cvegeo = int(gdf["cvegeo"].nunique(dropna=True))
    null_geometries = int(gdf.geometry.isna().sum())
    invalid_geometries = int((~gdf.geometry.is_valid & gdf.geometry.notna()).sum())
    geometry_types = sorted(gdf.geometry.geom_type.dropna().unique().tolist())
    srid = gdf.crs.to_epsg() if gdf.crs is not None else None

    validations = {
        "expected_count": count == expected_count,
        "unique_cvegeo": unique_cvegeo == expected_count,
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
            validation = validate_boundary_layer(gdf, geometry_column, index_present)
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
