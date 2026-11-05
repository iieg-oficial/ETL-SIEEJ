"""El descubrimiento va por el campo de metodologia, donde CODE subio sus datos."""

import pandas as pd

from core.acervo.client import Upload
from core.pipelines.code.constants import UPLOAD_FIELD
from core.pipelines.code.stages.extract import CodeExtract
from tests.pipelines.code.code_factories import ACADEMIAS_NAME, make_upload


def _upload(updated_at: str = "2026-09-09 17:16:53+00:00", etag: str = "abc123") -> Upload:
    return make_upload(updated_at=updated_at, etag=etag)


def test_el_campo_es_el_de_metodologia():
    assert UPLOAD_FIELD == "adjunte_el_documento_metodologico_asociado_al_conjunto_de_datos"


def test_en_update_se_descarta_lo_anterior_al_watermark():
    extract = CodeExtract(mode="update", since={"reto": "2026-09-30 00:00:00+00:00"})

    assert extract._is_new(_upload()) is False


def test_en_update_se_toma_lo_posterior_al_watermark():
    extract = CodeExtract(mode="update", since={"reto": "2026-08-01 00:00:00+00:00"})

    assert extract._is_new(_upload()) is True


def test_en_update_se_salta_un_envio_cuyo_archivo_no_cambio():
    extract = CodeExtract(mode="update", processed_etags=["abc123"])

    assert extract._is_new(_upload(etag="abc123")) is False


def test_un_etag_nuevo_si_se_procesa():
    extract = CodeExtract(mode="update", processed_etags=["otro"])

    assert extract._is_new(_upload(etag="abc123")) is True


def test_sin_watermark_ni_etags_todo_es_nuevo():
    assert CodeExtract(mode="update")._is_new(_upload()) is True


def test_el_watermark_se_compara_como_fecha_con_zona_horaria():
    # Como texto "2026-09-09 17:16:53+00:00" < "2026-09-09 12:00:00-06:00", aunque es la misma hora.
    extract = CodeExtract(mode="update", since={"reto": "2026-09-09 12:00:00-06:00"})

    assert extract._is_new(_upload(updated_at="2026-09-09 18:16:53+00:00")) is True
    assert extract._is_new(_upload(updated_at="2026-09-09 17:59:00+00:00")) is False


def test_el_watermark_acepta_formatos_distintos_del_mismo_instante():
    extract = CodeExtract(mode="update", since={"reto": "2026-09-09T17:16:53.235786+00:00"})

    assert extract._is_new(_upload(updated_at="2026-09-09 17:16:53.235786+00:00")) is False


def test_la_finalizacion_borra_los_pickles_de_una_extraccion_anterior(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    stage = CodeExtract()
    folder = stage.work_dir / "academias"
    folder.mkdir(parents=True)
    pd.DataFrame({"tipo": ["viejo"]}).to_pickle(folder / "cat_tipo.pkl")
    entry = {"frames": {"datos": pd.DataFrame({"a": [1]})}, "upload": make_upload(name=ACADEMIAS_NAME)}

    stage.finalization({"academias": entry})

    assert sorted(path.name for path in folder.glob("*.pkl")) == ["datos.pkl"]
