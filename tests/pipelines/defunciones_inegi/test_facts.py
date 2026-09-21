"""Los componentes de fecha se conservan por separado de la fecha armada."""

from datetime import date

import pandas as pd
import pytest

from core.pipelines.defunciones_inegi.constants import DATE_COMPONENTS, DATE_PARTS
from core.pipelines.defunciones_inegi.helpers.facts import apply_numeric_sentinels, build_dates

OCURRENCIA = "fecha_ocurrencia"
DIA, MES, ANIO = DATE_COMPONENTS[OCURRENCIA]


def frame(**ocurrencia) -> pd.DataFrame:
    """Una fila con los componentes crudos de todas las fechas que espera `build_dates`."""
    row = {column: 1 for parts in DATE_PARTS.values() for column in parts}
    row |= {"anio_ocur": 2019, "anio_regis": 2019, "anio_nacim": 2019, "anio_cert": 2019}
    row |= dict(zip(DATE_PARTS[OCURRENCIA], (ocurrencia["dia"], ocurrencia["mes"], ocurrencia["anio"]), strict=True))
    return pd.DataFrame([row])


def test_fecha_completa_conserva_sus_tres_componentes():
    result = build_dates(frame(dia=5, mes=3, anio=2019)).iloc[0]

    assert result[OCURRENCIA] == date(2019, 3, 5)
    assert (result[DIA], result[MES], result[ANIO]) == (5, 3, 2019)


@pytest.mark.parametrize(
    ("dia", "mes"),
    [(99, 3), (5, 99), (99, 99)],
    ids=["sin dia", "sin mes", "sin dia ni mes"],
)
def test_dia_o_mes_no_especificado_conserva_el_anio(dia, mes):
    result = build_dates(frame(dia=dia, mes=mes, anio=2019)).iloc[0]

    assert result[ANIO] == 2019
    assert pd.isna(result[OCURRENCIA])


def test_anio_no_especificado_no_se_vuelve_una_fecha_artificial():
    result = build_dates(frame(dia=5, mes=3, anio=9999)).iloc[0]

    assert pd.isna(result[ANIO])
    assert pd.isna(result[OCURRENCIA])
    assert (result[DIA], result[MES]) == (5, 3)


def test_fecha_de_calendario_invalida_conserva_los_componentes():
    """31 de febrero no existe, pero los tres valores publicados sí son informativos."""
    result = build_dates(frame(dia=31, mes=2, anio=2019)).iloc[0]

    assert pd.isna(result[OCURRENCIA])
    assert (result[DIA], result[MES], result[ANIO]) == (31, 2, 2019)


def test_los_componentes_crudos_de_la_fuente_se_descartan():
    result = build_dates(frame(dia=5, mes=3, anio=2019))

    assert not set(DATE_PARTS[OCURRENCIA]) & set(result.columns)


def test_una_edicion_sin_columnas_de_fecha_deja_todo_nulo():
    result = build_dates(pd.DataFrame([{"edicion": 2019}])).iloc[0]

    for target, components in DATE_COMPONENTS.items():
        assert pd.isna(result[target])
        assert all(pd.isna(result[column]) for column in components)


def test_el_distrito_de_oaxaca_999_se_guarda_como_nulo():
    """999 marca los registros fuera de Oaxaca, que no tienen distrito."""
    df = pd.DataFrame([{"distrito_registro_oaxaca": 999}, {"distrito_registro_oaxaca": 927}])

    result = apply_numeric_sentinels(df)

    assert pd.isna(result["distrito_registro_oaxaca"].iloc[0])
    assert result["distrito_registro_oaxaca"].iloc[1] == 927
