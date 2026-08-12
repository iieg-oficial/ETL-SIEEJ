import logging
from contextlib import contextmanager
from datetime import date

import pandas as pd
import pytest

from core.pipelines.indice_shf_vivienda.constants import LEVEL_ESTATAL, LEVEL_GLOBAL, LEVEL_MUNICIPAL
from core.pipelines.indice_shf_vivienda.schemas import (
    StgIndiceShfViviendaEstatal,
    StgIndiceShfViviendaGlobal,
    StgIndiceShfViviendaMunicipal,
)
from core.pipelines.indice_shf_vivienda.stages import load as load_module
from core.pipelines.indice_shf_vivienda.stages.load import IndiceShfViviendaLoad

SERIE_IDS = {"nacional": 1, "zm_guadalajara": 9}
ESTADO_IDS = {
    "jalisco": 14,
    "coahuila_de_zaragoza": 5,
    "ciudad_de_mexico": 9,
    "quintana_roo": 23,
    "veracruz_de_ignacio_de_la_llave": 30,
}
MUNICIPIO_IDS = {
    14: {"guadalajara": 14039, "zapopan": 14120},
    9: {"benito_juarez": 9014},
    23: {"benito_juarez": 23005},
    30: {"veracruz": 30193},
}


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

    monkeypatch.setattr(load_module, "get_mapping", lambda *a, **k: SERIE_IDS)
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
    monkeypatch.setattr(
        load_module,
        "get_cvegeo_mapping",
        lambda session, table, key, value, is_normalize=False, cve_ent=None: (
            ESTADO_IDS if table == "cvegeo_states" else MUNICIPIO_IDS.get(cve_ent, {})
        ),
    )
    return calls


@pytest.fixture
def load() -> IndiceShfViviendaLoad:
    stage = object.__new__(IndiceShfViviendaLoad)
    stage.logger = logging.getLogger("test.indice_shf_vivienda.load")
    stage.db = _FakeDb()
    return stage


def _level(rows: list[dict], columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=columns)


PERIOD = {"fecha": date(2026, 4, 1), "anio": 2026, "trimestre": 2, "indice": 214.03}


def _input(**overrides) -> dict[str, pd.DataFrame]:
    data = {
        LEVEL_GLOBAL: _level(
            [{"serie_global": "ZM Guadalajara", **PERIOD}],
            ["serie_global", "fecha", "anio", "trimestre", "indice"],
        ),
        LEVEL_ESTATAL: _level(
            [{"estado": "Jalisco", **PERIOD}],
            ["estado", "fecha", "anio", "trimestre", "indice"],
        ),
        LEVEL_MUNICIPAL: _level(
            [{"estado": "Jalisco", "municipio": "Zapopan", **PERIOD}],
            ["estado", "municipio", "fecha", "anio", "trimestre", "indice"],
        ),
    }
    data.update(overrides)
    return data


def test_resolves_every_key_and_upserts_the_three_levels(load, captured):
    load.action(_input())

    upserted = {model: records for model, records, _ in captured["upserts"]}
    assert set(upserted) == {StgIndiceShfViviendaGlobal, StgIndiceShfViviendaEstatal, StgIndiceShfViviendaMunicipal}
    assert upserted[StgIndiceShfViviendaGlobal][0]["serie_global_id"] == 9
    assert upserted[StgIndiceShfViviendaEstatal][0]["cve_ent"] == 14
    assert upserted[StgIndiceShfViviendaMunicipal][0]["cvegeo"] == 14120


def test_applies_the_alias_for_the_short_state_names(load, captured):
    """SHF publica 'Coahuila'; el Marco Geoestadístico dice 'Coahuila de Zaragoza'."""
    estatal = _level([{"estado": "Coahuila", **PERIOD}], ["estado", "fecha", "anio", "trimestre", "indice"])

    load.action(_input(**{LEVEL_ESTATAL: estatal}))

    upserted = {model: records for model, records, _ in captured["upserts"]}
    assert upserted[StgIndiceShfViviendaEstatal][0]["cve_ent"] == 5


def test_resolves_repeated_municipality_names_inside_their_own_state(load, captured):
    municipal = _level(
        [
            {"estado": "Ciudad de México", "municipio": "Benito Juárez", **PERIOD},
            {"estado": "Quintana Roo", "municipio": "Benito Juárez", **PERIOD},
        ],
        ["estado", "municipio", "fecha", "anio", "trimestre", "indice"],
    )

    load.action(_input(**{LEVEL_MUNICIPAL: municipal}))

    upserted = {model: records for model, records, _ in captured["upserts"]}
    assert sorted(r["cvegeo"] for r in upserted[StgIndiceShfViviendaMunicipal]) == [9014, 23005]


def test_aborts_instead_of_loading_a_row_without_its_key(load, captured):
    """Perder la clave en silencio deja filas imposibles de atribuir: es peor que no cargar."""
    municipal = _level(
        [{"estado": "Jalisco", "municipio": "Municipio Inexistente", **PERIOD}],
        ["estado", "municipio", "fecha", "anio", "trimestre", "indice"],
    )

    with pytest.raises(ValueError, match="Municipio Inexistente"):
        load.action(_input(**{LEVEL_MUNICIPAL: municipal}))


def test_state_aliases_do_not_leak_into_municipality_names(load, captured):
    """'Veracruz' nombra a la vez a la entidad y al municipio del puerto.

    Traducir el alias de la entidad en el nivel municipal mandaba a buscar un
    municipio llamado 'Veracruz de Ignacio de la Llave', que no existe.
    """
    municipal = _level(
        [{"estado": "Veracruz", "municipio": "Veracruz", **PERIOD}],
        ["estado", "municipio", "fecha", "anio", "trimestre", "indice"],
    )

    load.action(_input(**{LEVEL_MUNICIPAL: municipal}))

    upserted = {model: records for model, records, _ in captured["upserts"]}
    registro = upserted[StgIndiceShfViviendaMunicipal][0]
    assert registro["cve_ent"] == 30
    assert registro["cvegeo"] == 30193
