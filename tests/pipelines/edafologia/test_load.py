from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import geopandas as gpd
import pandas as pd
import pytest
from geoalchemy2.elements import WKBElement
from shapely.geometry import MultiPolygon, Polygon
from sqlalchemy import create_engine, text

from core.pipelines.edafologia.constants import CANONICAL_SRID, TRANSFORM_OUTPUT_LAYER
from core.utils.files import sha256_file
from core.pipelines.edafologia.helpers.load import (
    canonical_records,
    dataframe_to_nullable_records,
    resolve_catalog_ids,
    shapely_to_wkb_element,
    source_identity,
    validate_version_collision,
)
from core.pipelines.edafologia.helpers.load_catalogs import (
    boundary_source_records,
    catalog_records,
    validate_catalog_counts,
)
from core.pipelines.edafologia.helpers.load_inputs import validate_transform_manifest, validate_transformed_frame
from core.pipelines.edafologia.helpers.municipal_overlay_load import overlay_records, validate_municipality_ids
from core.pipelines.edafologia.mappings import CALIFICADORES_EDAFOLOGICOS, GRUPOS_EDAFOLOGICOS
from core.pipelines.edafologia.schemas import Edafologias


def _square() -> MultiPolygon:
    return MultiPolygon([Polygon([(0, 0), (1, 0), (1, 1), (0, 0)])])


def _frame() -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        pd.DataFrame(
            [
                {
                    "source_version": "Serie III",
                    "source_objectid": 1,
                    "clave_wrb": "ACab-N",
                    "grupo1_origen": "AC",
                    "califp_g1_origen": "ab",
                    "califs_g1_origen": "N",
                    "grupo2_origen": None,
                    "califp_g2_origen": None,
                    "califs_g2_origen": None,
                    "grupo3_origen": None,
                    "califp_g3_origen": None,
                    "clase_textural_origen": "media",
                    "limite_superior_origen": None,
                    "fase_fisica_origen": None,
                    "fase_quimica_origen": None,
                    "shape_leng_origen": pd.NA,
                    "shape_area_origen": float("nan"),
                    "source_name": "INEGI",
                    "source_url": "https://example.test/source.zip",
                    "source_file_name": "source.zip",
                    "source_file_sha256": "abc123",
                    "source_downloaded_at": pd.Timestamp("2026-07-15T00:00:00Z"),
                    "processed_at": pd.Timestamp("2026-07-15T01:00:00Z"),
                    "fecha_actualizacion": pd.Timestamp("2026-07-15"),
                    "pipeline_version": "0.2.0",
                }
            ]
        ),
        geometry=[_square()],
        crs=f"EPSG:{CANONICAL_SRID}",
    )


def _manifest(tmp_path: Path, output_path: Path, extract_path: Path) -> dict[str, object]:
    return {
        "extract_manifest_path": str(extract_path),
        "extract_manifest_sha256": sha256_file(extract_path),
        "output_path": str(output_path),
        "output_sha256": sha256_file(output_path),
        "output_layer": TRANSFORM_OUTPUT_LAYER,
        "final_feature_count": 3765,
        "final_crs": CANONICAL_SRID,
        "final_geometry_types": ["MultiPolygon"],
        "spatial_validation": {
            "null_geometries": 0,
            "empty_geometries": 0,
            "invalid_geometries": 0,
            "non_positive_area": 0,
            "source_objectid_unique": True,
        },
    }


def test_validate_transform_manifest_rejects_extract_hash_mismatch(tmp_path):
    extract = tmp_path / "extract.json"
    output = tmp_path / "out.gpkg"
    extract.write_text("{}", encoding="utf-8")
    output.write_bytes(b"gpkg")
    manifest = _manifest(tmp_path, output, extract)
    extract.write_text('{"changed": true}', encoding="utf-8")

    with pytest.raises(ValueError, match="extract_manifest_sha256"):
        validate_transform_manifest(manifest, tmp_path / "transform_manifest.json")


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("final_feature_count", 1, "feature count"),
        ("final_crs", 4326, "CRS"),
    ],
)
def test_validate_transform_manifest_rejects_count_or_srid(tmp_path, field, value, message):
    extract = tmp_path / "extract.json"
    output = tmp_path / "out.gpkg"
    extract.write_text("{}", encoding="utf-8")
    output.write_bytes(b"gpkg")
    manifest = _manifest(tmp_path, output, extract)
    manifest[field] = value

    with pytest.raises(ValueError, match=message):
        validate_transform_manifest(manifest, tmp_path / "transform_manifest.json")


def test_shapely_to_wkb_element_sets_srid():
    value = shapely_to_wkb_element(_square())

    assert isinstance(value, WKBElement)
    assert value.srid == CANONICAL_SRID


def test_shapely_to_wkb_element_rejects_null_geometry():
    with pytest.raises(ValueError, match="null or empty"):
        shapely_to_wkb_element(None)


def test_resolve_catalog_ids_is_independent_from_insert_order():
    frame = _frame()
    grupo_ids = {"AC": 25}
    qualifier_ids = {"N": 400, "ab": 300}

    result = resolve_catalog_ids(frame, grupo_ids, qualifier_ids)

    assert result["grupo_edafologico_id"].iloc[0] == 25
    assert result["calificador_primario_id"].iloc[0] == 300
    assert result["calificador_secundario_id"].iloc[0] == 400


def test_resolve_catalog_ids_rejects_missing_catalog_code():
    frame = _frame()

    with pytest.raises(ValueError, match="Missing catalog ids"):
        resolve_catalog_ids(frame, {"AC": 1}, {"ab": 2})


def test_dataframe_to_nullable_records_converts_pd_missing_values():
    frame = pd.DataFrame({"a": [pd.NA], "b": [float("nan")], "c": [pd.NaT]})

    records = dataframe_to_nullable_records(frame, ["a", "b", "c"])

    assert records == [{"a": None, "b": None, "c": None}]


def test_canonical_records_excludes_serial_id_and_uses_wkb():
    frame = resolve_catalog_ids(_frame(), {"AC": 9}, {"ab": 8, "N": 7})

    records = canonical_records(frame)

    assert Edafologias.id.key not in records[0]
    assert isinstance(records[0]["geom"], WKBElement)


class _Query:
    def __init__(self, rows):
        self.rows = rows

    def filter(self, *_args, **_kwargs):
        return self

    def distinct(self):
        return self

    def all(self):
        return self.rows


class _Session:
    def __init__(self, rows):
        self.rows = rows

        self.rolled_back = False

    def query(self, *_args, **_kwargs):
        return _Query(self.rows)


def test_validate_version_collision_allows_identical_rerun():
    validate_version_collision(_Session([("abc123",)]), "Serie III", "abc123")


def test_validate_version_collision_rejects_same_version_different_hash():
    with pytest.raises(ValueError, match="source_version collision"):
        validate_version_collision(_Session([("different",)]), "Serie III", "abc123")


def test_source_identity_requires_single_version_and_hash():
    frame = _frame()

    assert source_identity(frame) == ("Serie III", "abc123")

    frame.loc[1, "source_version"] = "Otra version"
    with pytest.raises(ValueError, match="exactly one source_version"):
        source_identity(frame)


def test_catalogs_have_expected_counts_and_non_empty_values():
    group_records = catalog_records(GRUPOS_EDAFOLOGICOS)
    qualifier_records = catalog_records(CALIFICADORES_EDAFOLOGICOS)
    limit_records = boundary_source_records()

    validate_catalog_counts(group_records, qualifier_records, limit_records)
    assert len(group_records) == 24
    assert len(qualifier_records) == 87
    assert len(limit_records) == 2


def test_validate_transformed_frame_rejects_geometry_null():
    frame = _frame()
    frame.loc[0, frame.geometry.name] = None

    with pytest.raises(ValueError, match="null geometries"):
        validate_transformed_frame(frame, {"final_feature_count": 1})


def test_load_uses_upsert_conflict_keys_for_idempotence(monkeypatch):
    monkeypatch.setenv("SOURCE_URL", "https://example.test/source.zip")
    monkeypatch.setenv("CVEGEO_DB_USER", "user")
    monkeypatch.setenv("CVEGEO_DB_PASSWORD", "secret")
    monkeypatch.setenv("CVEGEO_DB_HOST", "localhost")
    sys.modules.pop("core.pipelines.edafologia.config", None)
    sys.modules.pop("core.pipelines.edafologia.stages.load", None)
    load_stage = importlib.import_module("core.pipelines.edafologia.stages.load")

    calls = []
    stage = load_stage.EdafologiaLoad()
    frame = _frame()

    def fake_upsert(_session, data, model, conflict_keys, update_keys=None, chunk_size=10_000):
        calls.append((model.__tablename__, conflict_keys, update_keys, len(data), chunk_size))

    monkeypatch.setattr(load_stage, "upsert_records", fake_upsert)
    monkeypatch.setattr(load_stage, "sync_id_sequence", lambda *_args, **_kwargs: None)
    stage._load_catalogs(SimpleNamespace())

    assert ("grupos_edafologicos", ["clave"], ["descripcion"], 24, 10_000) in calls
    assert ("calificadores_edafologicos", ["clave"], ["descripcion"], 87, 10_000) in calls

    records = canonical_records(resolve_catalog_ids(frame, {"AC": 1}, {"ab": 2, "N": 3}))
    fake_upsert(
        None,
        records,
        Edafologias,
        conflict_keys=[Edafologias.source_version.key, Edafologias.source_objectid.key],
        update_keys=[
            key for key in records[0] if key not in {Edafologias.source_version.key, Edafologias.source_objectid.key}
        ],
    )
    assert calls[-1][1] == ["source_version", "source_objectid"]


def test_load_rolls_back_transaction_on_error(monkeypatch):
    monkeypatch.setenv("SOURCE_URL", "https://example.test/source.zip")
    monkeypatch.setenv("CVEGEO_DB_USER", "user")
    monkeypatch.setenv("CVEGEO_DB_PASSWORD", "secret")
    monkeypatch.setenv("CVEGEO_DB_HOST", "localhost")
    sys.modules.pop("core.pipelines.edafologia.config", None)
    sys.modules.pop("core.pipelines.edafologia.stages.load", None)
    load_stage = importlib.import_module("core.pipelines.edafologia.stages.load")

    class FakeSessionContext:
        rolled_back = False

        def __enter__(self):
            return _Session([])

        def __exit__(self, exc_type, _exc, _traceback):
            self.rolled_back = exc_type is not None
            return False

    class FakeDb:
        def __init__(self, context):
            self.context = context
            self.disconnected = False

        def connect(self):
            return None

        def get_session(self):
            return self.context

        def disconnect(self):
            self.disconnected = True

    context = FakeSessionContext()
    fake_db = FakeDb(context)
    stage = load_stage.EdafologiaLoad()
    stage.db = fake_db
    monkeypatch.setattr(stage, "_load_catalogs", lambda _session: (_ for _ in ()).throw(RuntimeError("boom")))

    with pytest.raises(RuntimeError, match="boom"):
        stage.action({"manifest": {}, "frame": _frame()})

    assert context.rolled_back is True
    assert fake_db.disconnected is True


def test_load_checks_version_collision_before_catalog_writes(monkeypatch):
    monkeypatch.setenv("SOURCE_URL", "https://example.test/source.zip")
    monkeypatch.setenv("CVEGEO_DB_USER", "user")
    monkeypatch.setenv("CVEGEO_DB_PASSWORD", "secret")
    monkeypatch.setenv("CVEGEO_DB_HOST", "localhost")
    sys.modules.pop("core.pipelines.edafologia.config", None)
    sys.modules.pop("core.pipelines.edafologia.stages.load", None)
    load_stage = importlib.import_module("core.pipelines.edafologia.stages.load")

    class FakeSessionContext:
        def __enter__(self):
            return _Session([("different",)])

        def __exit__(self, *_args):
            return False

    class FakeDb:
        def connect(self):
            return None

        def get_session(self):
            return FakeSessionContext()

        def disconnect(self):
            return None

    stage = load_stage.EdafologiaLoad()
    stage.db = FakeDb()
    catalog_writes_called = False

    def fail_if_called(_session):
        nonlocal catalog_writes_called
        catalog_writes_called = True
        raise AssertionError("catalog writes should not run when source_version collides")

    monkeypatch.setattr(stage, "_load_catalogs", fail_if_called)

    with pytest.raises(ValueError, match="source_version collision"):
        stage.action({"manifest": {}, "frame": _frame()})

    assert catalog_writes_called is False


def test_load_does_not_transform_geometry_before_wkb():
    frame = resolve_catalog_ids(_frame(), {"AC": 1}, {"ab": 2, "N": 3})
    original_wkb = frame.geometry.iloc[0].wkb
    records = canonical_records(frame)

    assert bytes(records[0]["geom"].data) == original_wkb


def test_overlay_load_persists_cve_mun_as_municipality_id():
    frame = gpd.GeoDataFrame(
        [
            {
                "source_version": "Serie III",
                "source_objectid": 1,
                "fuente_limite_clave": "iieg",
                "municipality_id": 39,
                "area_m2": 0.5,
                "area_ha": 0.00005,
                "pct_poligono_fuente": 50.0,
                "pct_municipio_total": 25.0,
                "pct_cobertura_edafologica": 25.0,
            }
        ],
        geometry=[_square()],
        crs=f"EPSG:{CANONICAL_SRID}",
    )

    records = overlay_records(frame, {("Serie III", 1): 10}, {"iieg": 20})

    assert records[0]["municipality_id"] == 39
    assert "municipality_cvegeo" not in records[0]


def test_overlay_load_validates_municipality_id_against_fdw_catalog():
    class Result:
        def all(self):
            return [(municipality_id, 14_000 + municipality_id) for municipality_id in range(1, 126)]

    class Session:
        def execute(self, *_args, **_kwargs):
            return Result()

    validate_municipality_ids(Session(), [{"municipality_id": 39}])

    with pytest.raises(ValueError, match="outside Jalisco"):
        validate_municipality_ids(Session(), [{"municipality_id": 999}])


def _load_env_file(env_path: Path, monkeypatch) -> None:
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        monkeypatch.setenv(key.strip(), value.strip().strip('"').strip("'"))


@pytest.mark.integration
def test_edafologia_load_real_integration(monkeypatch):
    env_path = Path("migrations/edafologia/.env")
    transform_manifest_path = Path("data/transform/edafologia/transform_manifest.json")
    if not env_path.exists() or not transform_manifest_path.exists():
        pytest.skip("Local edafologia env and transform manifest are required")

    _load_env_file(env_path, monkeypatch)
    monkeypatch.setenv("SOURCE_URL", os.getenv("SOURCE_URL", "https://example.test/source.zip"))
    monkeypatch.setenv("CVEGEO_DB_USER", os.getenv("CVEGEO_DB_USER", "user"))
    monkeypatch.setenv("CVEGEO_DB_PASSWORD", os.getenv("CVEGEO_DB_PASSWORD", "secret"))
    monkeypatch.setenv("CVEGEO_DB_HOST", os.getenv("CVEGEO_DB_HOST", "localhost"))
    monkeypatch.setenv("CVEGEO_DB_PORT", os.getenv("CVEGEO_DB_PORT", "5433"))
    monkeypatch.setenv("CVEGEO_DB_NAME", os.getenv("CVEGEO_DB_NAME", "cvegeo"))
    sys.modules.pop("core.pipelines.edafologia.config", None)
    sys.modules.pop("core.pipelines.edafologia.stages.load", None)
    load_stage = importlib.import_module("core.pipelines.edafologia.stages.load")

    result = load_stage.EdafologiaLoad().execute()

    assert result["catalog_counts"] == {
        "grupos_edafologicos": 24,
        "calificadores_edafologicos": 87,
        "fuentes_limites_municipales": 2,
    }
    assert result["canonical_records"] == 3765

    settings = importlib.import_module("core.pipelines.edafologia.config").settings
    engine = create_engine(settings.database_url)
    with engine.connect() as connection:
        counts = dict(
            connection.execute(
                text(
                    """
                    SELECT 'grupos_edafologicos', count(*) FROM grupos_edafologicos
                    UNION ALL SELECT 'calificadores_edafologicos', count(*) FROM calificadores_edafologicos
                    UNION ALL SELECT 'fuentes_limites_municipales', count(*) FROM fuentes_limites_municipales
                    UNION ALL SELECT 'edafologias', count(*) FROM edafologias
                    """
                )
            ).all()
        )
    engine.dispose()

    assert counts == {
        "grupos_edafologicos": 24,
        "calificadores_edafologicos": 87,
        "fuentes_limites_municipales": 2,
        "edafologias": 3765,
    }
