import io

import pandas as pd
import pytest

from core.pipelines.nacimientos_dgis.attributes import NacimientosDgisTables as T
from core.pipelines.nacimientos_dgis.helpers.catalogs import (
    catalog_records,
    find_header_row,
    read_catalog,
)
from core.pipelines.nacimientos_dgis.stages.extract import NacimientosDgisExtract


def _sheet(rows: list[list]) -> io.BytesIO:
    """XLSX en memoria con la forma exacta que publica SINAC."""
    buffer = io.BytesIO()
    pd.DataFrame(rows).to_excel(buffer, index=False, header=False)
    buffer.seek(0)
    return buffer


def test_encabezado_no_esta_en_la_primera_fila():
    """Los XLSX chicos traen filas en blanco y el nombre del catálogo antes."""
    raw = pd.DataFrame([[None, None], [None, None], ["SEXO", None], ["Clave", "Descripción"], ["1", "HOMBRE"]])
    assert find_header_row(raw) == 3


def test_sin_columna_de_clave_falla_fuerte():
    raw = pd.DataFrame([["Otra", "Cosa"], ["1", "x"]])
    with pytest.raises(KeyError):
        find_header_row(raw)


def test_catalogo_simple():
    sheet = _sheet([[None, None], ["SEXO", None], ["Clave", "Descripción"], ["0", "NO ESPECIFICADO"], ["1", "HOMBRE"]])
    records = catalog_records(read_catalog(sheet), T.CAT_SEXO)

    assert records == [
        {"clave": 0, "descripcion": "No especificado"},
        {"clave": 1, "descripcion": "Hombre"},
    ]


def test_municipio_compone_la_clave_con_su_entidad():
    """`001` de Aguascalientes y `001` de Jalisco no son el mismo municipio."""
    sheet = _sheet(
        [
            ["MUNICIPIOS", None, None, None],
            ["EFE_KEY", "CATALOG_KEY", "MUNICIPIO", "CVEGEO"],
            ["01", "001", "AGUASCALIENTES", "01001"],
            ["14", "039", "GUADALAJARA", "14039"],
        ]
    )
    records = catalog_records(read_catalog(sheet), T.CAT_MUNICIPIO)

    assert {r["clave"] for r in records} == {1001, 14039}


def test_localidad_compone_las_tres_claves():
    sheet = _sheet(
        [
            ["LOCALIDADES", None, None, None, None],
            ["EFE_KEY", "MUN_KEY", "CATALOG_KEY", "LOCALIDAD", "CVEGEO"],
            ["14", "039", "0001", "GUADALAJARA", "140390001"],
        ]
    )
    records = catalog_records(read_catalog(sheet), T.CAT_LOCALIDAD)

    assert records == [{"clave": 140390001, "descripcion": "Guadalajara"}]


def test_localidad_edicion_2020_2023():
    """El paquete 2020-2023 publica CVE_ENT/CVE_MUN/CVE_LOC/NOM_LOC.

    El de 2024 usa EFE_KEY/MUN_KEY/CATALOG_KEY/LOCALIDAD para lo mismo. Si el
    parser se amarra a un juego de nombres, el otro paquete ni encuentra el
    encabezado.
    """
    sheet = _sheet(
        [
            ["CVE_ENT", "CVE_MUN", "CVE_LOC", "NOM_LOC", "Estatus"],
            ["14", "039", "0001", "GUADALAJARA", None],
        ]
    )
    records = catalog_records(read_catalog(sheet), T.CAT_LOCALIDAD)

    assert records == [{"clave": 140390001, "descripcion": "Guadalajara"}]


def test_municipio_edicion_2020_2023():
    """Mismas columnas que 2024 pero en otro orden: se resuelve por nombre."""
    sheet = _sheet(
        [
            ["CATALOG_KEY", "MUNICIPIO", "EFE_KEY", "ESTATUS"],
            ["039", "GUADALAJARA", "14", "VIGENTE"],
        ]
    )
    records = catalog_records(read_catalog(sheet), T.CAT_MUNICIPIO)

    assert records == [{"clave": 14039, "descripcion": "Guadalajara"}]


def test_clues_conserva_la_clave_alfanumerica():
    sheet = _sheet(
        [
            ["CLUES", "MUNICIPIO", "NOMBRE DE LA UNIDAD"],
            ["JCIMS000366", "GUADALAJARA", "HGR 45 GUADALAJARA"],
        ]
    )
    records = catalog_records(read_catalog(sheet), T.CAT_ESTABLECIMIENTO_SALUD)

    # El catálogo trae MUNICIPIO y LOCALIDAD además del nombre de la unidad:
    # la descripción tiene que ser la unidad, no el municipio.
    assert records == [{"clave": "JCIMS000366", "descripcion": "HGR 45 Guadalajara"}]


def test_si_no_no_es_un_dominio_binario():
    """Cinco valores, no dos: por eso es catálogo y no boolean."""
    sheet = _sheet(
        [
            [None, None],
            ["SI_NO", None],
            ["Clave", "Descripción"],
            ["0", "NO ESPECIFICADO"],
            ["1", "SI"],
            ["2", "NO"],
            ["8", "NO APLICA"],
            ["9", "SE IGNORA"],
        ]
    )
    records = catalog_records(read_catalog(sheet), T.CAT_SI_NO)

    assert [r["clave"] for r in records] == [0, 1, 2, 8, 9]
    assert {r["descripcion"] for r in records} >= {"No aplica", "Se ignora"}


def test_claves_duplicadas_se_quedan_con_la_primera():
    sheet = _sheet([["Clave", "Descripción"], ["1", "HOMBRE"], ["1", "HOMBRE (BIS)"]])
    records = catalog_records(read_catalog(sheet), T.CAT_SEXO)

    assert records == [{"clave": 1, "descripcion": "Hombre"}]


@pytest.mark.parametrize(
    ("year", "package"),
    [
        (2020, "sinac_catalogos_2020_2023.zip"),
        (2023, "sinac_catalogos_2020_2023.zip"),
        (2024, "sinac_catalogos_2024.zip"),
        (2025, "sinac_catalogos_2025.zip"),
        (2026, "sinac_catalogos_2025.zip"),
    ],
)
def test_cada_edicion_usa_su_paquete_de_catalogos(year, package):
    """DGIS publica los catálogos por rango, no uno por año."""
    assert NacimientosDgisExtract.catalog_package(year) == package


@pytest.mark.parametrize(
    ("crudo", "esperado"),
    [
        ("NO REMUNERADO, AMA DE CASA", "No remunerado, ama de casa"),
        ("BACHILLERATO O PREPARATORIA INCOMPLETA", "Bachillerato o preparatoria incompleta"),
        ("SEGURO POPULAR / INSABI", "Seguro popular / INSABI"),
        ("IMSS", "IMSS"),
        ("ISSSTE", "ISSSTE"),
    ],
)
def test_descripcion_en_caja_de_oracion(crudo, esperado):
    """SINAC publica en MAYÚSCULAS; las siglas sobreviven al cambio de caja."""
    sheet = _sheet([["Clave", "Descripción"], ["1", crudo]])
    records = catalog_records(read_catalog(sheet), T.CAT_AFILIACION)

    assert records[0]["descripcion"] == esperado


@pytest.mark.parametrize(
    ("crudo", "esperado"),
    [
        ("SAN JUAN DE LOS LAGOS", "San Juan de los Lagos"),
        ("BENITO JUAREZ", "Benito Juárez"),
        ("TLAHUAC", "Tláhuac"),
    ],
)
def test_nombre_propio_en_title_con_acentos(crudo, esperado):
    """Nombres propios en `title()`, con conectores abajo y acentos restituidos."""
    sheet = _sheet([["EFE_KEY", "CATALOG_KEY", "MUNICIPIO"], ["14", "039", crudo]])
    records = catalog_records(read_catalog(sheet), T.CAT_MUNICIPIO)

    assert records[0]["descripcion"] == esperado


def test_inicial_pegada_a_punto_no_es_conector():
    """La "A" de "A.C." no es la preposición: va seguida de punto, no de espacio."""
    sheet = _sheet([["CLUES", "NOMBRE DE LA UNIDAD"], ["JCIMS000366", "FUNDACION BEST A.C."]])
    records = catalog_records(read_catalog(sheet), T.CAT_ESTABLECIMIENTO_SALUD)

    assert records[0]["descripcion"] == "Fundación Best A.C."


def test_sigla_sin_vocales_se_conserva():
    """La cola larga de siglas (HGZ, CSS, CMF) no cabe en una lista enumerada."""
    sheet = _sheet([["CLUES", "NOMBRE DE LA UNIDAD"], ["JCIMS000366", "HGZ 2 AGUASCALIENTES"]])
    records = catalog_records(read_catalog(sheet), T.CAT_ESTABLECIMIENTO_SALUD)

    assert records[0]["descripcion"] == "HGZ 2 Aguascalientes"
