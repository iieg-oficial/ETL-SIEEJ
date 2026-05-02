import io
import zipfile

import requests


def fetch_zip(url: str, timeout: int = 120) -> zipfile.ZipFile:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(response.content))
