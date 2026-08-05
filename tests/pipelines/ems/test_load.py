import logging
from contextlib import contextmanager
from datetime import date

import pandas as pd
import pytest

from core.pipelines.ems.attributes import EmsTables as T
from core.pipelines.ems.constants import CONFLICT_KEYS
from core.pipelines.ems.schemas import StgEms
from core.pipelines.ems.stages import load as load_module
from core.pipelines.ems.stages.load import EmsLoad

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
def load() -> EmsLoad:
    stage = object.__new__(EmsLoad)
    stage.logger = logging.getLogger("test.ems.load")
    stage.db = _FakeDb()
    return stage


def _row(**overrides) -> dict:
    row = {
        "fecha": date(2026, 5, 1),
        "entidad_id": 14,
        "codigo_actividad": 51,
        "ind_ingresos_bienes_serv": 29.8,
        "ind_gastos_consumo": 27.3,
        "per_ocu_tot": 77.2,
        "per_ocu_dependiente": None,
        "per_ocu_no_dependiente": None,
        "remuneraciones_tot": 85.4,
        "estatus": "Cifras preliminares",
    }
    row.update(overrides)
    return row


def _payload(rows: list[dict]) -> dict:
    return {
        "df": pd.DataFrame(rows),
        "catalogs": {
            T.CAT_ESTATUS: [{"estatus": label} for label in ("Cifras definitivas", "Cifras preliminares")],
            T.CAT_ACTIVIDAD: [{"codigo_actividad": 51, "descripcion": "Información en medios masivos"}],
        },
    }


def _stg_records(captured: dict) -> list[dict]:
    return next(data for model, data, _ in captured["upserts"] if model is StgEms)


class TestUpsertContract:
    def test_conflict_keys_are_the_natural_key_of_the_source(self, load, captured):
        load.action(_payload([_row()]))

        conflict_keys = next(keys for model, _, keys in captured["upserts"] if model is StgEms)
        assert conflict_keys == CONFLICT_KEYS

    def test_a_revised_period_overwrites_instead_of_appending(self, load, captured):
        """Same period, entity and activity republished with definitive figures.

        INEGI republishes the whole series every month, so the second run carries
        the same natural key with a new status. Sending both rows would double the
        table; only the last one may survive.
        """
        rows = [_row(), _row(estatus="Cifras definitivas", ind_ingresos_bienes_serv=31.5)]

        load.action(_payload(rows))

        records = _stg_records(captured)
        assert len(records) == 1
        assert records[0]["estatus_id"] == ESTATUS_IDS["cifras_definitivas"]
        assert records[0]["ind_ingresos_bienes_serv"] == 31.5

    def test_revised_status_is_resolved(self, load, captured):
        """EMS does publish "Cifras revisadas" today, unlike EMEC."""
        load.action(_payload([_row(estatus="Cifras revisadas")]))

        assert _stg_records(captured)[0]["estatus_id"] == ESTATUS_IDS["cifras_revisadas"]

    def test_different_activities_in_the_same_period_are_both_kept(self, load, captured):
        load.action(_payload([_row(codigo_actividad=51), _row(codigo_actividad=61)]))

        assert len(_stg_records(captured)) == 2

    def test_different_entities_in_the_same_period_are_both_kept(self, load, captured):
        load.action(_payload([_row(entidad_id=14), _row(entidad_id=6)]))

        assert len(_stg_records(captured)) == 2

    def test_serial_id_is_never_sent_to_the_insert(self, load, captured):
        load.action(_payload([_row()]))

        assert "id" not in _stg_records(captured)[0]

    def test_every_mapped_column_is_sent(self, load, captured):
        load.action(_payload([_row()]))

        expected = [c for c in StgEms.columns() if c != "id"]
        assert sorted(_stg_records(captured)[0]) == sorted(expected)

    def test_null_personal_breakdown_reaches_the_insert_as_none(self, load, captured):
        """pd.NA would blow up psycopg; it has to be a real None."""
        load.action(_payload([_row()]))

        record = _stg_records(captured)[0]
        assert record["per_ocu_dependiente"] is None
        assert record["per_ocu_no_dependiente"] is None


class TestCatalogs:
    def test_activity_catalog_is_upserted_so_reworded_descriptions_land(self, load, captured):
        load.action(_payload([_row()]))

        conflict_keys = next(keys for model, _, keys in captured["upserts"] if model is not StgEms)
        assert conflict_keys == ["codigo_actividad"]

    def test_status_catalog_is_inserted_do_nothing_so_ids_never_shift(self, load, captured):
        load.action(_payload([_row()]))

        assert [keys for _, _, keys in captured["inserts"]] == [["estatus"]]


class TestGuards:
    def test_empty_input_does_not_touch_the_database(self, load, captured):
        result = load.action({"df": pd.DataFrame(), "catalogs": {}})

        assert result == {"records_before": None}
        assert not captured["upserts"] and not captured["inserts"]
