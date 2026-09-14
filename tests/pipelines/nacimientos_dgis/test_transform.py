from datetime import date

import pandas as pd
import pytest

from core.pipelines.nacimientos_dgis.constants import EDAD_SENTINELS
from core.pipelines.nacimientos_dgis.stages.transform import NacimientosDgisTransform


@pytest.fixture
def transform() -> NacimientosDgisTransform:
    return NacimientosDgisTransform()


def _fuente(edades: list, edades_padre: list) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ENTIDADRESIDENCIA": [14] * len(edades),
            "MUNICIPIORESIDENCIA": [39] * len(edades),
            "EDAD": edades,
            "EDADPADRE": edades_padre,
            "FECHANACIMIENTO": ["14/02/2023"] * len(edades),
        }
    )


@pytest.mark.parametrize("centinela", sorted(EDAD_SENTINELS))
def test_centinela_de_edad_del_padre_no_es_una_edad(transform, centinela):
    """99 y 999 cambian según la edición; el 0 no está ni documentado."""
    df = transform._jalisco(2023, _fuente([30, 30], [35, centinela]))

    assert df["EDADPADRE"].tolist()[0] == 35
    assert pd.isna(df["EDADPADRE"].tolist()[1])


@pytest.mark.parametrize("centinela", sorted(EDAD_SENTINELS))
def test_centinela_de_edad_de_la_madre_saca_la_fila(transform, centinela):
    """`edad_madre` es llave del agregado: sin edad válida no hay grupo."""
    df = transform._jalisco(2023, _fuente([30, centinela], [35, 35]))

    assert df["EDAD"].tolist() == [30]


def test_padre_centinela_no_cuenta_como_padre_de_18_mas(transform):
    """El bug que inflaba el indicador de madres de 10-14 varios puntos."""
    fuente = _fuente([12, 12, 12], [25, 99, 999])
    agregado = transform._aggregate(2023, transform._jalisco(2023, fuente))

    fila = agregado.iloc[0]
    assert fila["tot_nac"] == 3
    assert fila["nac_padre_conocido"] == 1
    assert fila["nac_padre_18_mas"] == 1
    assert fila["nac_padre_25_mas"] == 1


def test_agregado_conserva_su_grano(transform):
    fuente = _fuente([20, 20, 21], [30, 40, None])
    agregado = transform._aggregate(2023, transform._jalisco(2023, fuente))

    assert agregado["edad_madre"].tolist() == [20, 21]
    assert agregado["tot_nac"].tolist() == [2, 1]
    assert agregado["nac_padre_conocido"].tolist() == [2, 0]
    assert agregado["fecha_actualizacion"].iloc[0] == date.today()
