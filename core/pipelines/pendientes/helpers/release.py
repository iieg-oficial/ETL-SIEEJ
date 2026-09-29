from __future__ import annotations

import errno
import os
import shutil
from pathlib import Path
from typing import Any

from core.pipelines.pendientes.helpers.cog import validate_cog_structure
from core.utils.files import sha256_file


def materialize_release_file(source: Path, destination: Path, expected_sha256: str) -> dict[str, Any]:
    if sha256_file(source) != expected_sha256:
        raise ValueError(f"Transform COG checksum changed: {source}")
    validate_cog_structure(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        observed = sha256_file(destination)
        if observed != expected_sha256:
            raise ValueError(f"Existing release artifact is corrupt or incompatible: {destination}")
        return {
            "source": str(source),
            "destination": str(destination),
            "sha256": observed,
            "strategy": "existing_validated",
            "created": False,
        }
    temporary = destination.with_name(f".{destination.name}.partial")
    temporary.unlink(missing_ok=True)
    strategy = "hardlink_atomic"
    try:
        try:
            os.link(source, temporary)
        except OSError as error:
            if error.errno not in {errno.EXDEV, errno.EPERM, errno.EACCES, errno.EMLINK}:
                raise
            strategy = "copy_atomic"
            shutil.copyfile(source, temporary)
        observed = sha256_file(temporary)
        if observed != expected_sha256:
            raise ValueError(f"Release materialization checksum mismatch: {destination}")
        os.replace(temporary, destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return {
        "source": str(source),
        "destination": str(destination),
        "sha256": observed,
        "strategy": strategy,
        "created": True,
    }
