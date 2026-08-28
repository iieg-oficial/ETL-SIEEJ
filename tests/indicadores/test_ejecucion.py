"""Ejecución real de cada indicador contra su base. Requiere el .env del pipeline."""

from pathlib import Path

import pytest

from core.config import env_path
from core.indicadores import registro

pytestmark = pytest.mark.integration

INDICADORES = list(registro._catalogo().values())

# Sin filtros, la serie completa de estos indicadores rebasa LIMITE y ejecutar() falla.
ACOTAR = {"incidencia_delictiva_municipal": {"cve_geo": "14039"}}
ACOTAR.update(
    {
        "superficie_grupo_edafologico_municipal": {"fuente_limite": "iieg"},
        "porcentaje_grupo_edafologico_municipal": {"fuente_limite": "iieg"},
    }
)


@pytest.fixture(params=INDICADORES, ids=lambda i: i.id)
def filas(request):
    ind = request.param
    if not Path(env_path(ind.pipeline)).exists():
        pytest.skip(f"sin .env para el pipeline '{ind.pipeline}'")
    return registro.ejecutar(ind.id, **ACOTAR.get(ind.id, {}))


def test_devuelve_datos(filas):
    assert filas, "la consulta no devolvió filas"


def test_columnas_exactas(filas):
    assert list(filas[0]) == list(registro.COLUMNAS)


def test_cve_geo_bien_formada(filas):
    for fila in filas:
        assert fila["cve_geo"] is not None
        assert len(fila["cve_geo"]) in (2, 5), fila["cve_geo"]


def test_respeta_el_limite(filas):
    assert len(filas) <= registro.LIMITE


def test_filtro_por_municipio():
    """El bind opcional filtra de verdad, no se ignora."""
    if not Path(env_path("pobreza_multidimensional")).exists():
        pytest.skip("sin .env para el pipeline 'pobreza_multidimensional'")
    filas = registro.ejecutar("pobreza_municipal", cve_geo="14039")
    assert filas
    assert {f["cve_geo"] for f in filas} == {"14039"}


@pytest.mark.parametrize(
    "indicator_id",
    ("superficie_grupo_edafologico_municipal", "porcentaje_grupo_edafologico_municipal"),
)
@pytest.mark.parametrize("fuente_limite", ("iieg", "inegi"))
def test_edafologia_keeps_boundary_sources_separate(indicator_id, fuente_limite):
    if not Path(env_path("edafologia")).exists():
        pytest.skip("sin .env para el pipeline 'edafologia'")

    filas = registro.ejecutar(
        indicator_id,
        cve_geo="14001",
        fuente_limite=fuente_limite,
    )

    assert filas
    assert {fila["cve_geo"] for fila in filas} == {"14001"}
    assert {fila["periodo"] for fila in filas} == {"2021"}
    keys = [(fila["cve_geo"], fila["periodo"], fila["categoria"]) for fila in filas]
    assert len(keys) == len(set(keys))
