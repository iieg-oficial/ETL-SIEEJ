import shutil
from pathlib import Path

pipeline = "{{ cookiecutter.pipeline }}"
repo_root = Path("{{ cookiecutter._repo_dir }}").resolve().parents[1]
pipeline_dir = Path("core/pipelines") / pipeline
migrations_dir = Path("migrations") / pipeline

shutil.copyfile(pipeline_dir / ".env.example", pipeline_dir / ".env")
shutil.copyfile(migrations_dir / "flyway.conf.example", migrations_dir / "flyway.conf")

template = (repo_root / "docs/readme-pipeline.md").read_text(encoding="utf-8")
readme = template.split("```markdown\n", 1)[1].rsplit("```", 1)[0]
(pipeline_dir / "README.md").write_text(readme.replace("<nombre_pipeline>", pipeline), encoding="utf-8")
