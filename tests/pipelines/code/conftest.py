import logging
import zipfile
from pathlib import Path

import pytest

from core.pipelines.code.stages import load as load_module
from core.pipelines.code.stages.load import CodeLoad

from tests.pipelines.code.code_factories import (
    ACADEMIA_ROW,
    DEPORTE_CSV,
    POLI_ROW,
    TIPO_CSV,
    FakeDb,
    write_gpkg,
)


@pytest.fixture
def captured(monkeypatch) -> dict:
    calls: dict = {"inserts": [], "upserts": [], "bulk": []}

    monkeypatch.setattr(load_module, "get_mapping", lambda *a, **k: {"Altos Sur": 5, "Norte": 9})
    monkeypatch.setattr(load_module, "sync_id_sequence", lambda session, model: None)
    monkeypatch.setattr(load_module, "count_records", lambda session, model: 0)
    monkeypatch.setattr(
        load_module,
        "insert_records",
        lambda session, data, model, conflict_keys: calls["inserts"].append((model, data, conflict_keys)),
    )
    monkeypatch.setattr(
        load_module,
        "upsert_records",
        lambda session, data, model, conflict_keys, **k: calls["upserts"].append((model, data, conflict_keys)),
    )
    monkeypatch.setattr(
        load_module,
        "bulk_insert",
        lambda session, data, model: calls["bulk"].append((model, data)),
    )
    return calls


@pytest.fixture
def load() -> CodeLoad:
    stage = object.__new__(CodeLoad)
    stage.logger = logging.getLogger("test.code.load")
    stage.db = FakeDb()
    stage.mode = "bootstrap"
    return stage


@pytest.fixture
def academias_zip(tmp_path) -> Path:
    """Nombres de archivo y de capa raros a proposito: cambian entre cargas."""
    folder = tmp_path / "src_academias"
    folder.mkdir()
    write_gpkg(folder / "academias_deportivasnoviembre.gpkg", [ACADEMIA_ROW], layer="academiasnoviembre")
    (folder / "catalogo_a.csv").write_text(DEPORTE_CSV, encoding="utf-8")
    (folder / "catalogo_b.csv").write_text(TIPO_CSV, encoding="utf-8")
    archive = tmp_path / "academias.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        for item in folder.iterdir():
            zf.write(item, f"zip_x/{item.name}")
    return archive


@pytest.fixture
def polideportivos_zip(tmp_path) -> Path:
    folder = tmp_path / "src_poli"
    folder.mkdir()
    write_gpkg(folder / "polis_v2.gpkg", [POLI_ROW], layer="polideportivos")
    (folder / "code_catalogodeporte.csv").write_text(DEPORTE_CSV, encoding="utf-8")
    archive = tmp_path / "poli.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        for item in folder.iterdir():
            zf.write(item, item.name)
    return archive
