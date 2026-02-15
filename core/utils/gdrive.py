import os
import gdown


def gdown_folder(folder_url: str, output_folder: str) -> str:
    os.makedirs(output_folder, exist_ok=True)
    gdown.download_folder(folder_url, output=output_folder, quiet=True)
    return output_folder
