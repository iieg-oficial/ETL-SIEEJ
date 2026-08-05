import logging
from contextlib import contextmanager
from datetime import date

import pandas as pd
import pytest

from core.pipelines.emec.attributes import EmecTables as T
from core.pipelines.emec.constants import CONFLICT_KEYS
from core.pipelines.emec.schemas import StgEmec
from core.pipelines.emec.stages import load as load_module
from core.pipelines.emec.stages.load import EmecLoad

CVEGEO_STATES = {"jalisco": 14, "colima": 6, "veracruz_de_ignacio_de_la_llave": 30}
ESTATUS_IDS = {"cifras_definitivas": 1, "cifras_revisadas": 2, "cifras_preliminares": 3}


class _FakeSession:
    pass


class _FakeDb:
    def __init__(self):
        self.connected = False

    def connect(self):
        self.connected = True

    def disconnect(self):
        self.connected = False

    @contextmanager
    def get_session(self):
        yield _FakeSession()


@pytest.fixture
def captured(monkeypatch) -> dict:
    """Record what load hands to the DB helpers instead of hitting PostgreSQL.

    ON CONFLICT semantics are PostgreSQL's job; what has to be pinned here is the
    contract this pipeline passes to it — the conflict keys and the payload.
    """
    calls: dict = {"upserts": [], "inserts": []}

    monkeypatch.setattr(load_module, "get_cvegeo_mapping", lambda session, **kwargs: CVEGEO_STATES)
    monkeypatch.setattr(load_module, "get_mapping", lambda *args, **kwargs: ESTATUS_IDS)
    monkeypatch.setattr(load_module, "sync_id_sequence", lambda session, model: None)
    monkeypatch.setattr(load_module, "count_records", lambda session, model: 0)
    monkeypatch.setattr(
        load_module,
        "insert_records",
        lambda session, data, model, conflict_keys: calls["inserts"].append((model, data, conflict_keys)),
    )
    monkeypatch.setattr(
        load_module,
        "upsert_records",
        lambda session, data, model, conflict_keys, **kwargs: calls["upserts"].append((model, data, conflict_keys)),
    )
    return calls


@pytest.fixture
def load() -> EmecLoad:
    stage = object.__new__(EmecLoad)
    stage.logger = logging.getLogger("test.emec.load")
    stage.db = _FakeDb()
    return stage


def _row(**overrides) -> dict:
    row = {
        "fecha": date(2026, 5, 1),
        "entidad": "Jalisco",
        "codigo_actividad": 43,
        "per_ocu_tot": 79.4,
        "remuneraciones_tot": 70.4,
        "remuneraciones_media": 88.7,
        "ind_ingresos_bienes_serv": 50.8,
        "ind_compras_reventa": 54.3,
        "estatus": "Cifras preliminares",
    }
    row.update(overrides)
    return row


def _payload(rows: list[dict]) -> dict:
    return {
        "df": pd.DataFrame(rows),
        "catalogs": {
            T.CAT_ESTATUS: [{"estatus": label} for label in ("Cifras definitivas", "Cifras preliminares")],
            T.CAT_ACTIVIDAD: [{"codigo_actividad": 43, "descripcion": "Comercio al por mayor"}],
        },
    }


def _stg_records(captured: dict) -> list[dict]:
    return next(data for model, data, _ in captured["upserts"] if model is StgEmec)


class TestEntityResolution:
    def test_entity_name_becomes_the_cvegeo_key(self, load, captured):
        load.action(_payload([_row()]))

        assert _stg_records(captured)[0]["entidad_id"] == 14

    def test_official_long_names_resolve(self, load, captured):
        load.action(_payload([_row(entidad="Veracruz de Ignacio de la Llave")]))

        assert _stg_records(captured)[0]["entidad_id"] == 30

    def test_unknown_entity_is_dropped_instead_of_loaded_with_a_null_key(self, load, captured):
        """entidad_id is NOT NULL; an unmatched name must not reach the insert."""
        load.action(_payload([_row(), _row(entidad="Nueva Galicia")]))

        records = _stg_records(captured)
        assert len(records) == 1
        assert records[0]["entidad_id"] == 14

    def test_everything_unmatched_skips_the_insert_entirely(self, load, captured):
        load.action(_payload([_row(entidad="Nueva Galicia")]))

        assert not [data for model, data, _ in captured["upserts"] if model is StgEmec]


class TestUpsertContract:
    def test_conflict_keys_are_the_natural_key_of_the_source(self, load, captured):
        load.action(_payload([_row()]))

        conflict_keys = next(keys for model, _, keys in captured["upserts"] if model is StgEmec)
        assert conflict_keys == CONFLICT_KEYS

    def test_a_revised_period_overwrites_instead_of_appending(self, load, captured):
        """Same period, entity and activity published again as definitive figures.

        INEGI republishes the whole series every month, so the second run carries
        the same natural key with a new status. Sending both rows would double the
        table; only the last one may survive.
        """
        rows = [_row(), _row(estatus="Cifras definitivas", per_ocu_tot=81.2)]

        load.action(_payload(rows))

        records = _stg_records(captured)
        assert len(records) == 1
        assert records[0]["estatus_id"] == ESTATUS_IDS["cifras_definitivas"]
        assert records[0]["per_ocu_tot"] == 81.2

    def test_different_activities_in_the_same_period_are_both_kept(self, load, captured):
        load.action(_payload([_row(codigo_actividad=43), _row(codigo_actividad=46)]))

        assert len(_stg_records(captured)) == 2

    def test_different_entities_in_the_same_period_are_both_kept(self, load, captured):
        load.action(_payload([_row(entidad="Jalisco"), _row(entidad="Colima")]))

        assert len(_stg_records(captured)) == 2

    def test_serial_id_is_never_sent_to_the_insert(self, load, captured):
        load.action(_payload([_row()]))

        assert "id" not in _stg_records(captured)[0]

    def test_every_mapped_column_is_sent(self, load, captured):
        load.action(_payload([_row()]))

        expected = [c for c in StgEmec.columns() if c != "id"]
        assert sorted(_stg_records(captured)[0]) == sorted(expected)


class TestStatusResolution:
    def test_status_text_becomes_its_catalog_id(self, load, captured):
        load.action(_payload([_row(estatus="Cifras revisadas")]))

        assert _stg_records(captured)[0]["estatus_id"] == ESTATUS_IDS["cifras_revisadas"]

    def test_missing_status_is_loaded_as_null_not_as_a_failure(self, load, captured):
        load.action(_payload([_row(estatus=None)]))

        assert _stg_records(captured)[0]["estatus_id"] is None


class TestCatalogs:
    def test_activity_catalog_is_upserted_so_reworded_descriptions_land(self, load, captured):
        load.action(_payload([_row()]))

        conflict_keys = next(keys for model, _, keys in captured["upserts"] if model is not StgEmec)
        assert conflict_keys == ["codigo_actividad"]

    def test_status_catalog_is_inserted_do_nothing_so_ids_never_shift(self, load, captured):
        load.action(_payload([_row()]))

        assert [keys for _, _, keys in captured["inserts"]] == [["estatus"]]


class TestGuards:
    def test_empty_input_does_not_touch_the_database(self, load, captured):
        result = load.action({"df": pd.DataFrame(), "catalogs": {}})

        assert result == {"records_before": None}
        assert not captured["upserts"] and not captured["inserts"]
