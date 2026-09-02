from contextlib import contextmanager
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pytest
import rasterio
import yaml
from rasterio.transform import from_origin
from shapely.geometry import MultiPolygon, box
from sqlalchemy.engine import make_url

from core.pipelines.pendientes.attributes import PendientesTables
from core.pipelines.pendientes.config import Settings
from core.pipelines.pendientes.constants import FROZEN_RELEASE_COG_SHA256, MUNICIPAL_BOUNDARY_SOURCES
from core.pipelines.pendientes.helpers.municipal import (
    calculate_municipal_statistics,
    prepare_municipal_boundaries,
    validate_municipal_boundary_frame,
    write_municipal_boundaries_atomic,
    write_parquet_atomic,
)
from core.pipelines.pendientes.schemas import EstadisticasPendienteMunicipales
from core.pipelines.pendientes.stages.load import PendientesLoad
from core.utils.files import sha256_file


def _municipal_frame() -> gpd.GeoDataFrame:
    records = []
    for municipality_id in range(1, 126):
        row, column = divmod(municipality_id - 1, 25)
        records.append(
            {
                "cvegeo": 14_000 + municipality_id,
                "cve_ent": 14,
                "cve_mun": municipality_id,
                "nomgeo": f"Municipio {municipality_id}",
                "nom_ent": "Jalisco",
                "geometry": MultiPolygon(
                    [box(column * 15, (4 - row) * 15, (column + 1) * 15, (5 - row) * 15)]
                ),
            }
        )
    return gpd.GeoDataFrame(records, geometry="geometry", crs="EPSG:6368")


def _continuous(path: Path, multiplier: float, unit: str) -> None:
    values = np.arange(1, 126, dtype=np.float32).reshape(5, 25) * multiplier
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=25,
        height=5,
        count=1,
        dtype="float32",
        nodata=-9999.0,
        crs="EPSG:6368",
        transform=from_origin(0, 75, 15, 15),
    ) as dataset:
        dataset.write(values, 1)
        dataset.set_band_unit(1, unit)


def test_two_boundary_sources_produce_250_identity_safe_rows(tmp_path: Path) -> None:
    boundaries = tmp_path / "municipal_boundaries.gpkg"
    elevation = tmp_path / "elevation.tif"
    degrees = tmp_path / "degrees.tif"
    frame = _municipal_frame()
    assert validate_municipal_boundary_frame(frame)["municipality_count"] == 125
    write_municipal_boundaries_atomic({"iieg": frame, "inegi": frame}, boundaries)
    _continuous(elevation, 10.0, "metre")
    _continuous(degrees, 0.1, "degree")

    statistics, qa = calculate_municipal_statistics(boundaries, elevation, degrees)

    assert len(statistics) == 250
    assert statistics.groupby("fuente_limite_clave").size().to_dict() == {"iieg": 125, "inegi": 125}
    assert (statistics["municipality_id"] == statistics["cve_mun"]).all()
    assert (statistics["cvegeo"].astype(int) == 14_000 + statistics["cve_mun"]).all()
    assert set(qa["sources"]) == set(MUNICIPAL_BOUNDARY_SOURCES)
    parquet = write_parquet_atomic(
        statistics,
        tmp_path / "statistics.parquet",
        metadata={"slope_method": "WoodEvans5x5"},
    )
    assert parquet["rows"] == 250
    metadata = pq.read_metadata(parquet["path"]).metadata
    assert metadata[b"pendientes:slope_method"] == b"WoodEvans5x5"
    expected_percent = np.tan(np.radians(statistics["slope_degrees_mean"])) * 100
    np.testing.assert_allclose(statistics["slope_percent_mean"], expected_percent)


def test_database_identity_and_unique_contract() -> None:
    assert PendientesTables.ESTADISTICAS_PENDIENTE_MUNICIPALES == "estadisticas_pendiente_municipales"
    assert {"municipality_id", "cve_mun", "cve_ent", "fuente_limite_municipal_id"} <= set(
        EstadisticasPendienteMunicipales.columns()
    )
    constraints = {constraint.name for constraint in EstadisticasPendienteMunicipales.__table__.constraints}
    assert "uq_estadisticas_pendiente_municipio_fuente" in constraints


def test_cvegeo_connection_reuses_common_config_and_changes_only_database_name() -> None:
    config = Settings(DB_HOST="db.local", DB_PORT="5433", DB_USER="tester", DB_PASSWORD="not-logged")
    source = make_url(config.database_url)
    cvegeo = make_url(config.cvegeo_database_url)
    assert (cvegeo.host, cvegeo.port, cvegeo.username) == (source.host, source.port, source.username)
    assert cvegeo.database == "cvegeo"


def test_existing_snapshot_is_reused_and_checksum_change_is_rejected(tmp_path: Path) -> None:
    boundaries = tmp_path / "municipal_boundaries.gpkg"
    frame = _municipal_frame()
    write_municipal_boundaries_atomic({"iieg": frame, "inegi": frame}, boundaries)
    previous = {
        "sha256": sha256_file(boundaries),
        "sources": {
            key: {"geometry_column": source["geometry_column"]}
            for key, source in MUNICIPAL_BOUNDARY_SOURCES.items()
        },
    }

    reused = prepare_municipal_boundaries("invalid://not-used", boundaries, previous, force=False)
    assert reused["reused"] is True
    boundaries.write_bytes(boundaries.read_bytes() + b"corrupt")
    with pytest.raises(ValueError, match="checksum changed"):
        prepare_municipal_boundaries("invalid://not-used", boundaries, previous, force=False)


def test_context_coverage_gate_rejects_partial_municipality(tmp_path: Path) -> None:
    boundaries = tmp_path / "municipal_boundaries.gpkg"
    elevation = tmp_path / "elevation.tif"
    degrees = tmp_path / "degrees.tif"
    frame = _municipal_frame()
    frame.loc[0, "geometry"] = MultiPolygon([box(-15, 60, 15, 75)])
    write_municipal_boundaries_atomic({"iieg": frame, "inegi": _municipal_frame()}, boundaries)
    _continuous(elevation, 10.0, "metre")
    _continuous(degrees, 0.1, "degree")

    with pytest.raises(ValueError, match="partially_outside"):
        calculate_municipal_statistics(boundaries, elevation, degrees)


def test_only_five_selective_continuous_indicators_are_declared() -> None:
    catalog = Path("core/indicadores/catalogo/medio_ambiente")
    expected = {
        "elevacion_media_municipal_m",
        "pendiente_media_municipal_grados",
        "pendiente_mediana_municipal_grados",
        "pendiente_p95_municipal_grados",
        "pendiente_media_municipal_porcentaje",
    }
    observed = {}
    for path in catalog.glob("*.yaml"):
        definition = yaml.safe_load(path.read_text())
        if definition.get("pipeline") == "pendientes":
            observed[definition["id"]] = definition
    assert set(observed) == expected
    assert all(any(parameter["nombre"] == "fuente_limite" for parameter in item["parametros"]) for item in observed.values())
    assert all("clas" not in item["origen"] for item in observed.values())


def test_dag_and_load_expose_only_productive_etl_and_no_cog_conversion() -> None:
    assert {path.name for path in Path("core/pipelines/pendientes/stages").glob("*.py")} == {
        "__init__.py",
        "extract.py",
        "transform.py",
        "load.py",
    }
    dag_source = Path("dags/etl_pendientes.py").read_text()
    assert "stages=[PendientesExtract(), PendientesTransform(), PendientesLoad()]" in dag_source
    assert 'task_id="extract"' in dag_source
    assert 'task_id="transform"' in dag_source
    assert 'task_id="load"' in dag_source
    assert "extract_task >> transform_task >> load_task" in dag_source
    assert "schedule=None" in dag_source
    assert "max_active_runs=1" in dag_source
    load_names = set(PendientesLoad.action.__code__.co_names) | set(PendientesLoad.source.__code__.co_names)
    assert "create_cog" not in load_names
    assert "gdal_translate" not in Path("core/pipelines/pendientes/stages/load.py").read_text()
    transform_source = Path("core/pipelines/pendientes/stages/transform.py").read_text()
    assert "PendientesCartographicSlopeProduction" not in transform_source
    assert all(len(checksum) == 64 for checksum in FROZEN_RELEASE_COG_SHA256.values())


def test_migrations_create_only_tabular_products_and_enable_postgis() -> None:
    migration_dir = Path("migrations/pendientes/sql")
    sql = "\n".join(path.read_text() for path in sorted(migration_dir.glob("*.sql")))
    assert "CREATE EXTENSION IF NOT EXISTS postgis" in sql
    assert "CREATE FOREIGN TABLE IF NOT EXISTS cvegeo_municipalities" in sql
    assert "municipality_vector_area_ha" in sql
    assert "rasterized_area_difference_ha" in sql
    assert "postgis_raster" not in sql.lower()
    assert "raster_columns" not in sql.lower()


def test_load_statistics_uses_one_transaction_and_idempotent_upserts(monkeypatch, tmp_path: Path) -> None:
    class FakeDatabase:
        sessions = 0
        connected = False

        def connect(self):
            self.connected = True

        @contextmanager
        def get_session(self):
            self.sessions += 1
            yield object()

        def disconnect(self):
            self.connected = False

    row = {
        "municipality_id": 1,
        "cve_mun": 1,
        "cve_ent": 14,
        "cvegeo": "14001",
        "municipio": "Acatic",
        "fuente_limite_municipal_id": 1,
        "fuente_limite_clave": "iieg",
        "elevation_min_m": 1.0,
        "elevation_max_m": 2.0,
        "elevation_mean_m": 1.5,
        "elevation_median_m": 1.5,
        "elevation_std_m": 0.5,
        "elevation_p05_m": 1.05,
        "elevation_p95_m": 1.95,
        "slope_degrees_min": 0.0,
        "slope_degrees_max": 2.0,
        "slope_degrees_mean": 1.0,
        "slope_degrees_median": 1.0,
        "slope_degrees_std": 0.5,
        "slope_degrees_p05": 0.1,
        "slope_degrees_p95": 1.9,
        "slope_percent_mean": 1.8,
        "slope_percent_median": 1.7,
        "slope_percent_p95": 3.3,
        "slope_percent_max": 3.5,
        "valid_pixel_count": 10,
        "valid_area_ha": 0.225,
        "municipality_vector_area_ha": 0.225,
        "rasterized_area_difference_ha": 0.0,
        "coverage_percent": 100.0,
    }
    calls = []

    def capture_upsert(session, records, model, conflict_keys, update_keys):
        calls.append((model.__tablename__, records, [key for key in conflict_keys]))

    stage = PendientesLoad()
    stage.work_dir = tmp_path
    stage.db = FakeDatabase()
    monkeypatch.setattr("core.pipelines.pendientes.stages.load.upsert_records", capture_upsert)
    report = stage._load_statistics(pd.DataFrame([row]))

    assert stage.db.sessions == 1
    assert report == {"catalog_rows": 2, "municipal_statistics_rows": 1, "transactional": True}
    assert [call[0] for call in calls] == ["fuentes_limites_municipales", "estadisticas_pendiente_municipales"]
    assert calls[1][2] == ["municipality_id", "fuente_limite_municipal_id"]
