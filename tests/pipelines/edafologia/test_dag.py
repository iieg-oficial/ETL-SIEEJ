from __future__ import annotations

import importlib
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

for key, value in {
    "SOURCE_URL": "https://example.test/source.zip",
}.items():
    os.environ.setdefault(key, value)

from airflow.models.dag import DAG

from core.pipelines.edafologia.stages.extract import EdafologiaExtract
from core.pipelines.edafologia.stages.load import EdafologiaLoad
from core.pipelines.edafologia.stages.transform import EdafologiaTransform


stage_classes = (
    EdafologiaExtract,
    EdafologiaTransform,
    EdafologiaLoad,
)


def _dag_module():
    return importlib.reload(importlib.import_module("dags.etl_edafologia"))


def test_edafologia_stages_accept_bootstrap_mode():
    for stage_class in stage_classes:
        stage = stage_class(mode="bootstrap")

        assert stage.mode == "bootstrap"


def test_edafologia_stages_keep_default_bootstrap_mode():
    for stage_class in stage_classes:
        stage = stage_class()

        assert stage.mode == "bootstrap"


def test_edafologia_dag_imports_without_runtime_inputs(monkeypatch):
    def fail_run_bootstrap():
        raise AssertionError("DAG import executed the pipeline")

    module = _dag_module()
    monkeypatch.setattr(module, "run_bootstrap", fail_run_bootstrap)

    imported = importlib.reload(module)

    assert imported.dag_bootstrap.dag_id == "etl_edafologia_bootstrap"


def test_edafologia_declares_only_bootstrap_dag():
    module = _dag_module()
    dags = {value.dag_id: value for value in vars(module).values() if isinstance(value, DAG)}

    assert set(dags) == {"etl_edafologia_bootstrap"}
    assert dags["etl_edafologia_bootstrap"].schedule is None
    assert dags["etl_edafologia_bootstrap"].catchup is False
    assert dags["etl_edafologia_bootstrap"].max_active_runs == 1
    assert "etl_edafologia_update" not in dags


def test_run_bootstrap_builds_expected_stage_order(monkeypatch):
    module = _dag_module()
    built_stages = []
    run_modes = []

    class FakePipeline:
        def __init__(self, name, stages):
            self.name = name
            self.stages = stages

        def run(self, mode="bootstrap"):
            run_modes.append(mode)

    def fake_stage(name):
        class FakeStage:
            def __init__(self, mode="bootstrap"):
                self.name = name
                self.mode = mode
                built_stages.append(self)

        return FakeStage

    monkeypatch.setattr("core.pipeline.Pipeline", FakePipeline)
    monkeypatch.setattr("core.pipelines.edafologia.stages.extract.EdafologiaExtract", fake_stage("extract"))
    monkeypatch.setattr("core.pipelines.edafologia.stages.transform.EdafologiaTransform", fake_stage("transform"))
    monkeypatch.setattr("core.pipelines.edafologia.stages.load.EdafologiaLoad", fake_stage("load"))
    module.run_bootstrap()

    assert [stage.name for stage in built_stages] == ["extract", "transform", "load"]
    assert [stage.mode for stage in built_stages] == ["bootstrap"] * 3
    assert run_modes == ["bootstrap"]


def test_edafologia_dag_does_not_expose_credentials():
    module = _dag_module()
    serialized = repr(module.dag_bootstrap) + repr(module.default_args_bootstrap)

    assert "PASSWORD" not in serialized.upper()
    assert "CVEGEO" not in serialized.upper()
