import logging
from contextlib import contextmanager
from datetime import date

import pandas as pd
import pytest

from core.pipelines.emim.attributes import EmimTables as T
from core.pipelines.emim.constants import CONFLICT_KEYS
from core.pipelines.emim.schemas import StgEmim
from core.pipelines.emim.stages import load as load_module
from core.pipelines.emim.stages.load import EmimLoad

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
    """Record what load hands to the DB helpers instead of hitting PostgreSQL.

    ON CONFLICT semantics are PostgreSQL's job; what has to be pinned here is the
    contract this pipeline passes to it — the conflict keys and the payload.
    """
    calls: dict = {"upserts": [], "inserts": []}

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
def load() -> EmimLoad:
    stage = object.__new__(EmimLoad)
    stage.logger = logging.getLogger("test.emim.load")
    stage.db = _FakeDb()
    return stage


def _row(**overrides) -> dict:
    row = {
        "fecha": date(2026, 5, 1),
        "entidad_id": 14,
        "codigo_actividad": "31-33",
        "per_ocu_tot": 79150,
        "horas_trabajadas": 16337.001,
        "remuneraciones": 1153818,
        "valor_produccion": 25622352,
        "valor_ventas": 24926158,
        "estatus": "Cifras preliminares",
    }
    row.update(overrides)
    return row


def _payload(rows: list[dict]) -> dict:
    return {
        "df": pd.DataFrame(rows),
        "catalogs": {
            T.CAT_ESTATUS: [{"estatus": label} for label in ("Cifras definitivas", "Cifras preliminares")],
            T.CAT_ACTIVIDAD: [{"codigo_actividad": "31-33", "descripcion": "Industrias manufactureras"}],
        },
    }


def _stg_records(captured: dict) -> list[dict]:
    return next(data for model, data, _ in captured["upserts"] if model is StgEmim)


class TestUpsertContract:
    def test_conflict_keys_are_the_natural_key_of_the_source(self, load, captured):
        load.action(_payload([_row()]))

        conflict_keys = next(keys for model, _, keys in captured["upserts"] if model is StgEmim)
        assert conflict_keys == CONFLICT_KEYS

    def test_a_revised_period_overwrites_instead_of_appending(self, load, captured):
        """Same period, entity and activity republished with definitive figures.

        INEGI republishes the whole series every month, so the second run carries
        the same natural key with a new status. Sending both rows would double the
        table; only the last one may survive.
        """
        rows = [_row(), _row(estatus="Cifras definitivas", valor_produccion=26000000)]

        load.action(_payload(rows))

        records = _stg_records(captured)
        assert len(records) == 1
        assert records[0]["estatus_id"] == ESTATUS_IDS["cifras_definitivas"]
        assert records[0]["valor_produccion"] == 26000000

    def test_the_text_activity_code_is_part_of_the_natural_key(self, load, captured):
        """The sector "31-33" and its subsectors coexist in the same period."""
        load.action(_payload([_row(codigo_actividad="31-33"), _row(codigo_actividad="311")]))

        records = _stg_records(captured)
        assert len(records) == 2
        assert {r["codigo_actividad"] for r in records} == {"31-33", "311"}

    def test_different_entities_in_the_same_period_are_both_kept(self, load, captured):
        load.action(_payload([_row(entidad_id=14), _row(entidad_id=6)]))

        assert len(_stg_records(captured)) == 2

    def test_revised_status_is_resolved(self, load, captured):
        load.action(_payload([_row(estatus="Cifras revisadas")]))

        assert _stg_records(captured)[0]["estatus_id"] == ESTATUS_IDS["cifras_revisadas"]

    def test_serial_id_is_never_sent_to_the_insert(self, load, captured):
        load.action(_payload([_row()]))

        assert "id" not in _stg_records(captured)[0]

    def test_every_mapped_column_is_sent(self, load, captured):
        load.action(_payload([_row()]))

        expected = [c for c in StgEmim.columns() if c != "id"]
        assert sorted(_stg_records(captured)[0]) == sorted(expected)

    def test_missing_measures_reach_the_insert_as_none(self, load, captured):
        """pd.NA would blow up psycopg; it has to be a real None."""
        load.action(_payload([_row(remuneraciones=None, valor_ventas=None)]))

        record = _stg_records(captured)[0]
        assert record["remuneraciones"] is None
        assert record["valor_ventas"] is None


class TestCatalogs:
    def test_activity_catalog_is_upserted_so_reworded_descriptions_land(self, load, captured):
        load.action(_payload([_row()]))

        conflict_keys = next(keys for model, _, keys in captured["upserts"] if model is not StgEmim)
        assert conflict_keys == ["codigo_actividad"]

    def test_status_catalog_is_inserted_do_nothing_so_ids_never_shift(self, load, captured):
        load.action(_payload([_row()]))

        assert [keys for _, _, keys in captured["inserts"]] == [["estatus"]]


class TestGuards:
    def test_empty_input_does_not_touch_the_database(self, load, captured):
        result = load.action({"df": pd.DataFrame(), "catalogs": {}})

        assert result == {"records_before": None}
        assert not captured["upserts"] and not captured["inserts"]
