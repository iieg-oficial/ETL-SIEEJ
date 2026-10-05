"""Las regiones llegan sucias del origen; el helper las vuelve etiquetas legibles."""

import pandas as pd
import pytest

from core.pipelines.code.helpers.values import title_es


@pytest.mark.parametrize(
    ("origen", "esperado"),
    [
        ("Altos Norte ", "Altos Norte"),
        ("Altos sur", "Altos Sur"),
        ("Cienega ", "Ciénega"),
        ("Costa-Sierra Occidental", "Costa-Sierra Occidental"),
        ("Sierra de Amula", "Sierra de Amula"),
        ("costa sur", "Costa Sur"),
    ],
)
def test_las_regiones_quedan_en_title_case_con_acentos(origen, esperado):
    assert title_es(origen) == esperado


def test_baja_las_preposiciones_menos_la_primera_palabra():
    assert title_es("DE AMULA") == "De Amula"
    assert title_es("SIERRA DE AMULA") == "Sierra de Amula"


def test_colapsa_espacios_repetidos():
    assert title_es("  Costa   Sur ") == "Costa Sur"


@pytest.mark.parametrize("vacio", [None, pd.NA, "", "   "])
def test_un_valor_vacio_devuelve_none(vacio):
    assert title_es(vacio) is None
