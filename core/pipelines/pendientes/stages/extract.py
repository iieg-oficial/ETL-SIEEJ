from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from core.pipelines.pendientes.config import settings
from core.pipelines.pendientes.constants import (
    EXTRACT_MANIFEST_FILENAME,
    PIPELINE_NAME,
    PIPELINE_VERSION,
    SOURCE_EDITION,
    SOURCE_ALLOWED_SRIDS,
    SOURCE_EXPECTED_BANDS,
    SOURCE_EXPECTED_DTYPE,
    SOURCE_EXPECTED_NODATA,
    SOURCE_EXPECTED_RESOLUTION_DEGREES,
    SOURCE_LINEAGE_INPUT,
    SOURCE_LINEAGE_OUTPUT,
    SOURCE_LINEAGE_REFERENCES,
    SOURCE_NAME,
    SOURCE_NOMINAL_RESOLUTION_M,
    SOURCE_PRODUCER,
    SOURCE_RESAMPLING_DOCUMENTED,
    SOURCE_RESOLUTION_ABS_TOLERANCE,
    SOURCE_TEMPORAL_COVERAGE,
    SOURCE_TIFF_FILENAME,
    SOURCE_TIFF_MEMBER,
    SOURCE_UPC,
    SOURCE_VERTICAL_QUANTITY,
    SOURCE_VERTICAL_UNIT,
)
from core.pipelines.pendientes.helpers.download import extract_tiff_member, identify_tiff_member, prepare_source_zip
from core.pipelines.pendientes.helpers.raster import inspect_raster, validate_source_contract
from core.pipelines.stage import Stage
from core.utils.files import sha256_file, write_json_atomic


class PendientesExtract(Stage):
    """Acquire, inventory, and validate the immutable CEM source."""

    def __init__(self, pipeline_name: str = PIPELINE_NAME, mode: str = "bootstrap") -> None:
        self.mode = mode
        super().__init__(pipeline_name, "extract")
        self.raw_dir = self.work_dir / "raw"
        self.source_dir = self.work_dir / "source"
        self.manifest_path = self.work_dir / EXTRACT_MANIFEST_FILENAME

    def source(self, input_data: Any | None = None) -> dict[str, object]:
        if settings.SOURCE_TIFF_PATH is not None:
            source_path = settings.SOURCE_TIFF_PATH.expanduser().resolve()
            if not source_path.is_file():
                raise FileNotFoundError(f"Configured SOURCE_TIFF_PATH does not exist: {source_path}")
            if source_path.name != SOURCE_TIFF_FILENAME:
                raise ValueError(f"Configured source must be named {SOURCE_TIFF_FILENAME}; found {source_path.name}")
            return {
                "acquisition_mode": "configured_local_tiff",
                "tiff_path": str(source_path),
                "tiff_size_bytes": source_path.stat().st_size,
                "tiff_sha256": sha256_file(source_path),
                "downloaded_this_run": False,
            }
        if not settings.SOURCE_URL:
            raise ValueError("Configure SOURCE_TIFF_PATH to reuse the CEM or SOURCE_URL to download it")
        return prepare_source_zip(
            url=settings.SOURCE_URL,
            destination=self.raw_dir / settings.SOURCE_ZIP_FILENAME,
            force=settings.FORCE_DOWNLOAD,
            retries=settings.DOWNLOAD_RETRIES,
            connect_timeout=settings.DOWNLOAD_CONNECT_TIMEOUT,
            read_timeout=settings.DOWNLOAD_READ_TIMEOUT,
            chunk_size=settings.DOWNLOAD_CHUNK_SIZE,
        )

    def action(self, input_data: dict[str, object]) -> dict[str, object]:
        if input_data.get("acquisition_mode") == "configured_local_tiff":
            tiff_path = Path(str(input_data["tiff_path"]))
            zip_inventory = None
        else:
            zip_path = Path(str(input_data["zip_path"]))
            member = identify_tiff_member(zip_path, expected_member=SOURCE_TIFF_MEMBER)
            tiff_path = extract_tiff_member(zip_path, member, self.source_dir)
            zip_inventory = {
                "selected_tiff_member": member.filename,
                "selected_tiff_size_bytes": member.file_size,
                "selected_tiff_crc32": f"{member.CRC:08x}",
            }
        metadata = inspect_raster(tiff_path, max_cells=settings.STATS_MAX_CELLS)
        validate_source_contract(
            metadata,
            expected_bands=SOURCE_EXPECTED_BANDS,
            allowed_srids=SOURCE_ALLOWED_SRIDS,
            expected_dtype=SOURCE_EXPECTED_DTYPE,
            expected_nodata=SOURCE_EXPECTED_NODATA,
            expected_pixel_size=SOURCE_EXPECTED_RESOLUTION_DEGREES,
            pixel_size_tolerance=SOURCE_RESOLUTION_ABS_TOLERANCE,
        )
        return {
            "source": {
                "producer": SOURCE_PRODUCER,
                "product": SOURCE_NAME,
                "role": "source_original",
                "scope": "national",
                "immutable": True,
                "upc": SOURCE_UPC,
                "edition": SOURCE_EDITION,
                "temporal_coverage": SOURCE_TEMPORAL_COVERAGE,
                "nominal_resolution_m": SOURCE_NOMINAL_RESOLUTION_M,
                "url": settings.SOURCE_URL,
                "vertical_quantity": SOURCE_VERTICAL_QUANTITY,
                "vertical_unit": SOURCE_VERTICAL_UNIT,
                "vertical_unit_evidence": "confirmación documental complementaria; GeoTIFF unit es nulo",
                "documented_resampling": SOURCE_RESAMPLING_DOCUMENTED,
                "institutional_lineage": {
                    "operation": "Resample",
                    "input": SOURCE_LINEAGE_INPUT,
                    "output": SOURCE_LINEAGE_OUTPUT,
                    "method": SOURCE_RESAMPLING_DOCUMENTED,
                    "related_intermediates": list(SOURCE_LINEAGE_REFERENCES),
                    "internal_workstation_paths_are_nonfunctional_metadata": True,
                },
            },
            "acquisition": input_data,
            "zip_inventory": zip_inventory,
            "tiff_path": str(tiff_path),
            "tiff_size_bytes": tiff_path.stat().st_size,
            "tiff_sha256": sha256_file(tiff_path),
            "raster": metadata.to_dict(),
            "observed_source_metadata": {
                "source_crs": f"EPSG:{metadata.epsg}",
                "source_pixel_size": {
                    "x": metadata.pixel_size[0],
                    "y": metadata.pixel_size[1],
                    "unit": "degree",
                    "arcseconds": metadata.pixel_size[0] * 3600,
                },
                "source_dtype": metadata.data_types[0],
                "source_nodata": metadata.nodata[0],
                "source_resampling_documented": SOURCE_RESAMPLING_DOCUMENTED,
                "source_vertical_quantity": SOURCE_VERTICAL_QUANTITY,
                "source_vertical_unit": SOURCE_VERTICAL_UNIT,
                "geotiff_vertical_unit": metadata.z_units[0],
            },
            "source_contract": {
                "allowed_srids": list(SOURCE_ALLOWED_SRIDS),
                "expected_bands": SOURCE_EXPECTED_BANDS,
                "expected_dtype": SOURCE_EXPECTED_DTYPE,
                "expected_nodata": SOURCE_EXPECTED_NODATA,
                "expected_pixel_size_degrees": SOURCE_EXPECTED_RESOLUTION_DEGREES,
                "pixel_size_absolute_tolerance": SOURCE_RESOLUTION_ABS_TOLERANCE,
                "source_crs_was_detected": True,
                "actual_crs_was_not_assumed": True,
            },
            "pipeline_version": PIPELINE_VERSION,
            "created_at": datetime.now().astimezone().isoformat(),
        }

    def finalization(self, input_data: dict[str, object]) -> dict[str, object]:
        write_json_atomic(input_data, self.manifest_path)
        return input_data
