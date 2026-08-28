from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from affine import Affine

from core.pipelines.pendientes.constants import CALIBRATION_PROFILE_OFFSETS_PIXELS
from core.pipelines.pendientes.helpers.directed_banding import directed_banding_metrics


@dataclass(frozen=True)
class ProfileLine:
    profile_id: str
    normal_angle_degrees: float
    tangent_offset_pixels: int
    rows: tuple[int, ...]
    columns: tuple[int, ...]


def _deduplicate_cells(rows: np.ndarray, columns: np.ndarray) -> tuple[tuple[int, ...], tuple[int, ...]]:
    keep = np.ones(rows.size, dtype=bool)
    keep[1:] = (rows[1:] != rows[:-1]) | (columns[1:] != columns[:-1])
    return tuple(int(value) for value in rows[keep]), tuple(int(value) for value in columns[keep])


def profile_lines_from_raw(
    raw: np.ndarray,
    nodata: float | None,
    offsets: tuple[int, ...] = CALIBRATION_PROFILE_OFFSETS_PIXELS,
) -> tuple[list[ProfileLine], dict[str, Any]]:
    banding, _, _ = directed_banding_metrics(raw, nodata)
    angle_degrees = banding["orientation"]["dominant_normal_degrees"]
    if angle_degrees is None:
        raise ValueError("Cannot orient profiles because RAW has no directed second-difference structure")
    angle = math.radians(angle_degrees)
    column_direction = math.cos(angle)
    row_direction = math.sin(angle)
    tangent_column = -row_direction
    tangent_row = column_direction
    center_row = (raw.shape[0] - 1) / 2
    center_column = (raw.shape[1] - 1) / 2
    diagonal = math.ceil(math.hypot(*raw.shape))
    parameter = np.arange(-diagonal, diagonal + 1, dtype=np.float64)
    lines: list[ProfileLine] = []
    for index, offset in enumerate(offsets, start=1):
        origin_row = center_row + offset * tangent_row
        origin_column = center_column + offset * tangent_column
        rows = np.rint(origin_row + parameter * row_direction).astype(np.int32)
        columns = np.rint(origin_column + parameter * column_direction).astype(np.int32)
        inside = (rows >= 0) & (rows < raw.shape[0]) & (columns >= 0) & (columns < raw.shape[1])
        unique_rows, unique_columns = _deduplicate_cells(rows[inside], columns[inside])
        if len(unique_rows) < min(raw.shape) // 2:
            raise ValueError("Derived calibration profile is unexpectedly short")
        lines.append(
            ProfileLine(
                profile_id=f"transecto_{index}",
                normal_angle_degrees=angle_degrees,
                tangent_offset_pixels=offset,
                rows=unique_rows,
                columns=unique_columns,
            )
        )
    return lines, {
        "orientation_source": "RAW dominant axial normal of high second-difference cells",
        "normal_angle_degrees": angle_degrees,
        "tangent_offsets_pixels": list(offsets),
        "sampling": "nearest baseline cell along one-pixel-spaced rasterized lines",
    }


def profile_records(
    line: ProfileLine,
    raw: np.ndarray,
    candidates: dict[str, np.ndarray],
    transform: Affine,
) -> list[dict[str, Any]]:
    rows = np.asarray(line.rows)
    columns = np.asarray(line.columns)
    x = transform.c + transform.a * (columns + 0.5) + transform.b * (rows + 0.5)
    y = transform.f + transform.d * (columns + 0.5) + transform.e * (rows + 0.5)
    segment_distance = np.hypot(np.diff(x), np.diff(y))
    distance = np.concatenate(([0.0], np.cumsum(segment_distance)))
    raw_values = raw[rows, columns].astype(np.float64, copy=False)
    records: list[dict[str, Any]] = []
    for index in range(rows.size):
        record: dict[str, Any] = {
            "profile_id": line.profile_id,
            "sample_index": index,
            "distance_m": float(distance[index]),
            "row": int(rows[index]),
            "column": int(columns[index]),
            "x": float(x[index]),
            "y": float(y[index]),
            "elevation_RAW_m": float(raw_values[index]),
        }
        for candidate_id, values in candidates.items():
            candidate_value = float(values[rows[index], columns[index]])
            record[f"elevation_{candidate_id}_m"] = candidate_value
            record[f"delta_{candidate_id}_m"] = candidate_value - float(raw_values[index])
        records.append(record)
    return records


def write_profile_csv(path: Path, records: list[dict[str, Any]]) -> Path:
    if not records:
        raise ValueError("Profile CSV requires records")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.csv")
    with temporary.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    temporary.replace(path)
    return path


def _draw_line(image: np.ndarray, start: tuple[int, int], end: tuple[int, int], color: tuple[int, int, int]) -> None:
    x0, y0 = start
    x1, y1 = end
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    x = np.rint(np.linspace(x0, x1, steps + 1)).astype(int)
    y = np.rint(np.linspace(y0, y1, steps + 1)).astype(int)
    inside = (x >= 0) & (x < image.shape[1]) & (y >= 0) & (y < image.shape[0])
    image[y[inside], x[inside]] = color


def write_profile_png(
    path: Path,
    records: list[dict[str, Any]],
    candidate_order: tuple[str, ...],
) -> dict[str, Any]:
    if not records:
        raise ValueError("Profile PNG requires records")
    width, height = 1200, 600
    left, right, top, bottom = 70, 30, 30, 50
    image = np.full((height, width, 3), 255, dtype=np.uint8)
    colors = {
        "RAW": (0, 0, 0),
        "B2": (0, 102, 204),
        "FP1": (0, 153, 76),
        "FP2": (230, 126, 34),
        "FP3": (142, 68, 173),
        "FP4": (192, 57, 43),
    }
    distance = np.array([record["distance_m"] for record in records], dtype=np.float64)
    series = {
        candidate_id: np.array([record[f"elevation_{candidate_id}_m"] for record in records], dtype=np.float64)
        for candidate_id in candidate_order
    }
    elevation_minimum = min(float(values.min()) for values in series.values())
    elevation_maximum = max(float(values.max()) for values in series.values())
    elevation_margin = max((elevation_maximum - elevation_minimum) * 0.05, 0.01)
    elevation_minimum -= elevation_margin
    elevation_maximum += elevation_margin
    x_pixels = left + (distance - distance.min()) / max(np.ptp(distance), 1.0) * (width - left - right)
    _draw_line(image, (left, top), (left, height - bottom), (80, 80, 80))
    _draw_line(image, (left, height - bottom), (width - right, height - bottom), (80, 80, 80))
    for candidate_id in candidate_order:
        values = series[candidate_id]
        y_pixels = top + (elevation_maximum - values) / (elevation_maximum - elevation_minimum) * (
            height - top - bottom
        )
        for index in range(1, values.size):
            _draw_line(
                image,
                (int(x_pixels[index - 1]), int(y_pixels[index - 1])),
                (int(x_pixels[index]), int(y_pixels[index])),
                colors[candidate_id],
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.png")
    with rasterio.open(
        temporary,
        "w",
        driver="PNG",
        width=width,
        height=height,
        count=3,
        dtype="uint8",
    ) as destination:
        destination.write(np.moveaxis(image, 2, 0))
    temporary.replace(path)
    return {
        "path": str(path),
        "distance_range_m": [float(distance.min()), float(distance.max())],
        "shared_elevation_range_m": [elevation_minimum, elevation_maximum],
        "series_order": list(candidate_order),
        "colors_rgb": {candidate_id: list(colors[candidate_id]) for candidate_id in candidate_order},
        "independent_autoscaling": False,
    }
