from __future__ import annotations

from pathlib import Path
from typing import Any

import pyogrio

from core.pipelines.edafologia.constants import (
    EXCLUDED_POINT_LAYER_SUFFIX,
    EXPECTED_AREA_LAYER_STEM,
    POLYGON_GEOMETRY_TYPES,
    VECTOR_EXTENSIONS,
)


def _layers_for(path: Path) -> list[str | None]:
    if path.suffix.lower() == ".gpkg":
        return [str(layer) for layer, _ in pyogrio.list_layers(path)]
    return [None]


def _format_bounds(bounds: Any) -> list[float] | None:
    if bounds is None:
        return None
    try:
        return [float(value) for value in bounds]
    except (TypeError, ValueError):
        return None


def _candidate_path_name(path: Path, layer: str | None) -> str:
    return layer or path.stem


def inspect_vector_candidates(extract_dir: Path, required_fields: tuple[str, ...]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    root = extract_dir.resolve()

    for path in sorted(extract_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in VECTOR_EXTENSIONS:
            continue
        for layer in _layers_for(path):
            try:
                info = pyogrio.read_info(path, layer=layer)
            except Exception as exc:
                candidates.append(
                    {
                        "relative_path": str(path.resolve().relative_to(root)),
                        "layer": _candidate_path_name(path, layer),
                        "format": path.suffix.lower().lstrip("."),
                        "readable": False,
                        "error": str(exc),
                    }
                )
                continue

            fields = [str(field) for field in info.get("fields", [])]
            required_found = [field for field in required_fields if field in fields]
            required_missing = [field for field in required_fields if field not in fields]
            candidates.append(
                {
                    "relative_path": str(path.resolve().relative_to(root)),
                    "layer": _candidate_path_name(path, layer),
                    "format": str(info.get("driver") or path.suffix.lower().lstrip(".")),
                    "readable": True,
                    "geometry_type": str(info.get("geometry_type")),
                    "crs": str(info.get("crs")) if info.get("crs") is not None else None,
                    "feature_count": int(info.get("features", 0) or 0),
                    "fields": fields,
                    "required_fields_found": required_found,
                    "required_fields_missing": required_missing,
                    "extent": _format_bounds(info.get("total_bounds")),
                }
            )

    return sorted(candidates, key=lambda item: (str(item.get("relative_path")), str(item.get("layer"))))


def select_canonical_candidate(candidates: list[dict[str, Any]], required_fields: tuple[str, ...]) -> dict[str, Any]:
    valid_candidates = []

    for candidate in candidates:
        if not candidate.get("readable"):
            continue
        layer = str(candidate.get("layer") or "")
        path = Path(str(candidate.get("relative_path") or ""))
        name = layer or path.stem
        if name.endswith(EXCLUDED_POINT_LAYER_SUFFIX) or path.stem.endswith(EXCLUDED_POINT_LAYER_SUFFIX):
            continue
        if name != EXPECTED_AREA_LAYER_STEM and path.stem != EXPECTED_AREA_LAYER_STEM:
            continue
        if candidate.get("geometry_type") not in POLYGON_GEOMETRY_TYPES:
            continue
        if any(field not in candidate.get("fields", []) for field in required_fields):
            continue
        valid_candidates.append(candidate)

    if not valid_candidates:
        missing_summary = [
            {
                "relative_path": item.get("relative_path"),
                "layer": item.get("layer"),
                "geometry_type": item.get("geometry_type"),
                "required_fields_missing": item.get("required_fields_missing"),
            }
            for item in candidates
            if item.get("readable")
        ]
        raise ValueError(f"No canonical Edafologia polygon layer found. Candidates: {missing_summary[:10]}")

    if len(valid_candidates) > 1:
        paths = [f"{item['relative_path']}::{item['layer']}" for item in valid_candidates]
        raise ValueError(f"Ambiguous canonical Edafologia layers: {paths}")

    return valid_candidates[0]
