"""Download dataset uploads that dependencies submit through the SIEEJ form.

Every submission lands under the folder of the person who sent it, so a
dependency's history is spread across many folders and the file name changes on
each upload. The `envio.json` next to each upload carries the dependency name,
the submission state, the reporting dates and the exact object key, which is why
discovery goes through it instead of through the object paths.

A submitter can replace a file before sending, which leaves several objects for
the same form field. Only the newest one per field is returned.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import boto3

from core.acervo.config import settings
from core.acervo.constants import (
    CONJUNTO_PATH,
    DATA_FIELD,
    DATASETS_FIELD,
    DEPENDENCIA_PATH,
    ESTADO_ENVIADO,
    FECHA_ACTUALIZACION_FIELD,
    FECHA_CORTE_FIELD,
)
from core.utils.logger import get_console_logger
from core.utils.normalize import strip_accents

logger = get_console_logger(__name__)

FIELD_INDEX = re.compile(rf"{DATASETS_FIELD}\[(\d+)\]")


@dataclass(frozen=True)
class Upload:
    """One file submitted by a dependency, with the metadata of its dataset."""

    object_key: str
    filename: str
    size: int
    uploaded_at: str
    envio: str
    envio_id: int
    conjunto: str
    updated_at: str
    field_path: str
    fecha_corte: str
    fecha_actualizacion: str
    etag: str

    @property
    def etag_is_md5(self) -> bool:
        """False for multipart uploads, whose ETag is not the content MD5."""
        return bool(self.etag) and "-" not in self.etag


def normalize(text: str) -> str:
    """Strip accents and case so free-text form values compare reliably.

    Keeps spaces, unlike `normalize_text`, since dependency names are compared
    as written in the form.
    """
    return " ".join(strip_accents(str(text)).lower().split())


def get_client():
    """Build an S3 client against Acervo from the module settings."""
    return boto3.client(
        "s3",
        endpoint_url=settings.ACERVO_ENDPOINT,
        aws_access_key_id=settings.ACERVO_ACCESS_KEY,
        aws_secret_access_key=settings.ACERVO_SECRET_KEY,
        region_name=settings.ACERVO_REGION,
    )


def _scan_prefix(client, bucket: str, prefix: str, envio_filename: str) -> tuple[list[str], dict[str, str]]:
    """Return the envio.json keys and a key to ETag map, in a single pass."""
    paginator = client.get_paginator("list_objects_v2")
    envios: list[str] = []
    etags: dict[str, str] = {}

    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            etags[obj["Key"]] = obj.get("ETag", "").strip('"')
            if obj["Key"].endswith(f"/{envio_filename}"):
                envios.append(obj["Key"])

    return envios, etags


def _dig(payload: dict, path: tuple[str, ...]) -> str:
    node = payload
    for step in path:
        node = node.get(step, {}) if isinstance(node, dict) else ""
    return node if isinstance(node, str) else ""


def _dataset_block(envio: dict, field_path: str) -> dict:
    """Return the conunto_datos entry that owns a given form field."""
    match = FIELD_INDEX.search(field_path)
    blocks = envio.get("datos", {}).get(DATASETS_FIELD, [])
    if not match or not isinstance(blocks, list):
        return {}
    index = int(match.group(1))
    return blocks[index] if index < len(blocks) else {}


def list_uploads(
    dependencia: str,
    client=None,
    bucket: str | None = None,
    prefix: str | None = None,
    estado: str = ESTADO_ENVIADO,
) -> list[Upload]:
    """Return a dependency's submitted uploads, oldest first.

    Drafts are skipped: only submissions whose state matches `estado` are read.
    When a form field holds several objects, only the newest one is returned.

    Args:
        dependencia: dependency name as captured in the form, accents optional.
        client: S3 client; built from settings when omitted.
        bucket: bucket holding the submissions; defaults to the configured one.
        prefix: form prefix to scan; defaults to the configured one.
        estado: submission state to accept; pass None to accept every state.
    """
    client = client or get_client()
    bucket = bucket or settings.ACERVO_BUCKET
    prefix = prefix or settings.ACERVO_FORM_PREFIX
    envio_filename = settings.ACERVO_ENVIO_FILENAME
    target = normalize(dependencia)

    envio_keys, etags = _scan_prefix(client, bucket, prefix, envio_filename)

    newest: dict[tuple[str, str], Upload] = {}
    for key in envio_keys:
        envio = json.loads(client.get_object(Bucket=bucket, Key=key)["Body"].read())
        meta = envio.get("envio", {})
        if estado and meta.get("estado") != estado:
            continue
        if normalize(_dig(envio, DEPENDENCIA_PATH)) != target:
            continue

        folder = key.removeprefix(prefix).removesuffix(f"/{envio_filename}")
        for archivo in envio.get("archivos", []):
            field_path = archivo.get("field_path", "")
            if DATA_FIELD not in field_path:
                continue

            block = _dataset_block(envio, field_path)
            upload = Upload(
                object_key=archivo["object_key"],
                filename=archivo["filename_original"],
                size=archivo["size_bytes"],
                uploaded_at=archivo["subido_en"],
                envio=folder,
                envio_id=meta.get("id"),
                conjunto=_dig(envio, CONJUNTO_PATH),
                updated_at=meta.get("actualizado_en", ""),
                field_path=field_path,
                fecha_corte=str(block.get(FECHA_CORTE_FIELD, "")),
                fecha_actualizacion=str(block.get(FECHA_ACTUALIZACION_FIELD, "")),
                etag=etags.get(archivo["object_key"], ""),
            )
            slot = (folder, field_path)
            current = newest.get(slot)
            if current is None or upload.uploaded_at > current.uploaded_at:
                if current is not None:
                    logger.info(f"[acervo] {folder}: '{field_path}' replaced by a newer file")
                newest[slot] = upload

    uploads = sorted(newest.values(), key=lambda upload: upload.uploaded_at)
    for upload in uploads:
        if upload.fecha_corte and upload.fecha_corte > upload.uploaded_at[:10]:
            logger.warning(
                f"[acervo] envio {upload.envio_id}: fecha_corte {upload.fecha_corte} "
                f"is later than the upload date {upload.uploaded_at[:10]}"
            )
        if not upload.etag_is_md5:
            logger.warning(f"[acervo] envio {upload.envio_id}: ETag is not a content MD5, use the watermark instead")

    logger.info(f"[acervo] {len(uploads)} upload(s) found for '{dependencia}'")
    return uploads


def download(
    upload: Upload,
    output_folder: Path,
    client=None,
    bucket: str | None = None,
) -> Path:
    """Download one upload, keeping the object key file name."""
    client = client or get_client()
    bucket = bucket or settings.ACERVO_BUCKET

    output_folder.mkdir(parents=True, exist_ok=True)
    target = output_folder / Path(upload.object_key).name

    logger.info(f"[acervo] downloading {upload.filename} -> {target}")
    client.download_file(bucket, upload.object_key, str(target))
    return target


def download_all(
    dependencia: str,
    output_folder: Path,
    client=None,
    bucket: str | None = None,
    since: str | None = None,
) -> list[Path]:
    """Download a dependency's uploads, oldest first.

    Args:
        since: when given, only submissions updated after this `updated_at` are
            pulled, which is how an incremental run skips what bootstrap took.
    """
    client = client or get_client()
    bucket = bucket or settings.ACERVO_BUCKET

    uploads = list_uploads(dependencia, client=client, bucket=bucket)
    if since:
        uploads = [upload for upload in uploads if upload.updated_at > since]

    if not uploads:
        logger.warning(f"[acervo] nothing to download for '{dependencia}'")
        return []

    return [download(upload, output_folder, client=client, bucket=bucket) for upload in uploads]
