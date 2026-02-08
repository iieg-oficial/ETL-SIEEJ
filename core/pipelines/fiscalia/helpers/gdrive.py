import os
import gdown
from typing import Dict


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
