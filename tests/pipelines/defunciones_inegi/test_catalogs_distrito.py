"""Los distritos de Oaxaca viajan dentro del catálogo de localidades."""

import pandas as pd
import pytest

from core.pipelines.defunciones_inegi.helpers.catalogs import distrito_oaxaca_records, localidad_records


@pytest.fixture
def catalogo() -> pd.DataFrame:
    """Muestra con la forma real de `entidad_municipio_localidad`."""
    return pd.DataFrame(
        [
            {"cve_ent": "20", "cve_mun": "901", "cve_loc": "0000", "nom_loc": "Silacayápam"},
            {"cve_ent": "20", "cve_mun": "927", "cve_loc": "0000", "nom_loc": "Yautepec"},
            {"cve_ent": "20", "cve_mun": "999", "cve_loc": "0000", "nom_loc": "Municipio no especificado"},
            {"cve_ent": "20", "cve_mun": "067", "cve_loc": "0001", "nom_loc": "Oaxaca de Juárez"},
            {"cve_ent": "14", "cve_mun": "039", "cve_loc": "0001", "nom_loc": "Guadalajara"},
        ]
    )


def test_solo_toma_los_distritos(catalogo):
    records = distrito_oaxaca_records(catalogo)

    assert records == [
        {"clave": 901, "descripcion": "Silacayápam"},
        {"clave": 927, "descripcion": "Yautepec"},
    ]


def test_el_centinela_999_no_es_un_distrito(catalogo):
    claves = [record["clave"] for record in distrito_oaxaca_records(catalogo)]

    assert 999 not in claves


def test_las_localidades_no_se_contaminan_con_distritos(catalogo):
    """`cve_loc` en cero es la marca de que la fila no es una localidad."""
    localidades = localidad_records(catalogo)

    assert [record["localidad"] for record in localidades] == ["Oaxaca de Juárez", "Guadalajara"]


def test_una_edicion_sin_oaxaca_no_produce_catalogo():
    solo_jalisco = pd.DataFrame([{"cve_ent": "14", "cve_mun": "039", "cve_loc": "0001", "nom_loc": "Guadalajara"}])

    assert distrito_oaxaca_records(solo_jalisco) == []
