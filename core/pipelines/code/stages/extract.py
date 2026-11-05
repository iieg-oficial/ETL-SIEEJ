from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.acervo import Upload, download, list_uploads
from core.pipelines.code.config import settings
from core.pipelines.code.constants import MANIFEST_FILENAME, PIPELINE_NAME
from core.pipelines.code.datasets import BY_KEY, DATASETS, RETO, Dataset
from core.pipelines.code.helpers.sources import read_geo_zip, read_reto_zip
from core.pipelines.stage import Stage
from core.utils.files import safe_extract_zip, validate_zip, write_json_atomic
from core.utils.logger import get_logger


class CodeExtract(Stage):
    def __init__(
        self,
        mode: str = "bootstrap",
        since: Mapping[str, str] | None = None,
        processed_etags: Iterable[str] = (),
    ):
        """
        Args:
            mode: `bootstrap` requires an upload; `update` only takes new ones.
            since: watermark per dataset key, the `actualizado_en` of its last processed envio.
            processed_etags: loaded etags, to skip a resubmission whose file did not change.
        """
        super().__init__(PIPELINE_NAME, "extract")
        self.mode = mode
        self.since = dict(since or {})
        self.processed_etags = frozenset(processed_etags)
        self.logger = get_logger(f"{PIPELINE_NAME}.extract")

    def _parse_timestamp(self, value: str, envio_id: int) -> pd.Timestamp:
        timestamp = pd.to_datetime(value, utc=True) if value else pd.NaT
        if pd.isna(timestamp):
            raise ValueError(f"envio {envio_id} has no valid actualizado_en")
        return timestamp

    def _is_new(self, upload: Upload, dataset: str = RETO) -> bool:
        """True when an update run still has to process this upload."""
        since = self.since.get(dataset)
        if since and self._parse_timestamp(upload.updated_at, upload.envio_id) <= pd.to_datetime(since, utc=True):
            return False

        if upload.etag and upload.etag in self.processed_etags:
            self.logger.info(f"[source] envio {upload.envio_id}: unchanged file, skipped")
            return False

        return True

    def _belongs_to(self, upload: Upload, dataset: Dataset) -> bool:
        """The form numbers datasets by position, so the name is what identifies one."""
        return dataset.field in upload.field_path and dataset.accepts(upload.dataset_name)

    def source(self, input_data: Optional[Any] = None) -> dict[str, Upload]:
        self.logger.info(f"[source] Listing uploads for '{settings.DEPENDENCIA}' in {self.mode} mode")
        uploads = [
            upload
            for field in sorted({dataset.field for dataset in DATASETS})
            for upload in list_uploads(settings.DEPENDENCIA, field=field)
        ]

        for name in sorted({u.dataset_name for u in uploads if not any(d.accepts(u.dataset_name) for d in DATASETS)}):
            self.logger.warning(f"[source] Unknown dataset name '{name}', skipped")

        selected: dict[str, Upload] = {}
        missing = []
        for dataset in DATASETS:
            candidates = [upload for upload in uploads if self._belongs_to(upload, dataset)]
            if not candidates:
                missing.append(dataset.key)
                self.logger.warning(f"[source] {dataset.key}: no upload found in the form")
            if self.mode == "update":
                candidates = [upload for upload in candidates if self._is_new(upload, dataset.key)]
            if not candidates:
                self.logger.info(f"[source] {dataset.key}: nothing to extract")
                continue

            # Each submission is the full dataset, so only the newest one is loaded.
            newest = max(candidates, key=lambda upload: upload.uploaded_at)
            self._parse_timestamp(newest.updated_at, newest.envio_id)
            selected[dataset.key] = newest

        if missing and self.mode == "bootstrap":
            raise ValueError(f"No uploads found for '{settings.DEPENDENCIA}' for datasets: {missing}")

        self.logger.info(f"[source] Selected datasets: {sorted(selected)}")
        return selected

    def _read_frames(self, dataset: str, path: Path) -> dict[str, pd.DataFrame]:
        """The upload is a ZIP holding the data and its catalogs."""
        validate_zip(path)
        extract_dir = Path(safe_extract_zip(path, self.work_dir / dataset / "raw", force=True))
        reader = read_reto_zip if dataset == RETO else read_geo_zip
        return reader(extract_dir)

    def action(self, input_data: dict[str, Upload]) -> dict[str, dict[str, Any]]:
        if not input_data:
            self.logger.info("[action] Nothing new to extract")
            return {}

        extracted = {}
        for key, upload in input_data.items():
            path = download(upload, self.work_dir / key)
            frames = self._read_frames(key, path)
            for name, df in frames.items():
                self.logger.info(f"[action] {key}/{name}: {len(df):,} rows read from {upload.filename}")
            extracted[key] = {"frames": frames, "upload": upload}

        return extracted

    def finalization(self, input_data: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        manifest = {}
        for key, entry in input_data.items():
            folder = self.work_dir / key
            folder.mkdir(parents=True, exist_ok=True)
            for name, df in entry["frames"].items():
                df.to_pickle(folder / f"{name}.pkl")
                self.logger.info(f"[finalization] {key}/{name}: {len(df):,} rows saved")

            upload = entry["upload"]
            manifest[key] = {
                "envio_id": upload.envio_id,
                "conjunto": BY_KEY[key].label,
                "object_key": upload.object_key,
                "etag": upload.etag,
                "actualizado_en": upload.updated_at,
            }

        write_json_atomic(manifest, self.work_dir / MANIFEST_FILENAME)
        self.logger.info(f"[finalization] manifest written for {len(manifest)} dataset(s)")

        return input_data
