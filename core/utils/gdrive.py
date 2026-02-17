import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


def _build_service(client_email: str, private_key: str):
    credentials = service_account.Credentials.from_service_account_info(
        {
            "type": "service_account",
            "client_email": client_email,
            "private_key": private_key,
            "token_uri": "https://oauth2.googleapis.com/token",
        },
        scopes=SCOPES,
    )
    return build('drive', 'v3', credentials=credentials)


def _list_files(service, folder_id: str):
    query = f"'{folder_id}' in parents"
    results = service.files().list(
        q=query,
        fields="files(id, name, mimeType)",
        pageSize=1000,
    ).execute()
    return results.get('files', [])


def _download_file(service, file_id: str, file_name: str, destination: str) -> str:
    request = service.files().get_media(fileId=file_id)
    file_path = os.path.join(destination, file_name)

    fh = io.FileIO(file_path, 'wb')
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
        if 'application/vnd.google-apps' not in file['mimeType']:
            _download_file(service, file['id'], file['name'], output_folder)

    return output_folder
