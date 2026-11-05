"""Modelos de los conjuntos Academias y Polideportivos."""

from sqlalchemy import Float

from core.pipelines.code.schemas import (
    CatDeportes,
    CatTiposAcademia,
    PolideportivoDeportes,
    StgAcademiasDeportivas,
    StgPolideportivos,
)


def _unique(model, name):
    return {
        tuple(c.name for c in constraint.columns)
        for constraint in model.__table__.constraints
        if constraint.name == name
    }


def test_los_deportes_conservan_el_id_del_origen_y_nombres_unicos():
    table = CatDeportes.__table__

    assert table.c.id.autoincrement is False
    assert table.c.deporte.unique is True


def test_los_tipos_de_academia_tienen_id_generado_y_nombres_unicos():
    table = CatTiposAcademia.__table__

    assert table.c.id.autoincrement is True
    assert table.c.tipo.unique is True


def test_academias_referencia_ambos_catalogos():
    table = StgAcademiasDeportivas.__table__

    assert {fk.target_fullname for fk in table.c.deporte_id.foreign_keys} == {"cat_deportes.id"}
    assert {fk.target_fullname for fk in table.c.tipo_id.foreign_keys} == {"cat_tipos_academia.id"}
    assert table.c.deporte_id.nullable is False
    assert table.c.tipo_id.nullable is False


def test_academias_tienen_coordenadas_float_y_no_geometria():
    table = StgAcademiasDeportivas.__table__

    assert isinstance(table.c.longitud.type, Float) and isinstance(table.c.latitud.type, Float)
    assert "geom" not in table.c


def test_academias_sin_llave_unica_porque_el_origen_repite_filas_por_sede():
    assert not [c for c in StgAcademiasDeportivas.__table__.constraints if c.name and c.name.startswith("uq_")]


def test_el_polideportivo_es_unico_por_corte_municipio_y_nombre():
    assert _unique(StgPolideportivos, "uq_stg_polideportivos") == {("fecha_corte", "municipio_id", "nombre_centro")}


def test_la_puente_tiene_llave_compuesta_y_borra_en_cascada():
    table = PolideportivoDeportes.__table__

    assert [c.name for c in table.primary_key.columns] == ["polideportivo_id", "deporte_id"]
    fk = next(iter(table.c.polideportivo_id.foreign_keys))
    assert fk.ondelete == "CASCADE"
    assert {f.target_fullname for f in table.c.deporte_id.foreign_keys} == {"cat_deportes.id"}


def _indexes(model):
    return {index.name: tuple(c.name for c in index.columns) for index in model.__table__.indexes}


def test_academias_declara_el_indice_por_corte_de_la_migracion():
    assert _indexes(StgAcademiasDeportivas)["ix_stg_academias_deportivas_fecha_corte"] == ("fecha_corte",)


def test_la_puente_declara_el_indice_por_deporte_de_la_migracion():
    assert _indexes(PolideportivoDeportes)["ix_polideportivo_deportes_deporte_id"] == ("deporte_id",)
