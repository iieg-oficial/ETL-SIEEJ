"""El descubrimiento va por el campo de metodologia, donde CODE subio sus datos."""

import pandas as pd
import pytest

from core.acervo.client import Upload
from core.pipelines.code.constants import UPLOAD_FIELD
from core.pipelines.code.stages import extract as extract_module
from core.pipelines.code.stages.extract import CodeExtract


def _upload(
    updated_at: str = "2026-09-09 17:16:53+00:00", etag: str = "abc123", uploaded_at: str = "2026-09-09 17:15:51+00:00"
) -> Upload:
    return Upload(
        object_key="k",
        filename="zip_reto.zip",
        size=1,
        uploaded_at=uploaded_at,
        envio="persona",
        envio_id=28,
        conjunto="Puntos de activación del programa Reto",
        updated_at=updated_at,
        field_path=f"conunto_datos[0].{UPLOAD_FIELD}",
        fecha_corte="",
        fecha_actualizacion="",
        etag=etag,
    )


@pytest.fixture
def listado(monkeypatch) -> dict:
    """Reemplaza list_uploads para registrar con que argumentos se llama."""
    state: dict = {"uploads": [], "calls": []}

    def fake(dependencia, **kwargs):
        state["calls"].append((dependencia, kwargs))
        return state["uploads"]

    monkeypatch.setattr(extract_module, "list_uploads", fake)
    return state


def test_el_campo_de_metodologia_se_pide_al_cliente(listado):
    listado["uploads"] = [_upload()]

    CodeExtract().source()

    _, kwargs = listado["calls"][0]
    assert kwargs["field"] == UPLOAD_FIELD


def test_el_campo_es_el_de_metodologia():
    assert UPLOAD_FIELD == "adjunte_el_documento_metodologico_asociado_al_conjunto_de_datos"


def test_con_varios_envios_se_toma_el_mas_reciente(listado):
    viejo = _upload(uploaded_at="2026-08-01 10:00:00+00:00", etag="viejo")
    nuevo = _upload(uploaded_at="2026-09-09 17:15:51+00:00", etag="nuevo")
    listado["uploads"] = [nuevo, viejo]

    assert CodeExtract().source().etag == "nuevo"


def test_un_bootstrap_sin_envios_es_un_error(listado):
    with pytest.raises(ValueError, match="No uploads"):
        CodeExtract(mode="bootstrap").source()


def test_un_update_sin_nada_nuevo_no_es_un_error(listado):
    listado["uploads"] = [_upload()]

    assert CodeExtract(mode="update", since="2026-09-30 00:00:00+00:00").source() is None


def test_en_update_se_descarta_lo_anterior_al_watermark():
    extract = CodeExtract(mode="update", since="2026-09-30 00:00:00+00:00")

    assert extract._is_new(_upload()) is False


def test_en_update_se_toma_lo_posterior_al_watermark():
    extract = CodeExtract(mode="update", since="2026-08-01 00:00:00+00:00")

    assert extract._is_new(_upload()) is True


def test_en_update_se_salta_un_envio_cuyo_archivo_no_cambio():
    extract = CodeExtract(mode="update", processed_etags=["abc123"])

    assert extract._is_new(_upload(etag="abc123")) is False


def test_un_etag_nuevo_si_se_procesa():
    extract = CodeExtract(mode="update", processed_etags=["otro"])

    assert extract._is_new(_upload(etag="abc123")) is True


def test_sin_watermark_ni_etags_todo_es_nuevo():
    assert CodeExtract(mode="update")._is_new(_upload()) is True


def test_la_accion_sin_envio_no_descarga_nada(listado):
    salida = CodeExtract(mode="update").action(None)

    assert salida == {"frames": {}, "upload": None}


def test_el_manifiesto_no_lleva_las_fechas_vacias_del_formulario(tmp_path, monkeypatch):
    # CODE no captura fecha de corte: el corte sale de los datos.
    extract = CodeExtract()
    extract.work_dir = tmp_path

    extract.finalization({"frames": {"base": pd.DataFrame({"a": [1]})}, "upload": _upload()})

    manifiesto = pd.read_json(tmp_path / "manifest.json", typ="series")
    assert manifiesto["envio_id"] == 28
    assert "fecha_corte" not in manifiesto
    assert str(manifiesto["actualizado_en"]).startswith("2026-09-09")


def test_la_accion_lee_la_hoja_de_datos_y_la_del_catalogo(tmp_path, monkeypatch):
    import zipfile

    xlsx = tmp_path / "datos.xlsx"
    with pd.ExcelWriter(xlsx) as writer:
        pd.DataFrame({"id": [1]}).to_excel(writer, sheet_name="base", index=False)
        pd.DataFrame({"actividad": ["Baile"], "id": [1]}).to_excel(writer, sheet_name="cat_actividad", index=False)
    archivo = tmp_path / "zip_reto.zip"
    with zipfile.ZipFile(archivo, "w") as zf:
        zf.write(xlsx, "code_catalogo_actividad_reto.xlsx")
        zf.writestr("reto.gpkg", b"ignorado")

    monkeypatch.setattr(extract_module, "download", lambda upload, folder: archivo)
    extract = CodeExtract()
    extract.work_dir = tmp_path / "work"

    salida = extract.action(_upload())

    assert set(salida["frames"]) == {"base", "cat_actividad"}
    assert salida["frames"]["cat_actividad"]["actividad"].tolist() == ["Baile"]


def test_un_zip_sin_hoja_de_calculo_falla(tmp_path, monkeypatch):
    import zipfile

    archivo = tmp_path / "zip_reto.zip"
    with zipfile.ZipFile(archivo, "w") as zf:
        zf.writestr("reto.gpkg", b"ignorado")
    monkeypatch.setattr(extract_module, "download", lambda upload, folder: archivo)
    extract = CodeExtract()
    extract.work_dir = tmp_path / "work"

    with pytest.raises(FileNotFoundError, match="xlsx"):
        extract.action(_upload())


def test_el_watermark_se_compara_como_fecha_con_zona_horaria():
    # Como texto "2026-09-09 17:16:53+00:00" < "2026-09-09 12:00:00-06:00", aunque es la misma hora.
    extract = CodeExtract(mode="update", since="2026-09-09 12:00:00-06:00")

    assert extract._is_new(_upload(updated_at="2026-09-09 18:16:53+00:00")) is True
    assert extract._is_new(_upload(updated_at="2026-09-09 17:59:00+00:00")) is False


def test_el_watermark_acepta_formatos_distintos_del_mismo_instante():
    extract = CodeExtract(mode="update", since="2026-09-09T17:16:53.235786+00:00")

    assert extract._is_new(_upload(updated_at="2026-09-09 17:16:53.235786+00:00")) is False


def test_un_envio_sin_actualizado_en_falla_antes_de_cargar(listado):
    listado["uploads"] = [_upload(updated_at="")]

    with pytest.raises(ValueError, match="actualizado_en"):
        CodeExtract().source()
