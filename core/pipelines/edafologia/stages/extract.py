from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from core.pipelines.edafologia.config import settings
from core.pipelines.edafologia.constants import (
    BOUNDARIES_GPKG_FILENAME,
    CONTROLLED_CATALOG_METHODOLOGY,
    CONTROLLED_CATALOG_ORIGIN,
    CONTROLLED_CATALOG_PENDING_METADATA,
    CONTROLLED_CATALOG_FL_REFERENCE_PAGE,
    CONTROLLED_CATALOG_REFERENCE_DOCUMENT,
    CONTROLLED_CATALOG_REFERENCE_DOCUMENT_VERSION,
    CONTROLLED_CATALOG_REFERENCE_INSTITUTION,
    CONTROLLED_CATALOG_REFERENCE_SCALE,
    CONTROLLED_CATALOG_REFERENCE_YEAR,
    CONTROLLED_CATALOG_STATUS,
    CONTROLLED_CATALOG_VERSION,
    CONTROLLED_CATALOG_VERSION_DATE,
    EXPECTED_SOURCE_COLUMNS,
    MANIFEST_FILENAME,
    MUNICIPAL_BOUNDARY_SOURCES,
    PIPELINE_NAME,
    PIPELINE_VERSION,
    SOURCE_NAME,
    SOURCE_VERSION,
)
from core.pipelines.edafologia.helpers.archive import safe_extract_zip
from core.pipelines.edafologia.helpers.boundaries import prepare_municipal_boundaries
from core.pipelines.edafologia.helpers.download import prepare_source_zip
from core.pipelines.edafologia.helpers.inventory import inspect_vector_candidates, select_canonical_candidate
from core.pipelines.edafologia.helpers.manifest import read_manifest, write_manifest
from core.pipelines.edafologia.mappings import (
    CALIFICADORES_EDAFOLOGICOS,
    GRUPOS_EDAFOLOGICOS,
    catalog_manifest,
)
from core.pipelines.stage import Stage
from core.utils.logger import get_logger


class EdafologiaExtract(Stage):
    def __init__(self, pipeline_name: str = PIPELINE_NAME):
        super().__init__(pipeline_name, "extract")
        self.logger = get_logger(f"{pipeline_name}.extract")
        self.raw_dir = self.work_dir / "raw"
        self.extraction_dir = self.work_dir / "extracted"
        self.boundaries_path = self.work_dir / "auxiliary" / BOUNDARIES_GPKG_FILENAME
        self.manifest_path = self.work_dir / MANIFEST_FILENAME

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
        previous_manifest = read_manifest(self.manifest_path)
        previous_auxiliary = (previous_manifest or {}).get("auxiliary_inputs", {})
        auxiliary_inputs = {
            "municipal_boundaries": prepare_municipal_boundaries(
                database_url=settings.cvegeo_database_url,
                database_name=settings.CVEGEO_DB_NAME,
                output_path=self.boundaries_path,
                boundary_sources=MUNICIPAL_BOUNDARY_SOURCES,
                previous_manifest=previous_auxiliary.get("municipal_boundaries"),
                force=settings.FORCE_DOWNLOAD,
            ),
        }
        controlled_catalogs = {
            "metadata": {
                "origin_type": CONTROLLED_CATALOG_ORIGIN,
                "version": CONTROLLED_CATALOG_VERSION,
                "version_date": CONTROLLED_CATALOG_VERSION_DATE,
                "methodology": CONTROLLED_CATALOG_METHODOLOGY,
                "reference_institution": CONTROLLED_CATALOG_REFERENCE_INSTITUTION,
                "reference_document": CONTROLLED_CATALOG_REFERENCE_DOCUMENT,
                "reference_scale": CONTROLLED_CATALOG_REFERENCE_SCALE,
                "reference_document_version": CONTROLLED_CATALOG_REFERENCE_DOCUMENT_VERSION,
                "reference_year": CONTROLLED_CATALOG_REFERENCE_YEAR,
                "fl_reference_page": CONTROLLED_CATALOG_FL_REFERENCE_PAGE,
                "status": CONTROLLED_CATALOG_STATUS,
                "pending_metadata": CONTROLLED_CATALOG_PENDING_METADATA,
            },
            "grupo1": catalog_manifest(GRUPOS_EDAFOLOGICOS, CONTROLLED_CATALOG_VERSION),
            "calificadores": catalog_manifest(CALIFICADORES_EDAFOLOGICOS, CONTROLLED_CATALOG_VERSION),
        }

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
            "auxiliary_inputs": auxiliary_inputs,
            "controlled_catalogs": controlled_catalogs,
            "pipeline_version": PIPELINE_VERSION,
            "manifest_created_at": datetime.now().astimezone().isoformat(),
        }
        return manifest

    def finalization(self, input_data: dict[str, object]) -> dict[str, object]:
        write_manifest(input_data, self.manifest_path)
        self.logger.info("[finalization] Extract manifest written to %s", self.manifest_path)
        return input_data
