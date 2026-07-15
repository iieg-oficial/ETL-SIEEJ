from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import pandas as pd

from core.pipelines.edafologia.helpers.download import sha256_file


def validate_dictionary(path: Path, key_field: str, description_field: str) -> dict[str, Any]:
    frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing_fields = [field for field in (key_field, description_field) if field not in frame.columns]
    if missing_fields:
        raise ValueError(f"Dictionary {path} is missing required columns: {missing_fields}")

    key = frame[key_field].fillna("").astype(str).str.strip()
    description = frame[description_field].fillna("").astype(str).str.strip()
    duplicated_keys = sorted(key[key.ne("") & key.duplicated(keep=False)].drop_duplicates().tolist())
    empty_keys = int(key.eq("").sum())
    empty_descriptions = int(description.eq("").sum())

    if duplicated_keys:
        raise ValueError(f"Dictionary {path} contains duplicated keys: {duplicated_keys[:20]}")
    if empty_keys:
        raise ValueError(f"Dictionary {path} contains {empty_keys} empty keys")
    if empty_descriptions:
        raise ValueError(f"Dictionary {path} contains {empty_descriptions} empty descriptions")

    return {
        "source_path": str(path),
        "columns": list(frame.columns),
        "key_field": key_field,
        "description_field": description_field,
        "row_count": int(len(frame)),
        "duplicated_keys": duplicated_keys,
        "empty_keys": empty_keys,
        "empty_descriptions": empty_descriptions,
    }


def copy_dictionary(
    name: str,
    source_path: Path,
    output_dir: Path,
    key_field: str,
    description_field: str,
    previous_manifest: dict[str, Any] | None,
    force: bool,
) -> dict[str, Any]:
    if not source_path.exists():
        raise FileNotFoundError(f"Dictionary source does not exist: {source_path}")

    source_validation = validate_dictionary(source_path, key_field, description_field)
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / source_path.name
    source_hash = sha256_file(source_path)

    previous = (previous_manifest or {}).get(name, {})
    can_reuse = (
        destination.exists()
        and not force
        and previous.get("temporary_path") == str(destination)
        and previous.get("sha256") == source_hash
        and sha256_file(destination) == source_hash
    )
    if not can_reuse:
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        shutil.copy2(source_path, temporary)
        temporary.replace(destination)

    copied_validation = validate_dictionary(destination, key_field, description_field)
    return {
        **copied_validation,
        "source_path": str(source_path),
        "temporary_path": str(destination),
        "copied_name": destination.name,
        "sha256": sha256_file(destination),
        "size_bytes": destination.stat().st_size,
    }


def prepare_dictionaries(
    specs: dict[str, dict[str, str]],
    paths_by_setting: dict[str, str],
    output_dir: Path,
    previous_manifest: dict[str, Any] | None,
    force: bool,
) -> dict[str, Any]:
    return {
        name: copy_dictionary(
            name=name,
            source_path=Path(paths_by_setting[spec["path_setting"]]).expanduser().resolve(),
            output_dir=output_dir,
            key_field=spec["key_field"],
            description_field=spec["description_field"],
            previous_manifest=previous_manifest,
            force=force,
        )
        for name, spec in specs.items()
    }
