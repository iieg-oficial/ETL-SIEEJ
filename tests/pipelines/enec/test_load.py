import logging
from contextlib import contextmanager
from datetime import date

import pandas as pd
import pytest

from core.pipelines.enec.attributes import EnecTables as T
from core.pipelines.enec.constants import ENTIDAD_CONFLICT_KEYS, MEASURE_RENAME, NACIONAL_CONFLICT_KEYS
from core.pipelines.enec.schemas import StgEnecEntidad, StgEnecNacional
from core.pipelines.enec.stages import load as load_module
from core.pipelines.enec.stages.load import EnecLoad

ESTATUS_IDS = {"cifras_definitivas": 1, "cifras_revisadas": 2, "cifras_preliminares": 3}


class _FakeSession:
    pass


class _FakeDb:
    def connect(self):
        pass

    def disconnect(self):
        pass

    @contextmanager
    def get_session(self):
        yield _FakeSession()


@pytest.fixture
def captured(monkeypatch) -> dict:
    """Record what load hands to the DB helpers instead of hitting PostgreSQL."""
    calls: dict = {"upserts": [], "inserts": []}

    monkeypatch.setattr(load_module, "get_mapping", lambda *a, **k: ESTATUS_IDS)
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
        lambda session, data, model, conflict_keys, **k: calls["upserts"].append((model, data, conflict_keys)),
    )
    return calls


@pytest.fixture
def load() -> EnecLoad:
    stage = object.__new__(EnecLoad)
    stage.logger = logging.getLogger("test.enec.load")
    stage.db = _FakeDb()
    return stage


def _measures() -> dict:
    return {name: 1000 for name in MEASURE_RENAME.values()}


def _nacional_row(**overrides) -> dict:
    row = {"fecha": date(2026, 1, 1), "codigo_actividad": 23, "estatus": "Cifras preliminares", **_measures()}
    row.update(overrides)
    return row


def _entidad_row(**overrides) -> dict:
    row = {"fecha": date(2026, 1, 1), "entidad_id": 14, "estatus": "Cifras preliminares", **_measures()}
    row.update(overrides)
    return row


def _payload(nacional: list[dict], entidad: list[dict]) -> dict:
    return {
        "nacional": pd.DataFrame(nacional),
        "entidad": pd.DataFrame(entidad),
        "catalogs": {
            T.CAT_ESTATUS: [{"estatus": e} for e in ("Cifras definitivas", "Cifras preliminares")],
            T.CAT_ACTIVIDAD: [{"codigo_actividad": 23, "descripcion": "Construcción"}],
        },
    }


def _records(captured: dict, model) -> list[dict]:
    return next(data for m, data, _ in captured["upserts"] if m is model)


class TestBothTablesAreLoaded:
    def test_each_dataset_goes_to_its_own_table(self, load, captured):
        load.action(_payload([_nacional_row()], [_entidad_row()]))

        models = [m for m, _, _ in captured["upserts"]]
        assert StgEnecNacional in models and StgEnecEntidad in models

    def test_each_table_uses_its_own_conflict_keys(self, load, captured):
        load.action(_payload([_nacional_row()], [_entidad_row()]))

        keys = {m: k for m, _, k in captured["upserts"]}
        assert keys[StgEnecNacional] == NACIONAL_CONFLICT_KEYS
        assert keys[StgEnecEntidad] == ENTIDAD_CONFLICT_KEYS

    def test_an_empty_dataset_does_not_block_the_other(self, load, captured):
        load.action(_payload([], [_entidad_row()]))

        models = [m for m, _, _ in captured["upserts"]]
        assert StgEnecEntidad in models and StgEnecNacional not in models


class TestUpsertContract:
    def test_a_revised_period_overwrites_instead_of_appending(self, load, captured):
        rows = [_entidad_row(), _entidad_row(estatus="Cifras definitivas", valor_produccion=2000)]

        load.action(_payload([_nacional_row()], rows))

        records = _records(captured, StgEnecEntidad)
        assert len(records) == 1
        assert records[0]["estatus_id"] == ESTATUS_IDS["cifras_definitivas"]
        assert records[0]["valor_produccion"] == 2000

    def test_activities_coexist_in_the_national_table(self, load, captured):
        load.action(_payload([_nacional_row(codigo_actividad=23), _nacional_row(codigo_actividad=236)], []))

        assert len(_records(captured, StgEnecNacional)) == 2

    def test_entities_coexist_in_the_state_table(self, load, captured):
        load.action(_payload([], [_entidad_row(entidad_id=14), _entidad_row(entidad_id=33)]))

        assert len(_records(captured, StgEnecEntidad)) == 2

    def test_serial_id_is_never_sent(self, load, captured):
        load.action(_payload([_nacional_row()], [_entidad_row()]))

        assert "id" not in _records(captured, StgEnecNacional)[0]
        assert "id" not in _records(captured, StgEnecEntidad)[0]

    def test_every_mapped_column_is_sent(self, load, captured):
        load.action(_payload([_nacional_row()], [_entidad_row()]))

        for model in (StgEnecNacional, StgEnecEntidad):
            expected = [c for c in model.columns() if c != "id"]
            assert sorted(_records(captured, model)[0]) == sorted(expected)

    def test_missing_measures_reach_the_insert_as_none(self, load, captured):
        load.action(_payload([], [_entidad_row(ingresos_tot=None)]))

        assert _records(captured, StgEnecEntidad)[0]["ingresos_tot"] is None


class TestCatalogs:
    def test_status_catalog_is_inserted_do_nothing_so_ids_never_shift(self, load, captured):
        load.action(_payload([_nacional_row()], [_entidad_row()]))

        assert [k for _, _, k in captured["inserts"]] == [["estatus"]]

    def test_activity_catalog_is_upserted(self, load, captured):
        load.action(_payload([_nacional_row()], [_entidad_row()]))

        keys = [k for m, _, k in captured["upserts"] if m not in (StgEnecNacional, StgEnecEntidad)]
        assert keys == [["codigo_actividad"]]


class TestGuards:
    def test_empty_input_does_not_touch_the_database(self, load, captured):
        result = load.action({"nacional": pd.DataFrame(), "entidad": pd.DataFrame(), "catalogs": {}})

        assert result == {"records_before": None}
        assert not captured["upserts"] and not captured["inserts"]
