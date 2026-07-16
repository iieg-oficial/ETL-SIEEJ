from __future__ import annotations

from pathlib import Path
from typing import Any

from core.db import Database
from core.pipelines.edafologia.config import settings
from core.pipelines.edafologia.constants import (
    MUNICIPAL_OVERLAY_DIRNAME,
    MUNICIPAL_OVERLAY_MANIFEST_FILENAME,
    PIPELINE_NAME,
)
from core.pipelines.edafologia.helpers.municipal_overlay_load import (
    analyze_overlay_tables,
    overlay_records,
    read_validated_overlay,
    replace_overlay_scope,
    resolve_boundary_source_ids,
    resolve_edafologia_ids,
)
from core.pipelines.edafologia.helpers.mode import validate_bootstrap_mode
from core.pipelines.stage import Stage
from core.utils.logger import get_logger


class EdafologiaMunicipalOverlayLoad(Stage):
    """Municipal overlay load stage for the bootstrap-only Edafologia historical source."""

    def __init__(self, pipeline_name: str = PIPELINE_NAME, mode: str = "bootstrap") -> None:
        self.mode = validate_bootstrap_mode(mode)
        super().__init__(pipeline_name, "load")
        self.logger = get_logger(f"{pipeline_name}.municipal_overlay_load")
        self.db = Database(settings.DB_NAME, settings.database_url)
        self.overlay_manifest_path = (
            Path("data") / "transform" / pipeline_name / MUNICIPAL_OVERLAY_DIRNAME / MUNICIPAL_OVERLAY_MANIFEST_FILENAME
        )

    def source(self, input_data: Any | None = None) -> dict[str, Any]:
        self.logger.info("[source] Reading municipal overlay manifest")
        manifest, frame = read_validated_overlay(self.overlay_manifest_path)
        return {"manifest": manifest, "frame": frame}

    def action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        self.logger.info("[action] Loading municipal overlay fragments")
        try:
            self.db.connect()
            with self.db.get_session() as session:
                source_ids = resolve_boundary_source_ids(session)
                edafologia_ids = resolve_edafologia_ids(session, input_data["frame"])
                records = overlay_records(input_data["frame"], edafologia_ids, source_ids)
                result = replace_overlay_scope(session, records, chunk_size=settings.CHUNK_SIZE)
                analyze_overlay_tables(session)
        except Exception:
            self.db.disconnect()
            raise
        return {"manifest": input_data["manifest"], **result}

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        try:
            self.logger.info(
                "[finalization] %s municipal overlay fragments loaded across %s scopes",
                input_data["records"],
                len(input_data["scopes"]),
            )
            return input_data
        finally:
            self.db.disconnect()
