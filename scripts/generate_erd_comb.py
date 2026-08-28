"""ERD con layout de peine para esquemas de hechos y catálogos.

Los layouts de `sqlalchemy-erd` (star, force, layered) no sirven cuando una
tabla de hechos referencia decenas de catálogos casi idénticos: las cajas se
enciman y no se distingue el destino de cada flecha.

Aquí los catálogos se ordenan verticalmente según el orden de su FK dentro de la
tabla de hechos, así las aristas quedan monótonas y no se cruzan. Las rutas son
ortogonales y cada una usa su propia canaleta vertical.

Uso:
    python scripts/generate_erd_comb.py defunciones_inegi
"""

from __future__ import annotations

import argparse
import html
import importlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy_erd.theme import get_theme

FACT_PREFIX = "stg_"

BOX_W = 250
HEADER_H = 30
ROW_H = 19
GAP_Y = 26
COL_GAP = 150
MARGIN = 40
FONT = "ui-monospace, 'SF Mono', 'Cascadia Mono', Menlo, monospace"

# Colores tomados de los temas de sqlalchemy-erd para que el diagrama sea
# coherente con el resto de los ERD del proyecto.
CATALOG_THEME = get_theme("blue")
FACT_THEME = get_theme("green")

CATALOG_HEADER = CATALOG_THEME.header_color
FACT_HEADER = FACT_THEME.header_color
BG = CATALOG_THEME.bg_color
CARD_BG = CATALOG_THEME.card_bg
BORDER = CATALOG_THEME.card_border
LINE = CATALOG_THEME.edge_color
INK = CATALOG_THEME.field_text_color
KIND = CATALOG_THEME.kind_colors
PK_INK = KIND["pk"]
FK_INK = KIND["fk"]
MUTED = KIND["other"]


def columns_of(table):
    out = []
    for col in table.columns:
        kind = "PK" if col.primary_key else ("FK" if col.foreign_keys else "")
        out.append((col.name, str(col.type).split("(")[0].lower(), kind))
    return out


def box_height(table):
    return HEADER_H + ROW_H * len(table.columns) + 8


def fk_targets(table):
    """(columna, tabla destino) en el orden en que aparecen en la tabla."""
    out = []
    for col in table.columns:
        for fk in col.foreign_keys:
            out.append((col.name, fk.column.table.name))
    return out


def render_box(x, y, table, rows, header=CATALOG_HEADER):
    h = HEADER_H + ROW_H * len(rows) + 8
    parts = [
        f'<g><rect x="{x}" y="{y}" width="{BOX_W}" height="{h}" rx="6" fill="{CARD_BG}" stroke="{BORDER}"/>',
        f'<path d="M{x} {y + 6}a6 6 0 0 1 6-6h{BOX_W - 12}a6 6 0 0 1 6 6v{HEADER_H - 6}H{x}z" fill="{header}"/>',
        f'<text x="{x + 12}" y="{y + 20}" font-family="{FONT}" font-size="12" font-weight="700" fill="#fff">'
        f"{html.escape(table.name)}</text>",
    ]
    for i, (name, kind, flag) in enumerate(rows):
        ty = y + HEADER_H + ROW_H * i + 14
        color = FK_INK if flag == "FK" else (PK_INK if flag == "PK" else INK)
        weight = "700" if flag == "PK" else "400"
        parts.append(
            f'<text x="{x + 12}" y="{ty}" font-family="{FONT}" font-size="10.5" fill="{color}" '
            f'font-weight="{weight}">{html.escape(name)}</text>'
        )
        label = flag or kind
        tint = KIND.get(kind, MUTED) if not flag else MUTED
        parts.append(
            f'<text x="{x + BOX_W - 12}" y="{ty}" font-family="{FONT}" font-size="9" fill="{tint}" '
            f'text-anchor="end">{html.escape(label)}</text>'
        )
    parts.append("</g>")
    return "".join(parts), h


def edge(x1, y1, x2, y2, to_left, lane):
    """Ruta ortogonal: sale horizontal, gira en una canaleta y entra horizontal.

    Cada arista usa su propia canaleta vertical (`lane`) para que los tramos no
    se encimen.
    """
    if abs(y1 - y2) < 1:
        path = f"M{x1} {y1} H{x2}"
    else:
        path = f"M{x1} {y1} H{lane} V{y2} H{x2}"
    head = (
        f"{x2 + 7},{y2 - 4} {x2},{y2} {x2 + 7},{y2 + 4}"
        if to_left
        else f"{x2 - 7},{y2 - 4} {x2},{y2} {x2 - 7},{y2 + 4}"
    )
    return (
        f'<path d="{path}" fill="none" stroke="{LINE}" stroke-width="1.2" '
        f'stroke-linejoin="round"/>'
        f'<polyline points="{head}" fill="none" stroke="{LINE}" stroke-width="1.2"/>'
    )


def build_block(fact, tables, start_y, used):
    """Un bloque = tabla de hechos al centro y sus catálogos repartidos a los lados."""
    rows = columns_of(fact)
    row_index = {name: i for i, (name, _, _) in enumerate(rows)}

    # Orden de aparición de las FK: define el orden vertical de los catálogos.
    targets, seen = [], set()
    for col, target in fk_targets(fact):
        if target in used or target in seen or target == fact.name:
            continue
        seen.add(target)
        targets.append((col, target))

    half = (len(targets) + 1) // 2
    sides = {"left": targets[:half], "right": targets[half:]}

    heights = {
        side: sum(box_height(tables[t]) + GAP_Y for _, t in items) - GAP_Y if items else 0
        for side, items in sides.items()
    }
    fact_h = box_height(fact)
    block_h = max(fact_h, *heights.values())

    fact_x = MARGIN + BOX_W + COL_GAP
    fact_y = start_y + (block_h - fact_h) // 2
    svg = [render_box(fact_x, fact_y, fact, rows, header=FACT_HEADER)[0]]

    positions = {}
    for side, items in sides.items():
        x = MARGIN if side == "left" else fact_x + BOX_W + COL_GAP
        y = start_y + (block_h - heights[side]) // 2
        for col, name in items:
            table = tables[name]
            body, h = render_box(x, y, table, columns_of(table))
            svg.append(body)
            positions[name] = (x, y + h / 2, side)
            used.add(name)
            y += h + GAP_Y

    edges = []
    per_side = {"left": 0, "right": 0}
    for col, name in targets:
        x, y, side = positions[name]
        fy = fact_y + HEADER_H + ROW_H * row_index[col] + 10
        if side == "left":
            fx, tx = fact_x, x + BOX_W
            lane = tx + 18 + per_side["left"] * 8
        else:
            fx, tx = fact_x + BOX_W, x
            lane = tx - 18 - per_side["right"] * 8
        per_side[side] += 1
        edges.append(edge(fx, fy, tx, y, to_left=(side == "left"), lane=lane))

    geometry = {"x": fact_x, "y": fact_y, "h": fact_h, "rows": row_index}
    return "".join(edges) + "".join(svg), block_h, fact_x + BOX_W + COL_GAP + BOX_W + MARGIN, geometry


def find_base(pipeline: str) -> type[DeclarativeBase]:
    module = importlib.import_module(f"core.pipelines.{pipeline}.schemas")
    for value in vars(module).values():
        if isinstance(value, type) and issubclass(value, DeclarativeBase) and value is not DeclarativeBase:
            if getattr(value, "__abstract__", False) or hasattr(value, "__tablename__"):
                continue
            return value
    raise LookupError(f"No se encontró el DeclarativeBase de {pipeline}")


def render(pipeline: str) -> Path:
    base = find_base(pipeline)
    tables = {t.name: t for t in base.metadata.sorted_tables}
    facts = [t for name, t in tables.items() if name.startswith(FACT_PREFIX)]
    used: set[str] = {t.name for t in facts}
    body, width = [], 0
    y = MARGIN

    geometries = {}
    for fact in facts:
        chunk, h, w, geometry = build_block(fact, tables, y, used)
        body.append(chunk)
        geometries[fact.name] = geometry
        width = max(width, w)
        y += h + 90

    # La relación 1:1 entre las dos tablas de hechos, que no es un catálogo.
    top, bottom = (geometries[t.name] for t in facts[:2])
    y_from = top["y"] + HEADER_H + ROW_H * top["rows"]["id"] + 10
    y_to = bottom["y"] + HEADER_H + ROW_H * bottom["rows"]["defuncion_id"] + 10
    lane = top["x"] - 46
    body.append(
        f'<path d="M{top["x"]} {y_from} H{lane} V{y_to} H{bottom["x"]}" fill="none" '
        f'stroke="{LINE}" stroke-width="1.6" stroke-dasharray="5 3" stroke-linejoin="round"/>'
        f'<polyline points="{bottom["x"] - 7},{y_to - 4} {bottom["x"]},{y_to} {bottom["x"] - 7},{y_to + 4}" '
        f'fill="none" stroke="{LINE}" stroke-width="1.6"/>'
        f'<text x="{lane + 6}" y="{(y_from + y_to) / 2}" font-family="{FONT}" font-size="10" '
        f'fill="{MUTED}">1:1</text>'
    )

    # Catálogos que ninguna tabla de hechos referencia directamente.
    leftovers = [n for n in tables if n not in used]
    if leftovers:
        x = MARGIN
        row_top = y
        for name in leftovers:
            table = tables[name]
            chunk, h = render_box(x, row_top, table, columns_of(table))
            body.append(chunk)
            x += BOX_W + GAP_Y
            if x + BOX_W > width:
                x = MARGIN
                row_top += h + GAP_Y
        y = row_top + 140

    height = y
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        f'<rect width="{width}" height="{height}" fill="{BG}"/>' + "".join(body) + "</svg>"
    )
    out = REPO_ROOT / "core" / "pipelines" / pipeline / "assets" / "erd.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg + "\n", encoding="utf-8")
    print(f"Generated {out.relative_to(REPO_ROOT)} ({width}x{height}, {len(tables)} tablas)")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="ERD con layout de peine")
    parser.add_argument("pipeline", help="Nombre del pipeline en core/pipelines/")
    render(parser.parse_args().pipeline)


if __name__ == "__main__":
    main()
