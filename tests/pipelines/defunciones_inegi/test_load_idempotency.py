"""Regresión de #378: una corrida sin ediciones nuevas no debe reinsertar hechos."""

from pathlib import Path

import pandas as pd
import pytest

from core.pipelines.defunciones_inegi.constants import CATALOGS_FILE, FACTS_DIR
from core.pipelines.defunciones_inegi.stages import load
from core.pipelines.defunciones_inegi.stages.transform import DefuncionesInegiTransform


@pytest.fixture
def workdir(tmp_path, monkeypatch) -> Path:
    """Los stages usan rutas relativas a `data/`; se aíslan en un directorio temporal."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _write_facts(loader: load.DefuncionesInegiLoad, *years: int) -> None:
    facts_dir = loader.transform_dir / FACTS_DIR
    facts_dir.mkdir(parents=True, exist_ok=True)
    for year in years:
        pd.DataFrame({"x": [1]}).to_pickle(facts_dir / f"{year}.pkl")
    pd.to_pickle({}, loader.transform_dir / CATALOGS_FILE)


class _ForbiddenDatabase:
    """Falla si algún stage intenta tocar la base."""

    def connect(self):
        raise AssertionError("no debe conectarse a la base")

    def get_session(self):
        raise AssertionError("no debe abrir sesión")


def test_source_ignores_stale_facts_when_transform_produced_none(workdir):
    loader = load.DefuncionesInegiLoad(mode="update")
    _write_facts(loader, 2017, 2018)

    assert loader.source({"editions": []}) == {"catalogs": {}, "editions": []}


def test_source_only_takes_editions_from_this_run(workdir):
    loader = load.DefuncionesInegiLoad(mode="update")
    _write_facts(loader, 2017, 2018, 2025)

    assert loader.source({"editions": [2025]})["editions"] == [2025]


def test_source_fails_when_transformed_facts_are_missing(workdir):
    loader = load.DefuncionesInegiLoad(mode="update")
    _write_facts(loader)

    with pytest.raises(FileNotFoundError):
        loader.source({"editions": [2025]})


def test_run_without_editions_does_not_touch_database(workdir, monkeypatch):
    loader = load.DefuncionesInegiLoad(mode="update")
    loader.db = _ForbiddenDatabase()
    monkeypatch.setattr(loader, "_refresh_views", lambda: pytest.fail("no debe refrescar vistas"))
    _write_facts(loader, 2017)

    result = loader.execute({"editions": []})

    assert result == {"defunciones": 0, "editions": []}
    assert (loader.transform_dir / FACTS_DIR / "2017.pkl").exists()


def test_edition_is_deleted_before_its_facts_are_inserted(workdir, monkeypatch):
    loader = load.DefuncionesInegiLoad(mode="update")
    _write_facts(loader, 2024)
    calls = []

    class Result:
        def scalar(self):
            return 0

    class Session:
        def execute(self, statement):
            return Result()

    monkeypatch.setattr(loader, "_resolve_ids", lambda df, *_: df)
    monkeypatch.setattr(loader, "_replace_edition", lambda *_: calls.append("delete"))
    monkeypatch.setattr(load, "bulk_insert", lambda *_, **__: calls.append("insert"))

    loader._load_edition_facts(Session(), 2024, edicion_id=8, mappings={})

    assert calls[:2] == ["delete", "insert"]


def test_finalization_removes_loaded_facts(workdir, monkeypatch):
    loader = load.DefuncionesInegiLoad(mode="update")
    _write_facts(loader, 2024, 2025)

    class SessionContext:
        def __enter__(self):
            class Session:
                def commit(self):
                    pass

            return Session()

        def __exit__(self, *_):
            return False

    class DatabaseStub:
        def get_session(self):
            return SessionContext()

        def disconnect(self):
            pass

    loader.db = DatabaseStub()
    monkeypatch.setattr(load, "sync_id_sequence", lambda *_: None)

    loader.finalization({"defunciones": 1, "editions": [2025]})

    facts_dir = loader.transform_dir / FACTS_DIR
    assert not (facts_dir / "2025.pkl").exists()
    assert (facts_dir / "2024.pkl").exists()


def test_transform_clears_previous_facts_even_without_new_editions(workdir):
    transform = DefuncionesInegiTransform(mode="update")
    facts_dir = transform.work_dir / FACTS_DIR
    facts_dir.mkdir(parents=True, exist_ok=True)
    for year in (2017, 2018):
        pd.DataFrame({"x": [1]}).to_pickle(facts_dir / f"{year}.pkl")

    assert transform.action({}) == {"catalogs": {}, "editions": []}
    assert list(facts_dir.glob("*.pkl")) == []
