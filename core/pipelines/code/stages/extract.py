from collections.abc import Iterable
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.acervo import Upload, download, list_uploads
from core.pipelines.code.config import settings
from core.pipelines.code.constants import (
    EXTRACT_DIRNAME,
    MANIFEST_FILENAME,
    PIPELINE_NAME,
    SHEET_ACTIVIDADES,
    SHEET_PUNTOS,
    UPLOAD_FIELD,
    XLSX_GLOB,
)
from core.pipelines.stage import Stage
from core.utils.files import safe_extract_zip, validate_zip, write_json_atomic
from core.utils.logger import get_logger


class CodeExtract(Stage):
    def __init__(self, mode: str = "bootstrap", since: str | None = None, processed_etags: Iterable[str] = ()):
        """
        Args:
            mode: `bootstrap` requires an upload; `update` only takes a new one.
            since: watermark, the `actualizado_en` of the last processed envio.
            processed_etags: loaded etags, to skip a resubmission whose file did not change.
        """
        super().__init__(PIPELINE_NAME, "extract")
        self.mode = mode
        self.since = since
        self.processed_etags = frozenset(processed_etags)
        self.logger = get_logger(f"{PIPELINE_NAME}.extract")

    def _is_new(self, upload: Upload) -> bool:
        """True when an update run still has to process this upload."""
        if self.since and upload.updated_at <= self.since:
            return False

        if upload.etag and upload.etag in self.processed_etags:
            self.logger.info(f"[source] envio {upload.envio_id}: unchanged file, skipped")
            return False

        return True

    def source(self, input_data: Optional[Any] = None) -> Upload | None:
        self.logger.info(f"[source] Listing uploads for '{settings.DEPENDENCIA}' in {self.mode} mode")
        uploads = list_uploads(settings.DEPENDENCIA, field=UPLOAD_FIELD)

        if self.mode == "update":
            uploads = [upload for upload in uploads if self._is_new(upload)]

        if not uploads:
            if self.mode == "bootstrap":
                raise ValueError(f"No uploads found for '{settings.DEPENDENCIA}'")
            return None

        # Each submission is the full dataset, so only the newest one is loaded.
        return max(uploads, key=lambda upload: upload.uploaded_at)

    def _read_sheets(self, path: Path) -> dict[str, pd.DataFrame]:
        """The upload is a ZIP holding the spreadsheet with the data and its catalog."""
        validate_zip(path)
        extract_dir = safe_extract_zip(path, self.work_dir / EXTRACT_DIRNAME, force=True)

        sheets = sorted(Path(extract_dir).rglob(XLSX_GLOB))
        if not sheets:
            raise FileNotFoundError(f"No .xlsx inside {path.name}")

        return pd.read_excel(sheets[0], sheet_name=[SHEET_PUNTOS, SHEET_ACTIVIDADES])

    def action(self, input_data: Upload | None) -> dict[str, Any]:
        if input_data is None:
            self.logger.info("[action] Nothing new to extract")
            return {"frames": {}, "upload": None}

        path = download(input_data, self.work_dir)
        frames = self._read_sheets(path)
        for sheet, df in frames.items():
            self.logger.info(f"[action] {sheet}: {len(df):,} rows read from {input_data.filename}")

        return {"frames": frames, "upload": input_data}

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        for sheet, df in input_data["frames"].items():
            df.to_pickle(self.work_dir / f"{sheet}.pkl")
            self.logger.info(f"[finalization] {sheet}: {len(df):,} rows saved")

        upload = input_data["upload"]
        manifest = (
            {
                "envio_id": upload.envio_id,
                "conjunto": upload.conjunto,
                "object_key": upload.object_key,
                "etag": upload.etag,
                "actualizado_en": upload.updated_at,
            }
            if upload
            else {}
        )
        write_json_atomic(manifest, self.work_dir / MANIFEST_FILENAME)
        self.logger.info(f"[finalization] manifest written for {len(manifest)} upload(s)")

        return input_data
