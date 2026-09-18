"""Cómo el load entrega los datos a la base, sin tocar PostgreSQL."""

import logging
from contextlib import contextmanager
from datetime import date

import pandas as pd
import pytest

from core.pipelines.secretaria_educacion.constants import AULAS_GOOGLE_DATASET
from core.pipelines.secretaria_educacion.schemas import (
    CatMedios,
    CatRegiones,
    CatTurnos,
    StgAulasGoogle,
)
from core.pipelines.secretaria_educacion.stages import load as load_module
from core.pipelines.secretaria_educacion.stages.load import SecretariaEducacionLoad

MUNICIPIOS_CVEGEO = [(98, "San Pedro Tlaquepaque"), (70, "El Salto"), (120, "Zapopan")]


class _FakeSession:
    """Solo responde lo que el load consulta: municipios de cvegeo y colonias."""

    def __init__(self):
        self.deletes = 0

    def execute(self, statement, params=None):
        if params is not None:
            return type("Result", (), {"all": lambda self: MUNICIPIOS_CVEGEO})()
        self.deletes += 1
        return None

    def query(self, *_columns):
        return type("Query", (), {"all": lambda self: []})()

    def flush(self):
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
    """Registra lo que el load entrega a los helpers de bulk_ops."""
    calls: dict = {"inserts": [], "upserts": [], "bulk": []}

    monkeypatch.setattr(load_module, "get_mapping", lambda *a, **k: {})
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
        "bulk_insert",
        lambda session, data, model: calls["bulk"].append((model, data)),
    )
    return calls


@pytest.fixture
def load() -> SecretariaEducacionLoad:
    stage = object.__new__(SecretariaEducacionLoad)
    stage.logger = logging.getLogger("test.secretaria_educacion.load")
    stage.db = _FakeDb()
    stage.mode = "bootstrap"
    return stage


CATALOGOS = {
    "turnos": [{"id": 120, "turno": "Matutino - Vespertino"}],
    "regiones": [{"id": 121, "region": "Centro ZMG"}],
    "medios": [{"medio": "Urbana"}],
}


def _aulas(municipio: str = "EL SALTO") -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "clave_ct": "14DES0135H",
                "nombre_ct": "Fray Servando",
                "inmueble": "1412827D",
                "region_operativa": "Centro 3",
                "municipio": municipio,
                "aulas_asignadas": 1,
                "entidad_id": 14,
                "fecha_corte": date(2026, 9, 10),
                "fecha_actualizacion_fuente": date(2026, 9, 1),
                "fecha_actualizacion": date(2026, 9, 18),
            }
        ]
    )


def test_los_catalogos_con_id_del_origen_se_actualizan(load, captured):
    """Con DO NOTHING una etiqueta corregida por la dependencia no se propagaría nunca."""
    load._load_catalogs(_FakeSession(), CATALOGOS)

    modelos_upserteados = {model for model, _, _ in captured["upserts"]}
    assert modelos_upserteados == {CatTurnos, CatRegiones}


def test_el_upsert_de_catalogos_va_por_el_id_del_origen(load, captured):
    load._load_catalogs(_FakeSession(), CATALOGOS)

    _, registros, conflict_keys = captured["upserts"][0]
    assert conflict_keys == ["id"]
    assert registros[0]["turno"] == "Matutino - Vespertino"


def test_los_catalogos_con_id_generado_se_insertan_por_su_valor(load, captured):
    load._load_catalogs(_FakeSession(), CATALOGOS)

    modelos_insertados = {model: keys for model, _, keys in captured["inserts"]}
    assert modelos_insertados[CatMedios] == ["medio"]


def test_un_catalogo_vacio_no_genera_escritura(load, captured):
    load._load_catalogs(_FakeSession(), {})

    assert captured["upserts"] == []
    assert captured["inserts"] == []


def test_el_municipio_de_aulas_se_resuelve_contra_cvegeo(load):
    mapeado = load._map_aulas(_FakeSession(), _aulas("EL SALTO"))

    assert mapeado["municipio_id"].item() == 70


def test_el_municipio_se_resuelve_sin_acentos_ni_mayusculas(load):
    mapeado = load._map_aulas(_FakeSession(), _aulas("SAN PEDRO TLAQUEPAQUE"))

    assert mapeado["municipio_id"].item() == 98


def test_un_municipio_sin_equivalencia_queda_nulo(load):
    # Preferimos un nulo explícito a inventar una clave equivocada.
    mapeado = load._map_aulas(_FakeSession(), _aulas("MUNICIPIO QUE NO EXISTE"))

    assert pd.isna(mapeado["municipio_id"].item())


def test_los_registros_excluyen_el_id_autoincremental(load):
    mapeado = load._map_aulas(_FakeSession(), _aulas())

    registros = load._records_from_df(mapeado, StgAulasGoogle)

    assert "id" not in registros[0]
    assert registros[0]["clave_ct"] == "14DES0135H"


def test_recargar_un_corte_borra_antes_de_insertar(load, captured):
    """La recarga por corte es lo que hace que correr dos veces no duplique."""
    session = _FakeSession()

    load._reload_dataset(session, AULAS_GOOGLE_DATASET, _aulas())

    assert session.deletes == 1
    modelo, registros = captured["bulk"][0]
    assert modelo is StgAulasGoogle
    assert len(registros) == 1
