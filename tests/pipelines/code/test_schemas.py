"""El modelo debe coincidir con el ERD aprobado."""

from sqlalchemy import Float

from core.pipelines.code.schemas import CatActividades, CatRegiones, StgPuntosActivacionReto


def test_las_coordenadas_son_float_opcionales_y_no_hay_geometria():
    tabla = StgPuntosActivacionReto.__table__

    assert isinstance(tabla.c.longitud.type, Float)
    assert isinstance(tabla.c.latitud.type, Float)
    assert tabla.c.longitud.nullable is True
    assert tabla.c.latitud.nullable is True
    assert "geom" not in tabla.c


def test_el_id_de_actividades_es_el_del_origen():
    columna = CatActividades.__table__.c.id

    assert columna.autoincrement is False


def test_las_regiones_son_unicas_y_con_id_generado():
    assert CatRegiones.__table__.c.region.unique is True
    assert CatRegiones.__table__.c.id.autoincrement is True


def test_el_punto_es_unico_por_corte_municipio_y_espacio():
    restricciones = {
        tuple(c.name for c in constraint.columns)
        for constraint in StgPuntosActivacionReto.__table__.constraints
        if constraint.name == "uq_stg_puntos_activacion_reto"
    }

    assert restricciones == {("fecha_corte", "municipio_id", "nombre_espacio")}


def test_la_actividad_es_opcional_y_la_region_no_tiene_fk_obligatoria_al_municipio():
    tabla = StgPuntosActivacionReto.__table__

    assert tabla.c.actividad_id.nullable is True
    assert not tabla.c.municipio_id.foreign_keys
