from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Any

from core.utils.files import sha256_file


def inspect_whitebox_backend(
    executable: Path,
    expected_version: str,
    expected_sha256: str,
) -> dict[str, Any]:
    if not executable.is_file():
        raise FileNotFoundError(f"WhiteboxTools executable not found: {executable}")
    observed_sha256 = sha256_file(executable)
    if observed_sha256 != expected_sha256:
        raise ValueError("WhiteboxTools executable checksum does not match the configured contract")
    version_result = subprocess.run(
        [str(executable), "--version"],
        check=True,
        capture_output=True,
        text=True,
    )
    version_line = version_result.stdout.splitlines()[0].strip()
    if version_line != expected_version:
        raise ValueError(f"WhiteboxTools version mismatch: expected {expected_version!r}, observed {version_line!r}")
    license_result = subprocess.run(
        [str(executable), "--license"],
        check=True,
        capture_output=True,
        text=True,
    )
    if "Permission is hereby granted" not in license_result.stdout:
        raise ValueError("WhiteboxTools did not report the expected MIT license text")
    help_result = subprocess.run(
        [str(executable), "--toolhelp=FeaturePreservingSmoothing"],
        check=True,
        capture_output=True,
        text=True,
    )
    required_parameters = ("--filter", "--norm_diff", "--num_iter", "--max_diff", "--zfactor")
    if not all(parameter in help_result.stdout for parameter in required_parameters):
        raise ValueError("WhiteboxTools FeaturePreservingSmoothing contract is incomplete")
    return {
        "status": "available",
        "executable": str(executable),
        "executable_sha256": observed_sha256,
        "observed_version": version_line,
        "expected_exact_version": expected_version,
        "license": "MIT",
        "tool": "FeaturePreservingSmoothing",
        "required_parameters_verified": list(required_parameters),
    }


def run_feature_preserving_smoothing(
    backend: dict[str, Any],
    input_path: Path,
    output_path: Path,
    configuration: dict[str, float | int | str],
) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(".tmp.tif")
    temporary.unlink(missing_ok=True)
    command = [
        str(backend["executable"]),
        "-r=FeaturePreservingSmoothing",
        "-v",
        f"--dem={input_path.resolve()}",
        f"--output={temporary.resolve()}",
        f"--filter={int(configuration['filter'])}",
        f"--norm_diff={float(configuration['norm_diff_degrees'])}",
        f"--num_iter={int(configuration['num_iter'])}",
        f"--max_diff={float(configuration['max_diff_m'])}",
        "--zfactor=1.0",
    ]
    started = time.perf_counter()
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        temporary.replace(output_path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return {
        "command": command,
        "elapsed_seconds": time.perf_counter() - started,
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_path": str(output_path),
        "output_sha256": sha256_file(output_path),
    }
