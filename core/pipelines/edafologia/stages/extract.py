from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from core.pipelines.edafologia.config import settings
from core.pipelines.edafologia.constants import (
    EXPECTED_SOURCE_COLUMNS,
    MANIFEST_FILENAME,
    PIPELINE_NAME,
    PIPELINE_VERSION,
    SOURCE_NAME,
    SOURCE_VERSION,
)
from core.pipelines.edafologia.helpers.archive import safe_extract_zip
from core.pipelines.edafologia.helpers.download import prepare_source_zip
from core.pipelines.edafologia.helpers.inventory import inspect_vector_candidates, select_canonical_candidate
from core.pipelines.edafologia.helpers.manifest import write_manifest
from core.pipelines.stage import Stage
from core.utils.logger import get_logger


class EdafologiaExtract(Stage):
    def __init__(self, pipeline_name: str = PIPELINE_NAME):
        super().__init__(pipeline_name, "extract")
        self.logger = get_logger(f"{pipeline_name}.extract")
        self.raw_dir = self.work_dir / "raw"
        self.extraction_dir = self.work_dir / "extracted"

    def source(self, input_data: Any | None = None) -> dict[str, object]:
        self.logger.info("[source] Preparing Edafologia source ZIP")
        return prepare_source_zip(
            source_url=settings.SOURCE_URL,
            raw_dir=self.raw_dir,
            source_zip_path=settings.SOURCE_ZIP_PATH,
            force_download=settings.FORCE_DOWNLOAD,
            retries=settings.DOWNLOAD_RETRIES,
            connect_timeout=settings.DOWNLOAD_CONNECT_TIMEOUT,
            read_timeout=settings.DOWNLOAD_READ_TIMEOUT,
            logger=self.logger,
        )

    def action(self, input_data: dict[str, object]) -> dict[str, object]:
        zip_path = Path(str(input_data["zip_path"]))
        self.logger.info("[action] Extracting and inventorying %s", zip_path.name)
        safe_extract_zip(zip_path, self.extraction_dir, force=settings.FORCE_DOWNLOAD, logger=self.logger)
        candidates = inspect_vector_candidates(self.extraction_dir, EXPECTED_SOURCE_COLUMNS)
        selected = select_canonical_candidate(candidates, EXPECTED_SOURCE_COLUMNS)

        manifest = {
            "source_url": input_data["source_url"],
            "source_name": SOURCE_NAME,
            "source_version": settings.SOURCE_VERSION or SOURCE_VERSION,
            "downloaded_at": input_data["downloaded_at"],
            "zip_path": input_data["zip_path"],
            "zip_size_bytes": input_data["zip_size_bytes"],
            "source_file_sha256": input_data["source_file_sha256"],
            "extraction_directory": str(self.extraction_dir),
            "inventory": candidates,
            "selected_path": str(self.extraction_dir / str(selected["relative_path"])),
            "selected_layer": selected["layer"],
            "selected_geometry_type": selected["geometry_type"],
            "selected_crs": selected["crs"],
            "selected_feature_count": selected["feature_count"],
            "selected_fields": selected["fields"],
            "pipeline_version": PIPELINE_VERSION,
            "manifest_created_at": datetime.now().astimezone().isoformat(),
        }
        return manifest

    def finalization(self, input_data: dict[str, object]) -> dict[str, object]:
        manifest_path = self.work_dir / MANIFEST_FILENAME
        write_manifest(input_data, manifest_path)
        self.logger.info("[finalization] Extract manifest written to %s", manifest_path)
        return input_data
