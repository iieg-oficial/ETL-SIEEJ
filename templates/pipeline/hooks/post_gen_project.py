import shutil
import sys
from pathlib import Path

pipeline = "{{ cookiecutter.pipeline }}"
repo_root = Path("{{ cookiecutter._repo_dir }}").resolve().parents[1]
pipeline_dir = Path("core/pipelines") / pipeline
migrations_dir = Path("migrations") / pipeline
dag_file = Path("dags") / f"etl_{pipeline}.py"

sys.path.insert(0, str(repo_root))

from core.utils.logger import get_console_logger  # noqa: E402

logger = get_console_logger("new-pipeline")


def tree_lines(root: Path) -> list[str]:
    lines = [f"{root}/"]
    for path in sorted(root.rglob("*")):
        indent = "  " * len(path.relative_to(root).parts)
        lines.append(f"{indent}{path.name}{'/' if path.is_dir() else ''}")
    return lines


shutil.copyfile(pipeline_dir / ".env.example", pipeline_dir / ".env")
shutil.copyfile(migrations_dir / "flyway.conf.example", migrations_dir / "flyway.conf")

template = (repo_root / "docs/readme-pipeline.md").read_text(encoding="utf-8")
readme = template.split("```markdown\n", 1)[1].rsplit("```", 1)[0]
(pipeline_dir / "README.md").write_text(readme.replace("<nombre_pipeline>", pipeline), encoding="utf-8")

created = [*tree_lines(pipeline_dir), *tree_lines(migrations_dir), str(dag_file)]
logger.info("🟢 Pipeline '%s' created:\n%s", pipeline, "\n".join(created))
