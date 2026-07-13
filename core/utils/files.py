import io
import os
import glob
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

import chardet
import pandas as pd
import requests

from core.utils.logger import get_console_logger

logger = get_console_logger(__name__)

_FALLBACK_ENCODINGS = ("utf-8", "latin-1", "cp1252", "iso-8859-1", "utf-16")


def detect_encoding(file_path: str, sample_size: int = 10000) -> str:
    """Detect file encoding using chardet, with fallback to common encodings on low confidence.

    Args:
        file_path: Path to the file.
        sample_size: Number of bytes to sample for detection.

    Returns:
        Detected encoding string, defaulting to 'utf-8'.
    """
    try:
        with open(file_path, "rb") as f:
            raw_data = f.read(sample_size)

        result = chardet.detect(raw_data)
        encoding = result["encoding"]
        confidence = result["confidence"]

        logger.info(f"Detected encoding: {encoding} (confidence: {confidence:.2%})")

        if confidence < 0.7:
            logger.info(f"Low confidence ({confidence:.2%}), trying common encodings...")
            for fallback in _FALLBACK_ENCODINGS:
                try:
                    with open(file_path, "r", encoding=fallback) as f:
                        f.read(1000)
                    logger.info(f"Using fallback encoding: {fallback}")
                    return fallback
                except UnicodeDecodeError:
                    continue

        return encoding if encoding else "utf-8"

    except OSError as e:
        logger.warning(f"Error detecting encoding for {file_path}: {e}, defaulting to utf-8")
        return "utf-8"


def fetch_zip(url: str, timeout: int = 120) -> zipfile.ZipFile:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(response.content))


def read_csv_from_zip_url(url: str, csv_path: str, **read_csv_kwargs) -> pd.DataFrame:
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        with z.open(csv_path) as f:
            return pd.read_csv(f, **read_csv_kwargs)


def load_csv_lookups(csv_path: str | Path, group_col: str, key_col: str, value_col: str) -> dict[str, dict[str, str]]:
    df = pd.read_csv(csv_path, dtype=str)
    return {group: dict(zip(sub[key_col], sub[value_col])) for group, sub in df.groupby(group_col)}


def cleanup_pipeline_data(pipeline_name: str) -> None:
    data_dir = Path("data")
    for stage_dir in data_dir.iterdir():
        pipeline_dir = stage_dir / pipeline_name
        if pipeline_dir.exists() and pipeline_dir.is_dir():
            # Tolerant: post-load housekeeping must never fail the pipeline
            # (e.g. a file vanishing under a concurrent run).
            shutil.rmtree(pipeline_dir, ignore_errors=True)
            logger.info(f"Cleaned {pipeline_dir}")


def clean_directory(directory: Path, log=None) -> None:
    """Elimina todos los archivos y subdirectorios dentro de *directory* sin borrar la carpeta."""
    if not directory.exists():
        return
    for item in directory.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
    msg = f"Limpieza completada: {directory}"
    if log:
        log.info(msg)
    else:
        logger.info(msg)


def parse_date_from_filename(filepath: str, extension: str) -> datetime | None:
    filename = os.path.basename(filepath)
    date_str = filename.replace(extension, "")
    try:
        return datetime.strptime(date_str, "%d-%m-%Y")
    except ValueError:
        return None


def get_files_by_extension(output_folder: str, extension: str) -> list[str]:
    files = glob.glob(os.path.join(output_folder, f"*{extension}"))
    if not files:
        raise FileNotFoundError(f"No {extension} file was found in {output_folder}")
    logger.info(f"Found {len(files)} {extension} files in {output_folder}")
    return files


def get_latest_file(output_folder: str, extension: str = ".xlsx") -> str:
    files = get_files_by_extension(output_folder, extension)
    valid_files = [f for f in files if parse_date_from_filename(f, extension) is not None]

    if not valid_files:
        raise FileNotFoundError(f"No files with date format dd-mm-yyyy found in {output_folder}")

    latest_file = max(valid_files, key=lambda f: parse_date_from_filename(f, extension))
    logger.info(f"Latest file: {os.path.basename(latest_file)}")
    return latest_file


def get_latest_files_per_year(output_folder: str, extension: str = ".xlsx") -> list[str]:
    files = get_files_by_extension(output_folder, extension)
    valid_files = [f for f in files if parse_date_from_filename(f, extension) is not None]

    if not valid_files:
        raise FileNotFoundError(f"No files with date format dd-mm-yyyy found in {output_folder}")

    files_by_year = {}
    for file in valid_files:
        date = parse_date_from_filename(file, extension)
        year = date.year
        if year not in files_by_year or date > parse_date_from_filename(files_by_year[year], extension):
            files_by_year[year] = file

    latest_files = [file for year, file in sorted(files_by_year.items())]
    for file in latest_files:
        logger.info(f"File: {os.path.basename(file)}")

    return latest_files


def get_file_by_name(output_folder: str, filename: str) -> str:
    filepath = os.path.join(output_folder, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filename} not found in {output_folder}")

    logger.info(f"File found: {filename}")
    return filepath
