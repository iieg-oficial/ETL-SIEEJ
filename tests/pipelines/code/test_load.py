"""Como el load entrega los datos a la base, sin tocar PostgreSQL."""

from datetime import date

import pandas as pd

from core.pipelines.code.schemas import CargasAcervo, CatActividades, CatRegiones, StgPuntosActivacionReto
from core.pipelines.code.stages import load as load_module
from tests.pipelines.code.code_factories import FakeSession

MANIFEST = {
    "envio_id": 28,
    "conjunto": "Puntos de activación del programa Reto",
    "object_key": "k",
    "etag": "abc",
    "actualizado_en": "2026-09-09 17:16:53+00:00",
}


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
    load._load_catalogs(FakeSession(), CATALOGOS)

    modelo, registros, conflict_keys = captured["upserts"][0]
    assert modelo is CatActividades
    assert conflict_keys == ["id"]
    assert registros[0]["actividad"] == "Baile"


def test_las_regiones_con_id_generado_se_insertan_por_su_valor(load, captured):
    load._load_catalogs(FakeSession(), CATALOGOS)

    assert captured["inserts"] == [(CatRegiones, [{"region": "Altos Sur"}], ["region"])]


def test_un_catalogo_vacio_no_genera_escritura(load, captured):
    load._load_catalogs(FakeSession(), {})

    assert captured["upserts"] == []
    assert captured["inserts"] == []


def test_la_region_se_resuelve_contra_su_catalogo(load, captured):
    mapeado = load._map_foreign_keys(FakeSession(), _puntos())

    assert mapeado["region_id"].item() == 5


def test_los_registros_excluyen_el_id_y_el_texto_de_la_region(load, captured):
    mapeado = load._map_foreign_keys(FakeSession(), _puntos())

    registro = load._records_from_df(mapeado, StgPuntosActivacionReto)[0]

    assert "id" not in registro
    assert "region" not in registro
    assert registro["region_id"] == 5
    assert registro["actividad_id"] is None
    assert registro["longitud"] == -103.4
    assert registro["latitud"] == 20.7
    assert "geom" not in registro


def test_reemplazar_la_tabla_borra_antes_de_insertar(load, captured):
    """Cada envio trae el conjunto completo: correr dos veces no duplica."""
    session = FakeSession()

    load._replace_table(session, load._map_foreign_keys(session, _puntos()), StgPuntosActivacionReto)

    assert len(session.deletes) == 1
    modelo, registros = captured["bulk"][0]
    assert modelo is StgPuntosActivacionReto
    assert len(registros) == 1


def test_el_borrado_no_filtra_por_corte(load, captured):
    session = FakeSession()
    datos = load._map_foreign_keys(session, _puntos(cortes=(date(2026, 7, 1), date(2026, 8, 1))))

    load._replace_table(session, datos, StgPuntosActivacionReto)

    sentencia = str(session.deletes[0].compile(compile_kwargs={"literal_binds": True}))
    assert "WHERE" not in sentencia


def test_el_registro_de_carga_toma_el_corte_de_los_datos(load, captured):
    load._register_load(FakeSession(), MANIFEST, _puntos(cortes=(date(2026, 7, 1), date(2026, 8, 1))))

    modelo, registros, conflict_keys = captured["upserts"][0]
    assert modelo is CargasAcervo
    assert conflict_keys == ["envio_id", "object_key"]
    assert registros[0]["fecha_corte"] == date(2026, 8, 1)
    assert registros[0]["fecha_actualizacion_fuente"] == date(2026, 9, 9)
    assert registros[0]["etag"] == "abc"


def test_un_update_sin_cargas_nuevas_ni_siquiera_abre_la_conexion(load, captured):
    conexiones = []
    load.db.connect = lambda: conexiones.append("connect")

    load.action({})

    assert conexiones == []
    assert captured["bulk"] == []


def test_recargar_puntos_refresca_la_vista_materializada(load, monkeypatch):
    refrescos = []
    monkeypatch.setattr(load, "_load_dataset", lambda *_args: None)
    monkeypatch.setattr(
        load_module,
        "refresh_materialized_views",
        lambda db, views: refrescos.append((db, views)),
    )

    load.action({"reto": {"frames": {"puntos": _puntos()}, "manifest": MANIFEST, "catalogs": {}}})

    assert refrescos == [(load.db, ("vm_reto_code_geo",))]
