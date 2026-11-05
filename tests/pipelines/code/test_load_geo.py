"""Load de Academias y Polideportivos, sin tocar PostgreSQL."""

from datetime import date

import pandas as pd
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from core.pipelines.code.schemas import (
    CargasAcervo,
    CatDeportes,
    CatRegiones,
    CatTiposAcademia,
    CodeBase,
    PolideportivoDeportes,
    StgAcademiasDeportivas,
    StgPolideportivos,
    StgPuntosActivacionReto,
)
from core.pipelines.code.stages import load as load_module
from tests.pipelines.code.code_factories import FakeSession

MANIFEST = {
    "envio_id": 28,
    "conjunto": "Academias deportivas, Espacios para la Paz",
    "object_key": "k",
    "etag": "abc",
    "actualizado_en": "2026-10-22 22:27:17+00:00",
}

COMMON = {
    "entidad_id": 14,
    "municipio_id": 39,
    "longitud": -103.3,
    "latitud": 20.7,
    "fecha_corte": date(2026, 10, 1),
    "fecha_actualizacion_fuente": date(2026, 10, 22),
    "fecha_actualizacion": date(2026, 10, 28),
}


def _academias() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                **COMMON,
                "deporte_id": 13,
                "tipo": "Regular",
                "deporte_nombre_largo": "CHARRERÍA",
                "beneficiarios_total": 75,
                "beneficiarios_hombres": pd.NA,
                "beneficiarios_mujeres": 38,
                "domicilio": "Plaza 1",
                "horarios": "Lunes",
            }
        ]
    )


def _polideportivos() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {**COMMON, "nombre_centro": nombre, "domicilio": "x", "horarios": "y", "servicios": "z"}
            for nombre in ("Alcalde", "Metropolitano")
        ]
    )


def _bridge() -> pd.DataFrame:
    keys = {"fecha_corte": date(2026, 10, 1), "municipio_id": 39}
    return pd.DataFrame(
        [
            {**keys, "nombre_centro": "Alcalde", "deporte_id": 19},
            {**keys, "nombre_centro": "Alcalde", "deporte_id": 13},
            {**keys, "nombre_centro": "Metropolitano", "deporte_id": 19},
        ]
    )


@pytest.fixture
def tipos(monkeypatch):
    monkeypatch.setattr(load_module, "get_mapping", lambda *a, **k: {"Regular": 2})


def test_los_deportes_se_actualizan_por_el_id_del_origen(load, captured):
    load._load_deportes(FakeSession(), {"deportes": [{"id": 19, "deporte": "Natación"}]})

    model, rows, keys = captured["upserts"][0]
    assert (model, keys) == (CatDeportes, ["id"])
    assert rows == [{"id": 19, "deporte": "Natación"}]


def test_academias_el_tipo_se_resuelve_a_su_id(load, captured, tipos):
    session = FakeSession()

    load._reload_academias(session, _academias())

    model, rows = captured["bulk"][0]
    assert model is StgAcademiasDeportivas
    assert rows[0]["tipo_id"] == 2
    assert rows[0]["deporte_id"] == 13
    assert rows[0]["beneficiarios_hombres"] is None
    assert not {"id", "tipo"} & set(rows[0])


def test_academias_con_un_tipo_sin_catalogo_falla(load, captured, monkeypatch):
    monkeypatch.setattr(load_module, "get_mapping", lambda *a, **k: {})

    with pytest.raises(ValueError, match="Regular"):
        load._reload_academias(FakeSession(), _academias())


def test_polideportivos_la_puente_apunta_a_las_filas_insertadas(load, captured, monkeypatch):
    ids = {(date(2026, 10, 1), 39, "Alcalde"): 7, (date(2026, 10, 1), 39, "Metropolitano"): 8}
    monkeypatch.setattr(load, "_polideportivo_ids", lambda session, cuts: ids)

    load._reload_polideportivos(FakeSession(), _polideportivos(), _bridge())

    (main_model, main_rows), (bridge_model, bridge_rows) = captured["bulk"]
    assert main_model is StgPolideportivos and len(main_rows) == 2
    assert bridge_model is PolideportivoDeportes
    assert sorted((r["polideportivo_id"], r["deporte_id"]) for r in bridge_rows) == [(7, 13), (7, 19), (8, 19)]


def test_polideportivos_sin_fila_puente_igual_se_cargan(load, captured, monkeypatch):
    monkeypatch.setattr(load, "_polideportivo_ids", lambda session, cuts: {})

    load._reload_polideportivos(FakeSession(), _polideportivos(), _bridge().iloc[0:0])

    assert [model for model, _ in captured["bulk"]] == [StgPolideportivos]


def test_el_registro_de_carga_usa_el_nombre_de_cada_conjunto(load, captured):
    load._register_load(FakeSession(), MANIFEST, _academias())

    model, rows, keys = captured["upserts"][0]
    assert model is CargasAcervo
    assert rows[0]["conjunto"] == "Academias deportivas, Espacios para la Paz"
    assert rows[0]["fecha_corte"] == date(2026, 10, 1)


def test_las_deportes_con_otro_nombre_para_el_mismo_id_se_rechazan(load, captured, monkeypatch):
    monkeypatch.setattr(load_module, "get_mapping", lambda *a, **k: {19: "Natación"})

    with pytest.raises(ValueError, match="19"):
        load._load_deportes(FakeSession(), {"deportes": [{"id": 19, "deporte": "Surf"}]})

    assert captured["upserts"] == []


def test_un_nombre_de_deporte_con_otro_id_se_rechaza(load, captured, monkeypatch):
    monkeypatch.setattr(load_module, "get_mapping", lambda *a, **k: {19: "Natación"})

    with pytest.raises(ValueError, match="Natación"):
        load._load_deportes(FakeSession(), {"deportes": [{"id": 20, "deporte": "Natacion"}]})


def test_un_deporte_repetido_con_ids_distintos_en_el_mismo_catalogo_se_rechaza(load, captured, monkeypatch):
    monkeypatch.setattr(load_module, "get_mapping", lambda *a, **k: {})
    catalogo = {"deportes": [{"id": 1, "deporte": "Box"}, {"id": 2, "deporte": "box"}]}

    with pytest.raises(ValueError, match="box"):
        load._load_deportes(FakeSession(), catalogo)


def test_un_deporte_que_solo_cambia_en_mayusculas_o_acentos_se_actualiza(load, captured, monkeypatch):
    monkeypatch.setattr(load_module, "get_mapping", lambda *a, **k: {19: "natacion"})

    load._load_deportes(FakeSession(), {"deportes": [{"id": 19, "deporte": "Natación"}]})

    assert captured["upserts"][0][1] == [{"id": 19, "deporte": "Natación"}]


def test_un_catalogo_de_deportes_vacio_no_escribe(load, captured, monkeypatch):
    monkeypatch.setattr(load_module, "get_mapping", lambda *a, **k: {})

    load._load_deportes(FakeSession(), {})

    assert captured["upserts"] == []


def _entrada(deportes, frames=None):
    return {"frames": frames or {}, "manifest": MANIFEST, "catalogs": {"deportes": deportes}}


def test_dos_conjuntos_con_deportes_en_conflicto_no_se_cargan_pero_reto_si(load, captured, monkeypatch):
    cargados = []
    monkeypatch.setattr(load, "_load_dataset", lambda session, key, entry: cargados.append(key))
    monkeypatch.setattr(load_module, "refresh_materialized_views", lambda db, views: None)
    datos = {
        "reto": {"frames": {}, "manifest": MANIFEST, "catalogs": {}},
        "academias": _entrada([{"id": 1, "deporte": "Box"}]),
        "polideportivos": _entrada([{"id": 1, "deporte": "Surf"}]),
    }

    with pytest.raises(ExceptionGroup) as error:
        load.action(datos)

    assert cargados == ["reto"]
    mensajes = " ".join(str(e) for e in error.value.exceptions)
    assert "academias" in mensajes and "polideportivos" in mensajes


def test_un_conjunto_que_falla_no_detiene_a_los_demas_y_la_tarea_falla(load, captured, monkeypatch):
    cargados, refrescos = [], []

    def cargar(session, key, entry):
        if key == "academias":
            raise ValueError("falla academias")
        cargados.append(key)

    monkeypatch.setattr(load, "_load_dataset", cargar)
    monkeypatch.setattr(load_module, "refresh_materialized_views", lambda db, views: refrescos.append(views))
    entrada = {"frames": {}, "manifest": MANIFEST, "catalogs": {}}

    with pytest.raises(ExceptionGroup, match="academias") as error:
        load.action({"reto": entrada, "academias": entrada, "polideportivos": entrada})

    assert cargados == ["reto", "polideportivos"]
    assert refrescos == [("vm_reto_code_geo",)]
    assert [str(e) for e in error.value.exceptions] == ["falla academias"]


def test_si_falla_reto_no_se_refresca_la_vista_y_los_demas_cargan(load, captured, monkeypatch):
    cargados, refrescos = [], []

    def cargar(session, key, entry):
        if key == "reto":
            raise ValueError("falla reto")
        cargados.append(key)

    monkeypatch.setattr(load, "_load_dataset", cargar)
    monkeypatch.setattr(load_module, "refresh_materialized_views", lambda db, views: refrescos.append(views))
    entrada = {"frames": {}, "manifest": MANIFEST, "catalogs": {}}

    with pytest.raises(ExceptionGroup):
        load.action({"reto": entrada, "academias": entrada})

    assert cargados == ["academias"]
    assert refrescos == []


def test_solo_reto_refresca_la_vista_materializada(load, captured, monkeypatch):
    refrescos = []
    monkeypatch.setattr(load, "_load_dataset", lambda *_a: None)
    monkeypatch.setattr(load_module, "refresh_materialized_views", lambda db, views: refrescos.append(views))
    entrada = {"frames": {}, "manifest": MANIFEST, "catalogs": {}}

    load.action({"academias": entrada})

    assert refrescos == []


def test_cada_conjunto_se_carga_en_su_propia_sesion(load, captured, monkeypatch):
    sesiones = []
    original = load.db.get_session
    load.db.get_session = lambda: (sesiones.append(1), original())[1]
    monkeypatch.setattr(load, "_load_dataset", lambda *_a: None)
    monkeypatch.setattr(load_module, "refresh_materialized_views", lambda *_a: None)
    entrada = {"frames": {}, "manifest": MANIFEST, "catalogs": {}}

    load.action({"academias": entrada, "polideportivos": entrada})

    assert len(sesiones) == 2


# Reemplazo: cada envio trae el conjunto completo, asi que la tabla no conserva cortes viejos.


@pytest.fixture
def sesion(monkeypatch):
    engine = create_engine("sqlite://", poolclass=StaticPool)
    event.listen(engine, "connect", lambda conexion, _: conexion.execute("PRAGMA foreign_keys=ON"))
    CodeBase.metadata.create_all(engine)
    monkeypatch.setattr(load_module, "sync_id_sequence", lambda session, model: None)
    with Session(engine) as session:
        session.add_all(
            [
                CatDeportes(id=19, deporte="Natación"),
                CatDeportes(id=13, deporte="Charrería"),
                CatTiposAcademia(id=2, tipo="Regular"),
                CatRegiones(id=5, region="Altos Sur"),
            ]
        )
        session.commit()
        yield session


def _con_corte(df: pd.DataFrame, corte: date) -> pd.DataFrame:
    return df.assign(fecha_corte=corte)


def _cortes(session, modelo) -> list:
    return sorted({fila[0] for fila in session.query(modelo.fecha_corte)})


def test_recargar_polideportivos_con_otro_corte_deja_solo_el_corte_nuevo(load, sesion):
    viejo, nuevo = date(2026, 9, 30), date(2026, 10, 1)
    load._reload_polideportivos(sesion, _con_corte(_polideportivos(), viejo), _con_corte(_bridge(), viejo))
    sesion.commit()

    load._reload_polideportivos(sesion, _con_corte(_polideportivos(), nuevo), _con_corte(_bridge(), nuevo))
    sesion.commit()

    assert _cortes(sesion, StgPolideportivos) == [nuevo]
    assert sesion.query(StgPolideportivos).count() == 2


def test_recargar_polideportivos_borra_en_cascada_el_puente_del_corte_viejo(load, sesion):
    viejo, nuevo = date(2026, 9, 30), date(2026, 10, 1)
    load._reload_polideportivos(sesion, _con_corte(_polideportivos(), viejo), _con_corte(_bridge(), viejo))
    sesion.commit()

    load._reload_polideportivos(sesion, _con_corte(_polideportivos(), nuevo), _con_corte(_bridge(), nuevo))
    sesion.commit()

    assert sesion.query(PolideportivoDeportes).count() == 3
    ids_vivos = {fila[0] for fila in sesion.query(StgPolideportivos.id)}
    assert {fila[0] for fila in sesion.query(PolideportivoDeportes.polideportivo_id)} <= ids_vivos


def test_recargar_academias_con_otro_corte_deja_solo_el_corte_nuevo(load, sesion):
    viejo, nuevo = date(2026, 9, 30), date(2026, 10, 1)
    load._reload_academias(sesion, _con_corte(_academias(), viejo))
    sesion.commit()

    load._reload_academias(sesion, _con_corte(_academias(), nuevo))
    sesion.commit()

    assert _cortes(sesion, StgAcademiasDeportivas) == [nuevo]


def test_recargar_reto_con_otro_corte_deja_solo_el_corte_nuevo(load, sesion):
    viejo, nuevo = date(2026, 9, 30), date(2026, 10, 1)
    for corte in (viejo, nuevo):
        df = load._map_foreign_keys(sesion, _puntos_reto(corte))
        load._replace_table(sesion, df, StgPuntosActivacionReto)
        sesion.commit()

    assert _cortes(sesion, StgPuntosActivacionReto) == [nuevo]


def test_si_falla_el_insert_la_tabla_conserva_las_filas_anteriores(load, sesion, monkeypatch):
    viejo = date(2026, 9, 30)
    load._reload_academias(sesion, _con_corte(_academias(), viejo))
    sesion.commit()
    monkeypatch.setattr(load_module, "bulk_insert", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("insert")))

    with pytest.raises(RuntimeError):
        load._reload_academias(sesion, _con_corte(_academias(), date(2026, 10, 1)))
    sesion.rollback()

    assert _cortes(sesion, StgAcademiasDeportivas) == [viejo]


def _puntos_reto(corte: date) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "clave_punto": 1,
                "region": "Altos Sur",
                "municipio_id": 120,
                "nombre_espacio": "Espacio 1",
                "dias_horarios": "L",
                "actividad_id": pd.NA,
                "cantidad_usuarios": 14,
                "longitud": -103.4,
                "latitud": 20.7,
                "entidad_id": 14,
                "fecha_corte": corte,
                "fecha_actualizacion_fuente": date(2026, 9, 9),
                "fecha_actualizacion": date(2026, 10, 5),
            }
        ]
    )
