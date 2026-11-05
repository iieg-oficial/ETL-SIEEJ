"""Los lectores de los zip nunca fijan nombres de archivo."""

import zipfile

import pandas as pd
import pytest

from core.pipelines.code.helpers.sources import read_geo_zip
from core.pipelines.code.stages import extract as extract_module
from core.pipelines.code.stages.extract import CodeExtract

from tests.pipelines.code.code_factories import ACADEMIAS_NAME, DATA_FIELD, make_upload


def test_el_zip_de_academias_trae_los_datos_y_los_dos_catalogos(academias_zip, tmp_path):
    with zipfile.ZipFile(academias_zip) as zf:
        zf.extractall(tmp_path / "out")

    frames = read_geo_zip(tmp_path / "out")

    assert set(frames) == {"datos", "cat_deporte", "cat_tipo"}
    assert len(frames["datos"]) == 1
    assert frames["datos"].crs.to_epsg() == 6368


def test_el_zip_de_polideportivos_no_trae_catalogo_de_tipos(polideportivos_zip, tmp_path):
    with zipfile.ZipFile(polideportivos_zip) as zf:
        zf.extractall(tmp_path / "out")

    assert set(read_geo_zip(tmp_path / "out")) == {"datos", "cat_deporte"}


def test_un_zip_sin_gpkg_falla(tmp_path):
    (tmp_path / "x.csv").write_text("deporte,id\nA,1\n")

    with pytest.raises(FileNotFoundError, match="gpkg"):
        read_geo_zip(tmp_path)


def test_un_gpkg_con_dos_capas_es_ambiguo(tmp_path):
    import geopandas as gpd
    from shapely.geometry import Point

    gdf = gpd.GeoDataFrame({"a": [1]}, geometry=[Point(0, 0)], crs="EPSG:6368")
    gdf.to_file(tmp_path / "x.gpkg", layer="uno", driver="GPKG")
    gdf.to_file(tmp_path / "x.gpkg", layer="dos", driver="GPKG")

    with pytest.raises(ValueError, match="layer"):
        read_geo_zip(tmp_path)


def test_la_accion_lee_cada_conjunto_seleccionado(academias_zip, tmp_path, monkeypatch):
    monkeypatch.setattr(extract_module, "download", lambda upload, folder: academias_zip)
    extract = CodeExtract()
    extract.work_dir = tmp_path / "work"
    upload = make_upload(1, ACADEMIAS_NAME, DATA_FIELD)

    out = extract.action({"academias": upload})

    assert set(out["academias"]["frames"]) == {"datos", "cat_deporte", "cat_tipo"}
    assert out["academias"]["upload"] is upload


def test_la_finalizacion_escribe_un_manifiesto_con_una_entrada_por_conjunto(tmp_path):
    from core.utils.files import read_json

    extract = CodeExtract()
    extract.work_dir = tmp_path
    upload = make_upload(1, ACADEMIAS_NAME, DATA_FIELD)
    import pandas as pd

    extract.finalization({"academias": {"frames": {"datos": pd.DataFrame({"a": [1]})}, "upload": upload}})

    manifest = read_json(tmp_path / "manifest.json")
    assert manifest["academias"]["envio_id"] == 28
    assert manifest["academias"]["conjunto"] == ACADEMIAS_NAME
    assert (tmp_path / "academias" / "datos.pkl").exists()


def _reto_zip(tmp_path, with_xlsx=True):
    archive = tmp_path / "zip_reto.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        if with_xlsx:
            xlsx = tmp_path / "datos.xlsx"
            with pd.ExcelWriter(xlsx) as writer:
                pd.DataFrame({"id": [1]}).to_excel(writer, sheet_name="base", index=False)
                pd.DataFrame({"actividad": ["Baile"], "id": [1]}).to_excel(
                    writer, sheet_name="cat_actividad", index=False
                )
            zf.write(xlsx, "any_name.xlsx")
        zf.writestr("reto.gpkg", b"ignored")
    return archive


def test_la_accion_de_reto_lee_la_hoja_de_datos_y_la_del_catalogo(tmp_path, monkeypatch):
    monkeypatch.setattr(extract_module, "download", lambda upload, folder: _reto_zip(tmp_path))
    extract = CodeExtract()
    extract.work_dir = tmp_path / "work"

    out = extract.action({"reto": make_upload()})

    assert set(out["reto"]["frames"]) == {"base", "cat_actividad"}
    assert out["reto"]["frames"]["cat_actividad"]["actividad"].tolist() == ["Baile"]


def test_un_zip_de_reto_sin_hoja_de_calculo_falla(tmp_path, monkeypatch):
    monkeypatch.setattr(extract_module, "download", lambda upload, folder: _reto_zip(tmp_path, with_xlsx=False))
    extract = CodeExtract()
    extract.work_dir = tmp_path / "work"

    with pytest.raises(FileNotFoundError, match="xlsx"):
        extract.action({"reto": make_upload()})


def test_el_manifiesto_no_lleva_las_fechas_vacias_del_formulario(tmp_path):
    # CODE no captura fecha de corte: el corte sale de los datos.
    from core.utils.files import read_json

    extract = CodeExtract()
    extract.work_dir = tmp_path

    extract.finalization({"reto": {"frames": {"base": pd.DataFrame({"a": [1]})}, "upload": make_upload()}})

    entrada = read_json(tmp_path / "manifest.json")["reto"]
    assert entrada["envio_id"] == 28
    assert "fecha_corte" not in entrada
    assert entrada["actualizado_en"].startswith("2026-09-09")


def test_la_accion_sin_cargas_no_descarga_nada(tmp_path, monkeypatch):
    monkeypatch.setattr(extract_module, "download", lambda *a: pytest.fail("no debe descargar"))
    extract = CodeExtract(mode="update")
    extract.work_dir = tmp_path

    assert extract.action({}) == {}


def test_la_finalizacion_sin_cargas_escribe_un_manifiesto_vacio(tmp_path):
    from core.utils.files import read_json

    extract = CodeExtract(mode="update")
    extract.work_dir = tmp_path

    extract.finalization({})

    assert read_json(tmp_path / "manifest.json") == {}
