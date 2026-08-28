from __future__ import annotations

import geopandas as gpd
from sqlalchemy import text
from sqlalchemy.engine import Engine


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
