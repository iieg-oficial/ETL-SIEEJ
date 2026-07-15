from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


def _member_target(root: Path, member_name: str) -> Path:
    member_path = Path(member_name)
    if member_path.is_absolute() or ".." in member_path.parts:
        raise ValueError(f"Unsafe ZIP member path: {member_name}")
    target = (root / member_path).resolve()
    root_resolved = root.resolve()
    if target != root_resolved and root_resolved not in target.parents:
        raise ValueError(f"ZIP member escapes extraction directory: {member_name}")
    return target


def safe_extract_zip(zip_path: Path, extract_dir: Path, force: bool = False, logger=None) -> Path:
    if force and extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)
    root = extract_dir.resolve()

    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            target = _member_target(root, member.filename)
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            if target.exists():
                if logger:
                    logger.info("[action] Reusing extracted member: %s", target)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)

    if logger:
        logger.info("[action] ZIP extracted to %s", extract_dir)
    return extract_dir
