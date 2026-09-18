"""El nombre del conjunto lo captura una persona, así que el ruteo va por prefijo."""

import pytest

from core.pipelines.secretaria_educacion.constants import (
    AULAS_GOOGLE_DATASET,
    DIRECTORIO_DATASET,
    PROGRAMAS_DATASET,
)
from core.pipelines.secretaria_educacion.stages.extract import SecretariaEducacionExtract


@pytest.fixture
def extract() -> SecretariaEducacionExtract:
    return SecretariaEducacionExtract()


@pytest.mark.parametrize(
    ("conjunto", "esperado"),
    [
        ("DIRECTORIO CATÁLOGO CENTROS DE TRABAJO", DIRECTORIO_DATASET),
        ("Escuelas beneficiadas por Programas Estratégicos ciclo escolar 2025-2026", PROGRAMAS_DATASET),
        ("Aulas google", AULAS_GOOGLE_DATASET),
    ],
)
def test_el_conjunto_se_rutea_a_su_dataset(extract, conjunto, esperado):
    assert extract._resolve_dataset(conjunto) == esperado


def test_el_ruteo_ignora_acentos_y_mayusculas(extract):
    assert extract._resolve_dataset("aulas GOOGLE") == AULAS_GOOGLE_DATASET


def test_el_ruteo_tolera_que_el_ciclo_escolar_cambie(extract):
    # El sufijo del ciclo cambia cada año y no debe romper el ruteo.
    assert extract._resolve_dataset("Aulas google 2026-2027") == AULAS_GOOGLE_DATASET
    assert (
        extract._resolve_dataset("Escuelas beneficiadas por Programas Estratégicos ciclo escolar 2026-2027")
        == PROGRAMAS_DATASET
    )


def test_un_conjunto_desconocido_no_se_rutea(extract):
    # Se omite con warning en vez de romper: la dependencia sube datasets nuevos.
    assert extract._resolve_dataset("Padrón de becas 2026") is None
