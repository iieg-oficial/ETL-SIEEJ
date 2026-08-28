from __future__ import annotations

import shutil
import time
import zipfile
from datetime import datetime
from pathlib import Path

import requests

from core.utils.files import sha256_file, validate_zip


def _remote_size(response: requests.Response, offset: int) -> int | None:
    content_range = response.headers.get("Content-Range", "")
    if "/" in content_range and content_range.rsplit("/", 1)[-1].isdigit():
        return int(content_range.rsplit("/", 1)[-1])
    content_length = response.headers.get("Content-Length")
    return offset + int(content_length) if content_length and content_length.isdigit() else None


def _download_once(
    url: str,
    temporary_path: Path,
    connect_timeout: int,
    read_timeout: int,
    chunk_size: int,
) -> None:
    offset = temporary_path.stat().st_size if temporary_path.exists() else 0
    headers = {"Range": f"bytes={offset}-"} if offset else {}
    with requests.get(url, headers=headers, stream=True, timeout=(connect_timeout, read_timeout)) as response:
        response.raise_for_status()
        if offset and response.status_code != 206:
            offset = 0
        expected_size = _remote_size(response, offset)
        with temporary_path.open("ab" if offset else "wb") as destination:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    destination.write(chunk)
    if expected_size is not None and temporary_path.stat().st_size != expected_size:
        raise OSError(f"Incomplete download: {temporary_path.stat().st_size} bytes received; {expected_size} expected")


def prepare_source_zip(
    url: str,
    destination: Path,
    force: bool,
    retries: int,
    connect_timeout: int,
    read_timeout: int,
    chunk_size: int,
) -> dict[str, object]:
    """Download atomically or reuse a valid ZIP without loading it in memory."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not force:
        validate_zip(destination)
        downloaded = False
    else:
        temporary_path = destination.with_suffix(destination.suffix + ".part")
        if force:
            temporary_path.unlink(missing_ok=True)
        last_error: Exception | None = None
        for attempt in range(1, retries + 1):
            try:
                _download_once(url, temporary_path, connect_timeout, read_timeout, chunk_size)
                validate_zip(temporary_path)
                temporary_path.replace(destination)
                downloaded = True
                break
            except (OSError, ValueError, requests.RequestException) as exc:
                last_error = exc
                if attempt < retries:
                    time.sleep(min(attempt * 5, 30))
        else:
            raise RuntimeError(f"Download failed after {retries} attempts") from last_error

    stat = destination.stat()
    return {
        "url": url,
        "zip_path": str(destination),
        "zip_size_bytes": stat.st_size,
        "zip_sha256": sha256_file(destination),
        "downloaded_this_run": downloaded,
        "downloaded_at": (
            datetime.now().astimezone() if downloaded else datetime.fromtimestamp(stat.st_mtime).astimezone()
        ).isoformat(),
    }


def identify_tiff_member(zip_path: Path, expected_member: str | None = None) -> zipfile.ZipInfo:
    with zipfile.ZipFile(zip_path) as archive:
        candidates = [
            member
            for member in archive.infolist()
            if not member.is_dir() and Path(member.filename).suffix.lower() in {".tif", ".tiff"}
        ]
    if not candidates:
        raise ValueError("Source ZIP does not contain a TIFF")
    if len(candidates) != 1:
        names = [member.filename for member in candidates]
        raise ValueError(f"Source ZIP has an ambiguous TIFF inventory: {names}")
    if expected_member is not None and candidates[0].filename.replace("\\", "/") != expected_member:
        raise ValueError(
            f"Source TIFF member does not match the CEM 4.0 contract: "
            f"expected {expected_member}, found {candidates[0].filename}"
        )
    return candidates[0]


def extract_tiff_member(zip_path: Path, member: zipfile.ZipInfo, output_dir: Path) -> Path:
    """Extract only the selected TIFF by streaming to disk; never mutate a reused source."""
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / Path(member.filename).name
    if destination.exists():
        if destination.stat().st_size != member.file_size:
            raise ValueError(f"Existing extracted TIFF has unexpected size: {destination}")
        return destination

    temporary_path = destination.with_suffix(destination.suffix + ".part")
    temporary_path.unlink(missing_ok=True)
    with zipfile.ZipFile(zip_path) as archive, archive.open(member) as source, temporary_path.open("wb") as output:
        shutil.copyfileobj(source, output, length=1024 * 1024)
    if temporary_path.stat().st_size != member.file_size:
        temporary_path.unlink(missing_ok=True)
        raise OSError("Extracted TIFF size does not match ZIP inventory")
    temporary_path.replace(destination)
    destination.chmod(0o444)
    return destination
