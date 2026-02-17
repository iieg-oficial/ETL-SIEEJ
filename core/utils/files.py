import os
import glob
import shutil
from pathlib import Path
from datetime import datetime

from core.utils.logger import get_console_logger

logger = get_console_logger(__name__)


def cleanup_pipeline_data(pipeline_name: str) -> None:
    data_dir = Path("data")
    for stage_dir in data_dir.iterdir():
        pipeline_dir = stage_dir / pipeline_name
        if pipeline_dir.exists() and pipeline_dir.is_dir():
            shutil.rmtree(pipeline_dir)
            logger.info(f"Cleaned {pipeline_dir}")

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
