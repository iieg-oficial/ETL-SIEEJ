from __future__ import annotations

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
    url_fuente: str,
    temporary: Path,
    connect_timeout: int,
    read_timeout: int,
) -> int:
    offset = temporary.stat().st_size if temporary.exists() else 0
    headers = {"Range": f"bytes={offset}-"} if offset else {}

    with requests.get(url_fuente, headers=headers, stream=True, timeout=(connect_timeout, read_timeout)) as response:
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
    url_fuente: str,
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
            _download_attempt(url_fuente, temporary, connect_timeout, read_timeout)
            validate_zip(temporary)
            temporary.replace(destination)
            return True
        except (requests.RequestException, OSError, ValueError) as exc:
            last_error = exc
            logger.warning("[source] Download attempt failed: %s", exc)
            if attempt < retries:
                time.sleep(min(5 * attempt, 30))

    raise RuntimeError(f"Download failed after {retries} attempts") from last_error


def _source_filename(url_fuente: str) -> str:
    return Path(urlparse(url_fuente).path).name or "source.zip"


def prepare_source_zip(
    url_fuente: str,
    raw_dir: Path,
    force_download: bool,
    retries: int,
    connect_timeout: int,
    read_timeout: int,
) -> dict[str, object]:
    raw_dir.mkdir(parents=True, exist_ok=True)

    destination = raw_dir / _source_filename(url_fuente)
    downloaded = _download_zip(
        url_fuente,
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
        "url_fuente": url_fuente,
        "zip_path": str(destination),
        "zip_size_bytes": stat.st_size,
        "sha256_archivo_fuente": sha256_file(destination),
        "downloaded_at": timestamp,
        "downloaded_this_run": downloaded,
    }
