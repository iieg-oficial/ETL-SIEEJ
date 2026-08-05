from __future__ import annotations

import shutil
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests

from core.utils.files import sha256_file, validate_zip
from core.utils.logger import get_console_logger

logger = get_console_logger(__name__)


def _expected_total_size(response: requests.Response, offset: int) -> int | None:
    content_range = response.headers.get("Content-Range")
    if content_range and "/" in content_range:
        total = content_range.rsplit("/", 1)[-1]
        if total.isdigit():
            return int(total)
    content_length = response.headers.get("Content-Length")
    if content_length and content_length.isdigit():
        return offset + int(content_length)
    return None


def _download_attempt(
    source_url: str,
    temporary: Path,
    connect_timeout: int,
    read_timeout: int,
) -> int:
    offset = temporary.stat().st_size if temporary.exists() else 0
    headers = {"Range": f"bytes={offset}-"} if offset else {}

    with requests.get(source_url, headers=headers, stream=True, timeout=(connect_timeout, read_timeout)) as response:
        response.raise_for_status()
        if offset and response.status_code != 206:
            logger.warning("[source] Server ignored Range; restarting temporary download")
            offset = 0
        expected_size = _expected_total_size(response, offset)
        mode = "ab" if offset else "wb"
        with temporary.open(mode) as output:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    output.write(chunk)

    actual_size = temporary.stat().st_size
    if expected_size is not None and actual_size != expected_size:
        raise OSError(f"Incomplete download: received {actual_size} bytes of {expected_size}")
    return actual_size


def _download_zip(
    source_url: str,
    destination: Path,
    force: bool,
    retries: int,
    connect_timeout: int,
    read_timeout: int,
) -> bool:
    if destination.exists() and not force:
        validate_zip(destination)
        logger.info("[source] Reusing valid ZIP: %s", destination)
        return False

    temporary = destination.with_suffix(destination.suffix + ".part")
    if force:
        temporary.unlink(missing_ok=True)

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            logger.info("[source] Download attempt %s/%s", attempt, retries)
            _download_attempt(source_url, temporary, connect_timeout, read_timeout)
            validate_zip(temporary)
            temporary.replace(destination)
            return True
        except (requests.RequestException, OSError, ValueError) as exc:
            last_error = exc
            logger.warning("[source] Download attempt failed: %s", exc)
            if attempt < retries:
                time.sleep(min(5 * attempt, 30))

    raise RuntimeError(f"Download failed after {retries} attempts") from last_error


def _source_filename(source_url: str) -> str:
    return Path(urlparse(source_url).path).name or "source.zip"


def prepare_source_zip(
    source_url: str,
    raw_dir: Path,
    source_zip_path: str | None,
    force_download: bool,
    retries: int,
    connect_timeout: int,
    read_timeout: int,
) -> dict[str, object]:
    raw_dir.mkdir(parents=True, exist_ok=True)

    if source_zip_path:
        source_path = Path(source_zip_path).expanduser().resolve()
        if not source_path.exists():
            raise FileNotFoundError(f"Configured local ZIP does not exist: {source_path}")
        validate_zip(source_path)
        destination = raw_dir / source_path.name
        if destination.resolve() != source_path:
            if destination.exists():
                validate_zip(destination)
                if sha256_file(destination) != sha256_file(source_path):
                    if not force_download:
                        raise ValueError(f"Existing raw ZIP differs from configured local ZIP: {destination}")
                    shutil.copy2(source_path, destination)
            else:
                shutil.copy2(source_path, destination)
        downloaded = False
    else:
        destination = raw_dir / _source_filename(source_url)
        downloaded = _download_zip(
            source_url,
            destination,
            force_download,
            retries,
            connect_timeout,
            read_timeout,
        )

    validate_zip(destination)
    stat = destination.stat()
    timestamp = (
        datetime.now().astimezone().isoformat()
        if downloaded
        else datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat()
    )
    return {
        "source_url": source_url,
        "zip_path": str(destination),
        "zip_size_bytes": stat.st_size,
        "source_file_sha256": sha256_file(destination),
        "downloaded_at": timestamp,
        "downloaded_this_run": downloaded,
    }
