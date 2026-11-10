from pathlib import Path

import pytest
from cookiecutter.exceptions import FailedHookException
from cookiecutter.main import cookiecutter

TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "pipeline"


def generate(output_dir: Path, pipeline: str = "mi_pipeline", **context: str) -> None:
    cookiecutter(
        str(TEMPLATE),
        no_input=True,
        overwrite_if_exists=True,
        output_dir=str(output_dir),
        extra_context={"pipeline": pipeline, **context},
    )


def test_generates_both_roots(tmp_path):
    generate(tmp_path)

    expected = [
        "core/pipelines/mi_pipeline/stages/__init__.py",
        "core/pipelines/mi_pipeline/stages/extract.py",
        "core/pipelines/mi_pipeline/stages/transform.py",
        "core/pipelines/mi_pipeline/stages/load.py",
        "core/pipelines/mi_pipeline/queries/__init__.py",
        "core/pipelines/mi_pipeline/attributes/mi_pipeline.py",
        "core/pipelines/mi_pipeline/constants/pipeline.py",
        "core/pipelines/mi_pipeline/mappings/__init__.py",
        "core/pipelines/mi_pipeline/assets/.gitkeep",
        "core/pipelines/mi_pipeline/config.py",
        "core/pipelines/mi_pipeline/schemas.py",
        "core/pipelines/mi_pipeline/.env.example",
        "core/pipelines/mi_pipeline/.env",
        "core/pipelines/mi_pipeline/README.md",
        "migrations/mi_pipeline/flyway.conf",
        "migrations/mi_pipeline/flyway.conf.example",
        "migrations/mi_pipeline/sql/.gitkeep",
        "dags/etl_mi_pipeline.py",
    ]
    assert [path for path in expected if not (tmp_path / path).is_file()] == []


def test_renders_names_and_valid_python(tmp_path):
    generate(tmp_path)
    pipeline_dir = tmp_path / "core/pipelines/mi_pipeline"

    assert "class MiPipelineExtract(Stage)" in (pipeline_dir / "stages/extract.py").read_text()
    assert '"etl_mi_pipeline_bootstrap"' in (tmp_path / "dags/etl_mi_pipeline.py").read_text()
    for path in [*pipeline_dir.rglob("*.py"), tmp_path / "dags/etl_mi_pipeline.py"]:
        compile(path.read_text(), str(path), "exec")


def test_logs_created_paths(tmp_path, capfd):
    generate(tmp_path)
    output = capfd.readouterr().out

    assert "🟢" in output
    for path in ["core/pipelines/mi_pipeline/", "migrations/mi_pipeline/", "dags/etl_mi_pipeline.py", "extract.py"]:
        assert path in output


def test_owner_is_optional(tmp_path):
    generate(tmp_path / "default")
    generate(tmp_path / "custom", owner="Nombre Apellido")

    assert '"owner": "IIEG"' in (tmp_path / "default/dags/etl_mi_pipeline.py").read_text()
    assert '"owner": "Nombre Apellido"' in (tmp_path / "custom/dags/etl_mi_pipeline.py").read_text()


def test_rejects_owner_that_breaks_the_dag(tmp_path):
    with pytest.raises(FailedHookException):
        generate(tmp_path, owner='A "B"')


def test_readme_comes_from_docs_template(tmp_path):
    generate(tmp_path)
    readme = (tmp_path / "core/pipelines/mi_pipeline/README.md").read_text()

    assert readme.startswith("# mi_pipeline\n")
    assert "## Diccionario de variables" in readme
    assert "<nombre_pipeline>" not in readme


def test_local_files_copy_examples_without_secrets(tmp_path):
    generate(tmp_path)
    env_file = tmp_path / "core/pipelines/mi_pipeline/.env"

    assert env_file.read_text() == (env_file.parent / ".env.example").read_text()
    assert "DB_PASSWORD=<DB_PASSWORD>" in env_file.read_text()


@pytest.mark.parametrize("name", ["MiPipeline", "mi-pipeline", "1pipeline", "../salida", "class"])
def test_rejects_invalid_names(tmp_path, name):
    with pytest.raises(FailedHookException):
        generate(tmp_path, name)


@pytest.mark.parametrize(
    "existing",
    ["core/pipelines/mi_pipeline/marker.txt", "migrations/mi_pipeline/marker.txt", "dags/etl_mi_pipeline.py"],
)
def test_does_not_touch_existing_pipeline(tmp_path, existing):
    marker = tmp_path / existing
    marker.parent.mkdir(parents=True)
    marker.write_text("original")

    with pytest.raises(FailedHookException):
        generate(tmp_path)

    assert marker.read_text() == "original"
    assert not (tmp_path / "core/pipelines/mi_pipeline/schemas.py").exists()
