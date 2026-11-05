"""CodeTransform lleva cada conjunto a su propio transform y los mantiene independientes."""

import pandas as pd
import pytest

from core.pipelines.code.stages.transform import CodeTransform
from core.utils.files import write_json_atomic
from tests.pipelines.code.code_factories import ACADEMIA_ROW, CAT_DEPORTE, CAT_TIPO, POLI_ROW, gdf_from_rows

MANIFEST = {"envio_id": 28, "actualizado_en": "2026-10-22 22:27:17+00:00"}


@pytest.fixture
def stage(tmp_path) -> CodeTransform:
    stage = CodeTransform()
    stage.work_dir = tmp_path / "transform"
    stage.work_dir.mkdir()
    return stage


def _frames():
    return {
        "academias": {
            "frames": {"datos": gdf_from_rows([ACADEMIA_ROW]), "cat_deporte": CAT_DEPORTE, "cat_tipo": CAT_TIPO},
            "manifest": MANIFEST,
        },
        "polideportivos": {
            "frames": {"datos": gdf_from_rows([POLI_ROW]), "cat_deporte": CAT_DEPORTE},
            "manifest": MANIFEST,
        },
    }


def test_la_accion_transforma_cada_conjunto_que_recibe(stage):
    out = stage.action(_frames())

    assert set(out) == {"academias", "polideportivos"}
    assert set(out["academias"]["frames"]) == {"academias"}
    assert set(out["polideportivos"]["frames"]) == {"polideportivos", "polideportivo_deportes"}
    assert set(out["polideportivos"]["catalogs"]) == {"deportes"}


def test_la_accion_sin_datos_no_devuelve_nada(stage):
    assert stage.action({}) == {}


def test_un_conjunto_que_falla_no_se_traga_el_error(stage):
    data = _frames()
    data["academias"]["frames"]["cat_deporte"] = CAT_DEPORTE.iloc[:1]

    with pytest.raises(ValueError, match="sports catalog"):
        stage.action(data)


def test_la_finalizacion_escribe_frames_y_catalogos_por_conjunto(stage):
    stage.finalization(stage.action(_frames()))

    assert (stage.work_dir / "academias" / "academias.pkl").exists()
    assert (stage.work_dir / "academias" / "catalogs.pkl").exists()
    assert (stage.work_dir / "polideportivos" / "polideportivo_deportes.pkl").exists()


def test_el_source_lee_lo_que_dejo_el_extract_de_cada_conjunto(stage, tmp_path, monkeypatch):
    extract = tmp_path / "data" / "extract" / "code"
    (extract / "academias").mkdir(parents=True)
    pd.DataFrame({"a": [1]}).to_pickle(extract / "academias" / "datos.pkl")
    write_json_atomic({"academias": MANIFEST, "polideportivos": MANIFEST}, extract / "manifest.json")
    monkeypatch.chdir(tmp_path)

    out = stage.source()

    assert set(out) == {"academias"}
    assert set(out["academias"]["frames"]) == {"datos"}
    assert out["academias"]["manifest"] == MANIFEST


def test_el_source_sin_manifiesto_no_tiene_nada_que_hacer(stage, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    assert stage.source() == {}
