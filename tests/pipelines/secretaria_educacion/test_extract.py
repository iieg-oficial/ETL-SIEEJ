"""El nombre del conjunto lo captura una persona, así que el ruteo va por prefijo."""

import pytest

from core.acervo.client import Upload
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


def _upload(updated_at: str = "2026-09-10 21:43:10+00:00", etag: str = "abc123") -> Upload:
    return Upload(
        object_key="k",
        filename="f.csv",
        size=1,
        uploaded_at="2026-09-10 21:42:01+00:00",
        envio="persona",
        envio_id=27,
        conjunto="Aulas google",
        updated_at=updated_at,
        field_path="conunto_datos[0].carga_de_datos",
        fecha_corte="2026-09-10",
        fecha_actualizacion="2026-09-01",
        etag=etag,
    )


def test_en_update_se_descarta_lo_anterior_al_watermark():
    extract = SecretariaEducacionExtract(mode="update", since="2026-09-30 00:00:00+00:00")

    assert extract._is_new(_upload()) is False


def test_en_update_se_toma_lo_posterior_al_watermark():
    extract = SecretariaEducacionExtract(mode="update", since="2026-08-01 00:00:00+00:00")

    assert extract._is_new(_upload()) is True


def test_en_update_se_salta_un_envio_cuyo_archivo_no_cambio():
    # Reenviar corrigiendo un metadato no debe recargar los datos.
    extract = SecretariaEducacionExtract(mode="update", since=None, processed_etags=["abc123"])

    assert extract._is_new(_upload(etag="abc123")) is False


def test_un_etag_nuevo_si_se_procesa():
    extract = SecretariaEducacionExtract(mode="update", since=None, processed_etags=["otro"])

    assert extract._is_new(_upload(etag="abc123")) is True


def test_sin_watermark_ni_etags_todo_es_nuevo():
    assert SecretariaEducacionExtract(mode="update")._is_new(_upload()) is True
