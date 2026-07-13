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
from sqlalchemy_erd import generate_erd, layout_select, star

PIPELINES_DIR = REPO_ROOT / "core" / "pipelines"

THEME = "blue"
NODE_WIDTH = "auto"
FORMAT = "svg"
LAYOUT = "star"


def star_layout_gridded(tables, relationships, star_cols=None, node_w=star.NODE_W):
    """Star layout that places disconnected tables in a grid, not a single row."""
    connected = {t for rel in relationships for t in (rel.from_table, rel.to_table)}
    main = [t for t in tables if t.name in connected]
    disconnected = [t for t in tables if t.name not in connected]

    if not main or not disconnected:
        return star.star_layout(tables, relationships, star_cols, node_w)

    positions = star.star_layout(main, relationships, star_cols, node_w)
    table_map = {t.name: t for t in main}
    max_bottom = max(y + star.node_h(table_map[name]) for name, (_, y) in positions.items())
    offset = max_bottom + star.GAP_Y * 2 - star.MARGIN
    for name, (x, y) in star._grid_layout(disconnected, star.MARGIN, node_w).items():
        positions[name] = (x, round(y + offset, 1))
    return positions


layout_select.star_layout = star_layout_gridded


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
