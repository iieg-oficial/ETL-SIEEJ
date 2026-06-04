import os
import io
from pathlib import Path

import requests


SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def download_public_file(file_id: str, dest_path: Path, timeout: int = 30) -> Path:
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_bytes(response.content)
    return dest_path


def _build_service(client_email: str, private_key: str):
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    credentials = service_account.Credentials.from_service_account_info(
        {
            "type": "service_account",
            "client_email": client_email,
            "private_key": private_key,
            "token_uri": "https://oauth2.googleapis.com/token",
        },
        scopes=SCOPES,
    )
    return build("drive", "v3", credentials=credentials)


def _list_files(service, folder_id: str):
    query = f"'{folder_id}' in parents"
    results = (
        service.files()
        .list(
            q=query,
            fields="files(id, name, mimeType)",
            pageSize=1000,
        )
        .execute()
    )
    return results.get("files", [])


def _download_file(service, file_id: str, file_name: str, destination: str) -> str:
    from googleapiclient.http import MediaIoBaseDownload

    request = service.files().get_media(fileId=file_id)
    file_path = os.path.join(destination, file_name)

    fh = io.FileIO(file_path, "wb")
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    return file_path


def download_folder(folder_id: str, output_folder: str, client_email: str, private_key: str) -> str:
    os.makedirs(output_folder, exist_ok=True)
    service = _build_service(client_email, private_key)
    files = _list_files(service, folder_id)

    for file in files:
        if "application/vnd.google-apps" not in file["mimeType"]:
            _download_file(service, file["id"], file["name"], output_folder)

    return output_folder
