from collections.abc import Iterable
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.acervo import Upload, download, list_uploads, normalize
from core.pipelines.secretaria_educacion.config import settings
from core.pipelines.secretaria_educacion.constants import (
    DATASET_PREFIXES,
    DIRECTORIO_DATASET,
    DIRECTORIO_HEADER_ROW,
    MANIFEST_FILENAME,
    PIPELINE_NAME,
)
from core.pipelines.stage import Stage
from core.utils.files import safe_extract_zip, validate_zip, write_json_atomic
from core.utils.logger import get_logger


class SecretariaEducacionExtract(Stage):
    def __init__(self, mode: str = "bootstrap", since: str | None = None, processed_etags: Iterable[str] = ()):
        """
        Args:
            mode: `bootstrap` toma todo el histórico; `update` solo lo nuevo.
            since: watermark, el `actualizado_en` del último envío procesado.
            processed_etags: etags ya cargados, para saltar envíos que se
                reenviaron sin que el archivo cambiara.
        """
        super().__init__(PIPELINE_NAME, "extract")
        self.mode = mode
        self.since = since
        self.processed_etags = frozenset(processed_etags)
        self.logger = get_logger(f"{PIPELINE_NAME}.extract")

    def _resolve_dataset(self, conjunto: str) -> str | None:
        """Route a submitted dataset name to its handler key.

        Matching is by prefix because the form captures the name as free text and
        the school cycle often trails it.
        """
        target = normalize(conjunto)
        for prefix, dataset in DATASET_PREFIXES.items():
            if target.startswith(prefix):
                return dataset
        return None

    def _is_new(self, upload: Upload) -> bool:
        """True when an update run still has to process this upload."""
        if self.since and upload.updated_at <= self.since:
            return False

        if upload.etag and upload.etag in self.processed_etags:
            self.logger.info(f"[source] envio {upload.envio_id}: unchanged file, skipped")
            return False

        return True

    def source(self, input_data: Optional[Any] = None) -> dict[str, Upload]:
        self.logger.info(f"[source] Listing uploads for '{settings.DEPENDENCIA}' in {self.mode} mode")
        uploads = list_uploads(settings.DEPENDENCIA)

        if self.mode == "update":
            uploads = [upload for upload in uploads if self._is_new(upload)]

        resolved: dict[str, Upload] = {}
        for upload in uploads:
            dataset = self._resolve_dataset(upload.conjunto)
            if dataset is None:
                self.logger.warning(f"[source] Unknown dataset '{upload.conjunto}', skipped")
                continue

            previous = resolved.get(dataset)
            if previous is None or upload.fecha_corte > previous.fecha_corte:
                resolved[dataset] = upload

        if not resolved and self.mode == "bootstrap":
            raise ValueError(f"No known datasets found for '{settings.DEPENDENCIA}'")

        self.logger.info(f"[source] Resolved datasets: {sorted(resolved)}")
        return resolved

    def _read_directorio(self, path: Path) -> pd.DataFrame:
        """The directory ships as a ZIP holding a single spreadsheet."""
        validate_zip(path)
        extract_dir = safe_extract_zip(path, self.work_dir / DIRECTORIO_DATASET, force=True)

        sheets = sorted(Path(extract_dir).rglob("*.xlsx"))
        if not sheets:
            raise FileNotFoundError(f"No .xlsx inside {path.name}")

        return pd.read_excel(sheets[0], header=DIRECTORIO_HEADER_ROW)

    def _read_file(self, dataset: str, path: Path) -> pd.DataFrame:
        if dataset == DIRECTORIO_DATASET:
            return self._read_directorio(path)

        suffix = path.suffix.lower()
        if suffix == ".csv":
            return pd.read_csv(path, encoding="utf-8-sig")
        if suffix in {".xlsx", ".xls"}:
            return pd.read_excel(path)

        raise ValueError(f"Unsupported format '{suffix}' for dataset '{dataset}'")

    def action(self, input_data: dict[str, Upload]) -> dict[str, Any]:
        frames: dict[str, pd.DataFrame] = {}
        for dataset, upload in input_data.items():
            path = download(upload, self.work_dir)
            frames[dataset] = self._read_file(dataset, path)
            self.logger.info(f"[action] {dataset}: {len(frames[dataset]):,} rows read from {upload.filename}")

        return {"frames": frames, "uploads": input_data}

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        for dataset, df in input_data["frames"].items():
            df.to_pickle(self.work_dir / f"{dataset}.pkl")
            self.logger.info(f"[finalization] {dataset}: {len(df):,} rows saved")

        manifest = {
            dataset: {
                "envio_id": upload.envio_id,
                "conjunto": upload.conjunto,
                "object_key": upload.object_key,
                "etag": upload.etag,
                "fecha_corte": upload.fecha_corte,
                "fecha_actualizacion": upload.fecha_actualizacion,
                "actualizado_en": upload.updated_at,
            }
            for dataset, upload in input_data["uploads"].items()
        }
        write_json_atomic(manifest, self.work_dir / MANIFEST_FILENAME)
        self.logger.info(f"[finalization] manifest written for {sorted(manifest)}")

        return input_data
