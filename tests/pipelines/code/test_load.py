"""Como el load entrega los datos a la base, sin tocar PostgreSQL."""

import logging
from contextlib import contextmanager
from datetime import date

import pandas as pd
import pytest

from core.pipelines.code.schemas import CargasAcervo, CatActividades, CatRegiones, StgPuntosActivacionReto
from core.pipelines.code.stages import load as load_module
from core.pipelines.code.stages.load import CodeLoad

MANIFEST = {
    "envio_id": 28,
    "conjunto": "Puntos de activación del programa Reto",
    "object_key": "k",
    "etag": "abc",
    "actualizado_en": "2026-09-09 17:16:53+00:00",
}


class _FakeSession:
    def __init__(self):
        self.deletes = []

    def execute(self, statement, params=None):
        self.deletes.append(statement)
        return None

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
    calls: dict = {"inserts": [], "upserts": [], "bulk": []}

    monkeypatch.setattr(load_module, "get_mapping", lambda *a, **k: {"Altos Sur": 5, "Norte": 9})
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
def load() -> CodeLoad:
    stage = object.__new__(CodeLoad)
    stage.logger = logging.getLogger("test.code.load")
    stage.db = _FakeDb()
    stage.mode = "bootstrap"
    return stage


def _puntos(cortes=(date(2026, 7, 1),)) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "clave_punto": i,
                "region": "Altos Sur",
                "municipio_id": 120,
                "nombre_espacio": f"Espacio {i}",
                "dias_horarios": "L - V",
                "actividad_id": pd.NA,
                "cantidad_usuarios": 14,
                "longitud": -103.4,
                "latitud": 20.7,
                "entidad_id": 14,
                "fecha_corte": corte,
                "fecha_actualizacion_fuente": date(2026, 9, 9),
                "fecha_actualizacion": date(2026, 10, 5),
            }
            for i, corte in enumerate(cortes, start=1)
        ]
    )


CATALOGOS = {
    "actividades": [{"id": 1, "actividad": "Baile"}],
    "regiones": [{"region": "Altos Sur"}],
}


def test_las_actividades_con_id_del_origen_se_actualizan(load, captured):
    """Con DO NOTHING una etiqueta corregida por la dependencia no se propagaria."""
    load._load_catalogs(_FakeSession(), CATALOGOS)

    modelo, registros, conflict_keys = captured["upserts"][0]
    assert modelo is CatActividades
    assert conflict_keys == ["id"]
    assert registros[0]["actividad"] == "Baile"


def test_las_regiones_con_id_generado_se_insertan_por_su_valor(load, captured):
    load._load_catalogs(_FakeSession(), CATALOGOS)

    assert captured["inserts"] == [(CatRegiones, [{"region": "Altos Sur"}], ["region"])]


def test_un_catalogo_vacio_no_genera_escritura(load, captured):
    load._load_catalogs(_FakeSession(), {})

    assert captured["upserts"] == []
    assert captured["inserts"] == []


def test_la_region_se_resuelve_contra_su_catalogo(load, captured):
    mapeado = load._map_foreign_keys(_FakeSession(), _puntos())

    assert mapeado["region_id"].item() == 5


def test_los_registros_excluyen_el_id_y_el_texto_de_la_region(load, captured):
    mapeado = load._map_foreign_keys(_FakeSession(), _puntos())

    registro = load._records_from_df(mapeado, StgPuntosActivacionReto)[0]

    assert "id" not in registro
    assert "region" not in registro
    assert registro["region_id"] == 5
    assert registro["actividad_id"] is None
    assert registro["longitud"] == -103.4
    assert registro["latitud"] == 20.7
    assert "geom" not in registro


def test_recargar_un_corte_borra_antes_de_insertar(load, captured):
    """La recarga por corte es lo que hace que correr dos veces no duplique."""
    session = _FakeSession()

    load._reload_puntos(session, _puntos())

    assert len(session.deletes) == 1
    modelo, registros = captured["bulk"][0]
    assert modelo is StgPuntosActivacionReto
    assert len(registros) == 1


def test_el_borrado_cubre_todos_los_cortes_del_archivo(load, captured):
    session = _FakeSession()

    load._reload_puntos(session, _puntos(cortes=(date(2026, 7, 1), date(2026, 8, 1), date(2026, 7, 1))))

    sentencia = str(session.deletes[0].compile(compile_kwargs={"literal_binds": True}))
    assert "2026-07-01" in sentencia and "2026-08-01" in sentencia


def test_el_registro_de_carga_toma_el_corte_de_los_datos(load, captured):
    load._register_load(_FakeSession(), MANIFEST, _puntos(cortes=(date(2026, 7, 1), date(2026, 8, 1))))

    modelo, registros, conflict_keys = captured["upserts"][0]
    assert modelo is CargasAcervo
    assert conflict_keys == ["envio_id", "object_key"]
    assert registros[0]["fecha_corte"] == date(2026, 8, 1)
    assert registros[0]["fecha_actualizacion_fuente"] == date(2026, 9, 9)
    assert registros[0]["etag"] == "abc"


def test_un_update_sin_cargas_nuevas_ni_siquiera_abre_la_conexion(load, captured):
    conexiones = []
    load.db.connect = lambda: conexiones.append("connect")

    load.action({"frames": {}, "manifest": {}, "catalogs": {}})

    assert conexiones == []
    assert captured["bulk"] == []
