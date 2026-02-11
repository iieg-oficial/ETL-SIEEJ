import os
import glob
import zipfile
import gdown
from typing import Dict

from core.utils.logger import get_logger

logger = get_logger("gdrive")


def download_files_from_folder(
    folder_url: str,
    output_folder: str,
    filenames: list[str]
) -> Dict[str, str]:

    os.makedirs(output_folder, exist_ok=True)
    gdown.download_folder(folder_url, output=output_folder, quiet=True)

    file_paths = {}
    for filename in filenames:
        filepath = os.path.join(output_folder, filename)
        if os.path.exists(filepath):
            file_paths[filename] = filepath
        else:
            raise FileNotFoundError(f"Archivo no encontrado: {filepath}")

    return file_paths


def download_and_unzip(folder_url: str, output_folder: str, extension: str = ".xlsx") -> str:
    os.makedirs(output_folder, exist_ok=True)
    gdown.download_folder(folder_url, output=output_folder, quiet=True)

    zip_files = glob.glob(os.path.join(output_folder, "*.zip"))
    if not zip_files:
        raise FileNotFoundError(f"No .zip file was found in {output_folder}")

    zip_path = zip_files[0]
    logger.info(f"📦 Unzipping {os.path.basename(zip_path)}")

    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(output_folder)

    extracted = glob.glob(os.path.join(output_folder, f"*{extension}"))
    if not extracted:
        raise FileNotFoundError(f"No {extension} was found inside the .zip")

    logger.info(f"📄 File found: {os.path.basename(extracted[0])}")
    return extracted[0]
