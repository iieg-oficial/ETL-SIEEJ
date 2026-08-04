import pandas as pd

from core.pipelines.scian.constants import SHEET_COLUMNS
from core.pipelines.scian.stages.transform import ScianTransform


def _hoja(filas: list[list]) -> pd.DataFrame:
    return pd.DataFrame(filas, columns=SHEET_COLUMNS)


def _estructura_minima() -> pd.DataFrame:
    return _hoja(
        [
            ["11", "Agricultura y cazaT", None, None, None, None],
            [None, "111", "AgriculturaT", None, None, None],
            [None, None, "1111", "Cultivo de cerealesT", None, None],
            [None, None, None, "11111", "Cultivo de soyaT", None],
            [None, None, None, None, "111110", "Cultivo de soya "],
            ["31-33 ", "Industrias manufacturerasT", None, None, None, None],
            [None, "311", "Industria alimentaria", None, None, None],
            [None, None, "3111", "Elaboracion de alimentos", None, None],
            [None, None, None, "31111", "Elaboracion de alimentos", None],
            [None, None, None, None, "311110", "Elaboracion de alimentos"],
        ]
    )


def test_jerarquia_encadena_por_sangria_no_por_prefijo():
    salida = ScianTransform().action(_estructura_minima())

    assert salida["df_sectores"]["codigo"].tolist() == ["11", "31-33"]
    assert salida["df_subsectores"]["padre"].tolist() == ["11", "31-33"]
    assert salida["df_ramas"]["padre"].tolist() == ["111", "311"]
    assert salida["df_subramas"]["padre"].tolist() == ["1111", "3111"]
    assert salida["df_clases"]["padre"].tolist() == ["11111", "31111"]


def test_sufijo_trinacional_se_extrae_y_se_borra_del_texto():
    salida = ScianTransform().action(_estructura_minima())

    sectores = salida["df_sectores"]
    assert sectores["descripcion"].tolist() == ["Agricultura y caza", "Industrias manufactureras"]
    assert sectores["comparable_trinacional"].tolist() == [True, True]

    subsectores = salida["df_subsectores"]
    assert subsectores["descripcion"].tolist() == ["Agricultura", "Industria alimentaria"]
    assert subsectores["comparable_trinacional"].tolist() == [True, False]


def test_clases_no_llevan_columna_trinacional_ni_espacios_colgantes():
    df_clases = ScianTransform().action(_estructura_minima())["df_clases"]

    assert "comparable_trinacional" not in df_clases.columns
    assert df_clases["descripcion"].tolist() == ["Cultivo de soya", "Elaboracion de alimentos"]


def test_entrada_vacia_devuelve_las_cinco_tablas_vacias():
    salida = ScianTransform().action(_hoja([]))

    assert set(salida) == {"df_sectores", "df_subsectores", "df_ramas", "df_subramas", "df_clases"}
    assert all(df.empty for df in salida.values())
