"""Reglas de limpieza que salieron de inspeccionar el xlsx real de CODE."""

from datetime import date

import pandas as pd
import pytest

from core.pipelines.code.constants import PUNTOS_COLUMNS
from core.pipelines.code.stages.transform import CodeTransform

MANIFEST = {"envio_id": 28, "actualizado_en": "2026-09-09 17:16:53.235786+00:00"}

# Encabezados y valores del origen, incluidos los espacios sobrantes.
FILA = {
    "fecha": pd.Timestamp("2026-07-01"),
    "id": 7,
    "region": "Altos sur ",
    "municipio": "ZMG Zapopan",
    "clave_agem": 120,
    "espacio": "  Unidad  Deportiva ",
    "dias_y_horarios": "L - Mi - V de 18:00 a 19:30",
    "actividad": "Baile ",
    "cat_actividad": 3.0,
    "cantidad_de_usuarios": 14,
    "y": 20.7,
    "x": -103.4,
}

CATALOGO = pd.DataFrame({"actividad": ["Baile ", "Zumba"], "id": [1, 2]})


def _puntos(**cambios) -> pd.DataFrame:
    return pd.DataFrame([{**FILA, **cambios}])


def _preparar(**cambios) -> pd.DataFrame:
    return CodeTransform()._prepare_puntos(_puntos(**cambios), MANIFEST)


def test_las_regiones_se_limpian_con_title_case_y_acentos():
    assert _preparar(region="CIENEGA ")["region"].item() == "Ciénega"


def test_el_nombre_del_municipio_no_sobrevive_al_transform():
    # El nombre se resuelve en la vista contra cvegeo.
    salida = _preparar()

    assert "municipio" not in salida.columns
    assert salida["municipio_id"].item() == 120


def test_el_texto_libre_se_limpia_de_espacios():
    assert _preparar()["nombre_espacio"].item() == "Unidad Deportiva"


def test_los_horarios_no_se_parsean():
    assert _preparar()["dias_horarios"].item() == "L - Mi - V de 18:00 a 19:30"


def test_la_actividad_flotante_pasa_a_entero_nullable():
    assert _preparar()["actividad_id"].item() == 3


def test_una_actividad_faltante_queda_nula():
    assert pd.isna(_preparar(cat_actividad=float("nan"), actividad=None)["actividad_id"].item())


def test_las_coordenadas_x_e_y_pasan_a_longitud_y_latitud():
    salida = _preparar()

    assert salida["longitud"].item() == -103.4
    assert salida["latitud"].item() == 20.7


def test_sin_coordenadas_quedan_nulas():
    salida = _preparar(x=float("nan"), y=float("nan"))

    assert pd.isna(salida["longitud"].item())
    assert pd.isna(salida["latitud"].item())


def test_no_se_construye_geometria():
    assert "geom" not in _preparar().columns


def test_la_entidad_se_fija_a_jalisco():
    assert _preparar()["entidad_id"].item() == 14


def test_el_corte_sale_de_la_columna_fecha_de_los_datos():
    assert _preparar()["fecha_corte"].item() == date(2026, 7, 1)


def test_la_actualizacion_de_la_fuente_sale_de_la_fecha_del_envio():
    assert _preparar()["fecha_actualizacion_fuente"].item() == date(2026, 9, 9)


def test_la_fecha_de_actualizacion_es_hoy():
    assert _preparar()["fecha_actualizacion"].item() == date.today()


def test_una_fecha_de_corte_vacia_es_un_error():
    with pytest.raises(ValueError, match="fecha"):
        _preparar(fecha=pd.NaT)


def test_las_filas_vacias_del_final_se_descartan():
    vacia = dict.fromkeys(FILA, None)
    df = pd.DataFrame([FILA, vacia, vacia])

    assert len(CodeTransform()._prepare_puntos(df, MANIFEST)) == 1


def test_standardize_avisa_cuando_el_origen_pierde_una_columna_modelada():
    df = _puntos().drop(columns=["cantidad_de_usuarios"])

    with pytest.raises(KeyError, match="cantidad_usuarios"):
        CodeTransform()._prepare_puntos(df, MANIFEST)


def test_las_columnas_modeladas_sobreviven_completas():
    salida = _preparar()

    assert not [c for c in PUNTOS_COLUMNS if c not in salida.columns]


def test_el_catalogo_de_actividades_conserva_el_id_del_origen():
    catalogo = CodeTransform()._build_catalogs(_preparar(), CATALOGO)["actividades"]

    assert catalogo == [{"id": 1, "actividad": "Baile"}, {"id": 2, "actividad": "Zumba"}]


def test_el_catalogo_de_regiones_sale_de_los_valores_ya_limpios():
    df = pd.concat([_puntos(region="Norte "), _puntos(region="norte"), _puntos(region="Altos sur")])
    preparado = CodeTransform()._prepare_puntos(df, MANIFEST)

    regiones = CodeTransform()._build_catalogs(preparado, CATALOGO)["regiones"]

    assert regiones == [{"region": "Altos Sur"}, {"region": "Norte"}]


def test_un_update_sin_cargas_nuevas_no_es_un_error():
    salida = CodeTransform(mode="update").action({"frames": {}, "manifest": {}})

    assert salida["frames"] == {}
    assert salida["catalogs"] == {}
