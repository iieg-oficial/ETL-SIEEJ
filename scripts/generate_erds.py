"""Generate ERD diagrams for pipeline schemas.

Renders ``core/pipelines/<pipeline>/assets/erd.svg`` from each pipeline's
SQLAlchemy ``DeclarativeBase`` using the project's theme.

Usage:
    python scripts/generate_erds.py                 # all pipelines with schemas.py
    python scripts/generate_erds.py censos_economicos denue
"""

import argparse
import importlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy_erd import generate_erd

PIPELINES_DIR = REPO_ROOT / "core" / "pipelines"

THEME = "blue"
NODE_WIDTH = "auto"
FORMAT = "svg"
LAYOUT = "star"


def find_base(pipeline: str) -> type[DeclarativeBase]:
    module = importlib.import_module(f"core.pipelines.{pipeline}.schemas")
    for obj in vars(module).values():
        if isinstance(obj, type) and DeclarativeBase in obj.__bases__:
            return obj
    raise LookupError(f"No DeclarativeBase subclass found in {pipeline}.schemas")


def discover_pipelines() -> list[str]:
    return sorted(p.parent.name for p in PIPELINES_DIR.glob("*/schemas.py"))


def generate(pipeline: str, layout: str = LAYOUT) -> None:
    base = find_base(pipeline)
    output = PIPELINES_DIR / pipeline / "assets" / "erd.svg"
    output.parent.mkdir(parents=True, exist_ok=True)
    generate_erd(
        base,
        output=str(output),
        format=FORMAT,
        theme=THEME,
        node_width=NODE_WIDTH,
        layout=layout,
    )
    print(f"Generated {output.relative_to(REPO_ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate pipeline ERD diagrams")
    parser.add_argument("pipelines", nargs="*", help="Pipeline names (default: all)")
    parser.add_argument(
        "--layout",
        default=LAYOUT,
        choices=["star", "force", "layered"],
        help=f"Layout algorithm (default: {LAYOUT})",
    )
    args = parser.parse_args()

    pipelines = args.pipelines or discover_pipelines()
    failed = []
    for pipeline in pipelines:
        try:
            generate(pipeline, layout=args.layout)
        except Exception as exc:
            failed.append((pipeline, exc))
            print(f"FAILED {pipeline}: {exc}", file=sys.stderr)

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
