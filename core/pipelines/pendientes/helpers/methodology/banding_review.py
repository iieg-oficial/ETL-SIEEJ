from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Callable

import matplotlib
import numpy as np

matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402

from core.pipelines.pendientes.constants import BANDING_REVIEW_LABELS


def write_review_csv(path: Path, rows: list[dict[str, Any]]) -> Path:
    if not rows:
        raise ValueError("Banding review CSV requires at least one row")
    for row in rows:
        label = row.get("human_label", "")
        if label and label not in BANDING_REVIEW_LABELS:
            raise ValueError(f"Invalid human banding label: {label}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.csv")
    with temporary.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)
    return path


def read_review_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    for row in rows:
        label = row.get("human_label", "")
        if label and label not in BANDING_REVIEW_LABELS:
            raise ValueError(f"Invalid human banding label: {label}")
    return rows


def write_chip_atlas(
    path: Path,
    arrays: dict[str, np.ndarray],
    metadata: dict[str, Any],
    slope_maximum: float,
    magnitude_maximum: float,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(2, 2, figsize=(12, 10), constrained_layout=True)
    panels = (
        (axes[0, 0], arrays["hillshade"], "Hillshade RAW", "gray", 0.0, 255.0),
        (axes[0, 1], arrays["slope"], "Pendiente Horn exploratoria", "gray", 0.0, slope_maximum),
        (
            axes[1, 0],
            arrays["second_difference"],
            "Magnitud de segunda diferencia",
            "magma",
            0.0,
            magnitude_maximum,
        ),
        (
            axes[1, 1],
            arrays["directed_signature"],
            "Firma dirigida (umbral RAW p90)",
            "magma",
            0.0,
            magnitude_maximum,
        ),
    )
    for axis, values, title, colour_map, minimum, maximum in panels:
        axis.imshow(values, cmap=colour_map, vmin=minimum, vmax=maximum, interpolation="nearest")
        axis.set_title(title)
        axis.set_axis_off()
    figure.suptitle(
        (
            f"{metadata['chip_id']} | X={metadata['center_x']:.1f}, Y={metadata['center_y']:.1f} | "
            f"{metadata['morphology_class']}\n"
            f"autocorr={metadata['autocorrelation']:.4f} | coherence={metadata['axial_coherence']:.4f} | "
            f"continuity={metadata['continuity']:.2f}% | axis={metadata['dominant_axis']} | "
            f"lag={metadata['dominant_lag']} px"
        ),
        fontsize=13,
    )
    temporary = path.with_suffix(".tmp.png")
    figure.savefig(temporary, dpi=120)
    plt.close(figure)
    temporary.replace(path)
    return path


def write_contact_sheet(path: Path, atlas_paths: list[Path], columns: int = 5) -> Path:
    if not atlas_paths:
        raise ValueError("Review contact sheet requires atlas images")
    rows = int(np.ceil(len(atlas_paths) / columns))
    figure, axes = plt.subplots(rows, columns, figsize=(columns * 4, rows * 4.2), constrained_layout=True)
    flat_axes = np.atleast_1d(axes).ravel()
    for axis, atlas_path in zip(flat_axes, atlas_paths, strict=False):
        axis.imshow(plt.imread(atlas_path))
        axis.set_title(atlas_path.stem, fontsize=8)
        axis.set_axis_off()
    for axis in flat_axes[len(atlas_paths) :]:
        axis.set_axis_off()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.png")
    figure.savefig(temporary, dpi=100)
    plt.close(figure)
    temporary.replace(path)
    return path


def percentile_rank(values: list[float], target: float) -> dict[str, float | int]:
    array = np.asarray(values, dtype=np.float64)
    equal = np.isclose(array, target, rtol=1e-12, atol=1e-12)
    lower_count = int(np.count_nonzero(array < target))
    equal_count = int(np.count_nonzero(equal))
    return {
        "value": target,
        "strictly_lower_count": lower_count,
        "equal_count": equal_count,
        "ascending_midrank": float(lower_count + (equal_count + 1) / 2),
        "sample_size": int(array.size),
        "percentile_midrank": float((lower_count + 0.5 * equal_count) / array.size * 100),
        "percentile_leq": float(np.count_nonzero(array <= target) / array.size * 100),
    }


def select_priority_review(
    rows: list[dict[str, Any]],
    maximum: int,
) -> list[dict[str, Any]]:
    if maximum <= 0:
        raise ValueError("Priority review size must be positive")
    selected: list[dict[str, Any]] = []

    def add(row: dict[str, Any], reason: str) -> None:
        existing = next((item for item in selected if item["chip_id"] == row["chip_id"]), None)
        if existing is not None:
            if reason not in existing["reasons"]:
                existing["reasons"].append(reason)
        elif len(selected) < maximum:
            selected.append({"chip_id": row["chip_id"], "reasons": [reason]})

    manual = next(row for row in rows if row["chip_id"] == "problema_manual")
    add(manual, "mandatory positive human reference")
    metrics = (
        "autocorrelation",
        "axial_coherence",
        "continuity",
        "peak_prominence",
        "lag_stable_fraction",
        "energy_anisotropy",
        "long_runs_per_million_cells",
        "profile_spacing_cv",
    )
    for metric in metrics:
        available = [row for row in rows if row[metric] not in (None, "")]
        add(min(available, key=lambda row: (float(row[metric]), row["chip_id"])), f"minimum {metric}")
        add(max(available, key=lambda row: (float(row[metric]), row["chip_id"])), f"maximum {metric}")
    rank_fields = (
        "autocorrelation",
        "axial_coherence",
        "continuity",
        "peak_prominence",
        "lag_stable_fraction",
        "energy_anisotropy",
        "long_runs_per_million_cells",
        "profile_strong_step_count",
    )
    rank_maps = {
        field: {
            row["chip_id"]: rank / max(len(rows) - 1, 1)
            for rank, row in enumerate(sorted(rows, key=lambda item: (float(item[field]), item["chip_id"])))
        }
        for field in rank_fields
    }
    disagreement = sorted(
        rows,
        key=lambda row: (
            -(
                max(rank_maps[field][row["chip_id"]] for field in rank_fields)
                - min(rank_maps[field][row["chip_id"]] for field in rank_fields)
            ),
            row["chip_id"],
        ),
    )
    for row in disagreement[:2]:
        add(row, "large disagreement among metric percentile ranks")
    for morphology in ("plano", "lomerio", "montana", "valle", "transicion_valle_sierra"):
        match = next((row for row in rows if row["morphology_class"] == morphology), None)
        if match is not None:
            add(match, f"morphology coverage: {morphology}")
    seen_lags: set[str] = set()
    for row in sorted(rows, key=lambda item: (int(item["dominant_lag"]), item["chip_id"])):
        lag = str(row["dominant_lag"])
        if lag not in seen_lags:
            add(row, f"distinct dominant lag: {lag} px")
            seen_lags.add(lag)
    return [
        {
            "priority_order": index,
            "chip_id": item["chip_id"],
            "reason": "; ".join(item["reasons"]),
            "reasons": item["reasons"],
        }
        for index, item in enumerate(selected, 1)
    ]


def labeled_metric_distributions(
    rows: list[dict[str, Any]],
    metric_names: tuple[str, ...],
) -> dict[str, Any]:
    labels = {row["human_label"] for row in rows if row.get("human_label")}
    if not {"banding_presente", "banding_ausente"} <= labels:
        return {
            "status": "not_executed_insufficient_human_labels",
            "required_labels": ["banding_presente", "banding_ausente"],
            "observed_labels": sorted(labels),
            "metrics": {},
        }
    output: dict[str, Any] = {}
    for metric in metric_names:
        by_label = {}
        for label in ("banding_presente", "banding_ausente", "dudoso"):
            values = np.array(
                [
                    float(row[metric])
                    for row in rows
                    if row.get("human_label") == label and row[metric] not in (None, "")
                ]
            )
            if values.size:
                by_label[label] = {
                    "count": int(values.size),
                    "median": float(np.median(values)),
                    "q25": float(np.percentile(values, 25)),
                    "q75": float(np.percentile(values, 75)),
                    "iqr": float(np.percentile(values, 75) - np.percentile(values, 25)),
                }
        present = by_label["banding_presente"]
        absent = by_label["banding_ausente"]
        overlap = max(0.0, min(present["q75"], absent["q75"]) - max(present["q25"], absent["q25"]))
        output[metric] = {
            "by_label": by_label,
            "median_separation": present["median"] - absent["median"],
            "iqr_overlap": overlap,
        }
    return {"status": "evaluated", "metrics": output}


def evaluate_candidate_rule(
    rows: list[dict[str, Any]],
    metric: str,
    threshold: float,
    predicate: Callable[[float, float], bool],
) -> dict[str, Any]:
    evaluated = [row for row in rows if row.get("human_label") in {"banding_presente", "banding_ausente"}]
    if {row["human_label"] for row in evaluated} != {"banding_presente", "banding_ausente"}:
        return {"status": "not_executed_insufficient_human_labels"}
    true_positive = false_positive = true_negative = false_negative = 0
    false_positive_ids = []
    false_negative_ids = []
    for row in evaluated:
        predicted = predicate(float(row[metric]), threshold)
        observed = row["human_label"] == "banding_presente"
        if predicted and observed:
            true_positive += 1
        elif predicted:
            false_positive += 1
            false_positive_ids.append(row["chip_id"])
        elif observed:
            false_negative += 1
            false_negative_ids.append(row["chip_id"])
        else:
            true_negative += 1
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    return {
        "status": "evaluated",
        "confusion_matrix": {
            "true_positive": true_positive,
            "false_positive": false_positive,
            "true_negative": true_negative,
            "false_negative": false_negative,
        },
        "precision": precision,
        "recall": recall,
        "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
        "false_positive_chip_ids": false_positive_ids,
        "false_negative_chip_ids": false_negative_ids,
    }
