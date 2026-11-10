"""El extract toma la carga mas reciente de cada conjunto, nunca la mas reciente global."""

from unittest.mock import Mock

import pytest

from core.pipelines.code.constants import UPLOAD_FIELD
from core.pipelines.code.stages import extract as extract_module
from core.pipelines.code.stages.extract import CodeExtract

from tests.pipelines.code.code_factories import ACADEMIAS_NAME, DATA_FIELD, POLIDEPORTIVOS_NAME, RETO_NAME, make_upload


@pytest.fixture
def listing(monkeypatch) -> dict:
    """list_uploads falso: responde por campo pedido, como el cliente real."""
    state: dict = {"uploads": [], "fields": []}

    def fake(dependencia, **kwargs):
        state["fields"].append(kwargs["field"])
        return [u for u in state["uploads"] if kwargs["field"] in u.field_path]

    monkeypatch.setattr(extract_module, "list_uploads", fake)
    return state


def test_la_carga_mas_reciente_global_no_se_apropia_de_otro_conjunto(listing):
    reto = make_upload(0, RETO_NAME, UPLOAD_FIELD, uploaded_at="2026-10-22 10:00:00+00:00", etag="reto")
    poli = make_upload(2, POLIDEPORTIVOS_NAME, DATA_FIELD, uploaded_at="2026-10-22 22:27:00+00:00", etag="poli")
    listing["uploads"] = [reto, poli]

    selected = CodeExtract(mode="update").source()

    assert selected["reto"].etag == "reto"
    assert selected["polideportivos"].etag == "poli"


def test_cada_conjunto_toma_su_propia_carga_mas_reciente(listing):
    listing["uploads"] = [
        make_upload(1, ACADEMIAS_NAME, DATA_FIELD, uploaded_at="2026-10-14 22:00:00+00:00", etag="old"),
        make_upload(1, ACADEMIAS_NAME, DATA_FIELD, uploaded_at="2026-10-22 22:00:00+00:00", etag="new"),
        make_upload(0, RETO_NAME, UPLOAD_FIELD, uploaded_at="2026-10-27 22:00:00+00:00", etag="reto"),
    ]

    selected = CodeExtract(mode="update").source()

    assert selected["academias"].etag == "new"
    assert selected["reto"].etag == "reto"


def test_el_conjunto_se_asigna_por_nombre_y_no_por_posicion(listing):
    listing["uploads"] = [make_upload(2, ACADEMIAS_NAME, DATA_FIELD, etag="shifted")]

    assert set(CodeExtract(mode="update").source()) == {"academias"}


def test_reto_lee_el_campo_de_metodologia_y_los_otros_el_de_datos(listing):
    listing["uploads"] = [
        make_upload(0, RETO_NAME, DATA_FIELD, etag="reto-data"),
        make_upload(0, RETO_NAME, UPLOAD_FIELD, etag="reto-meth"),
        make_upload(1, ACADEMIAS_NAME, UPLOAD_FIELD, etag="aca-meth"),
        make_upload(1, ACADEMIAS_NAME, DATA_FIELD, etag="aca-data"),
    ]

    selected = CodeExtract(mode="update").source()

    assert selected["reto"].etag == "reto-meth"
    assert selected["academias"].etag == "aca-data"
    assert set(listing["fields"]) == {UPLOAD_FIELD, DATA_FIELD}


def test_los_conjuntos_desconocidos_se_ignoran(listing):
    listing["uploads"] = [make_upload(3, "Otro conjunto", DATA_FIELD), make_upload(0)]

    assert set(CodeExtract(mode="update").source()) == {"reto"}


def test_el_bootstrap_sin_ningun_conjunto_conocido_falla(listing):
    with pytest.raises(ValueError, match="No uploads"):
        CodeExtract(mode="bootstrap").source()


def test_el_update_sin_novedades_no_devuelve_nada(listing):
    listing["uploads"] = [make_upload()]
    since = {"reto": "2026-09-30 00:00:00+00:00"}

    assert CodeExtract(mode="update", since=since).source() == {}


def test_el_watermark_se_aplica_por_conjunto(listing):
    """Un conjunto sin carga previa no debe saltarse por el watermark de otro."""
    same_envio = "2026-10-27 17:42:03+00:00"
    listing["uploads"] = [
        make_upload(0, RETO_NAME, UPLOAD_FIELD, updated_at=same_envio, etag="r"),
        make_upload(1, ACADEMIAS_NAME, DATA_FIELD, updated_at=same_envio, etag="a"),
    ]

    selected = CodeExtract(mode="update", since={"reto": same_envio}).source()

    assert set(selected) == {"academias"}


def test_el_update_salta_un_etag_ya_cargado(listing):
    listing["uploads"] = [make_upload(1, ACADEMIAS_NAME, DATA_FIELD, etag="same")]

    assert CodeExtract(mode="update", processed_etags=["same"]).source() == {}


def test_una_carga_sin_actualizado_en_falla_antes_de_cargar(listing):
    listing["uploads"] = [make_upload(updated_at="")]

    with pytest.raises(ValueError, match="actualizado_en"):
        CodeExtract(mode="update").source()


def test_un_nombre_con_sufijo_no_se_asigna_a_un_conjunto_conocido(listing):
    listing["uploads"] = [make_upload(1, "Academias deportivas borrador", DATA_FIELD), make_upload(0)]

    assert set(CodeExtract(mode="update").source()) == {"reto"}


def test_el_nombre_se_compara_exacto_sin_acentos_ni_mayusculas(listing):
    listing["uploads"] = [make_upload(1, "ACADEMIAS DEPORTIVAS,  espacios para la paz", DATA_FIELD)]

    assert set(CodeExtract(mode="update").source()) == {"academias"}


def test_un_nombre_desconocido_se_avisa(listing):
    listing["uploads"] = [make_upload(3, "Otro conjunto", DATA_FIELD), make_upload(0)]
    extract = CodeExtract(mode="update")
    extract.logger = Mock()

    extract.source()

    avisos = [call.args[0] for call in extract.logger.warning.call_args_list]
    assert any("Otro conjunto" in aviso for aviso in avisos)


def test_un_conjunto_conocido_sin_carga_se_avisa(listing):
    listing["uploads"] = [make_upload(0)]
    extract = CodeExtract(mode="update")
    extract.logger = Mock()

    extract.source()

    avisos = [call.args[0] for call in extract.logger.warning.call_args_list]
    assert any("academias" in aviso for aviso in avisos) and any("polideportivos" in aviso for aviso in avisos)


def test_el_bootstrap_falla_si_falta_algun_conjunto_conocido(listing):
    listing["uploads"] = [make_upload(0), make_upload(1, ACADEMIAS_NAME, DATA_FIELD)]

    with pytest.raises(ValueError, match="polideportivos"):
        CodeExtract(mode="bootstrap").source()


def test_el_bootstrap_con_los_tres_conjuntos_los_devuelve(listing):
    listing["uploads"] = [
        make_upload(0),
        make_upload(1, ACADEMIAS_NAME, DATA_FIELD),
        make_upload(2, POLIDEPORTIVOS_NAME, DATA_FIELD),
    ]

    assert set(CodeExtract(mode="bootstrap").source()) == {"reto", "academias", "polideportivos"}
