from __future__ import annotations

from pathlib import Path
from typing import Any

from core.pipelines.edafologia.constants import (
    MUNICIPAL_OVERLAY_DIRNAME,
    MUNICIPAL_OVERLAY_MANIFEST_FILENAME,
    MUNICIPAL_OVERLAY_OUTPUT_FILENAME,
    PIPELINE_NAME,
    TRANSFORM_MANIFEST_FILENAME,
)
from core.pipelines.edafologia.helpers.municipal_overlay import (
    calculate_municipal_overlay,
    read_overlay_inputs,
    write_overlay_artifacts,
)
from core.pipelines.edafologia.helpers.mode import validate_bootstrap_mode
from core.pipelines.stage import Stage
from core.utils.logger import get_logger


class EdafologiaMunicipalOverlay(Stage):
    """Municipal overlay stage for the bootstrap-only Edafologia historical source."""

    def __init__(self, pipeline_name: str = PIPELINE_NAME, mode: str = "bootstrap") -> None:
        self.mode = validate_bootstrap_mode(mode)
        super().__init__(pipeline_name, "transform")
        self.logger = get_logger(f"{pipeline_name}.municipal_overlay")
        self.transform_manifest_path = Path("data") / "transform" / pipeline_name / TRANSFORM_MANIFEST_FILENAME
        self.overlay_dir = self.work_dir / MUNICIPAL_OVERLAY_DIRNAME
        self.output_path = self.overlay_dir / MUNICIPAL_OVERLAY_OUTPUT_FILENAME
        self.overlay_manifest_path = self.overlay_dir / MUNICIPAL_OVERLAY_MANIFEST_FILENAME

    def source(self, input_data: Any | None = None) -> dict[str, Any]:
        self.logger.info("[source] Reading transform and boundary inputs for municipal overlay")
        return read_overlay_inputs(self.transform_manifest_path)

    def action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        self.logger.info("[action] Calculating municipal overlay for IIEG and INEGI boundaries")
        fragments, manifest = calculate_municipal_overlay(input_data)
        return {"fragments": fragments, "manifest": manifest}

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        manifest = write_overlay_artifacts(
            input_data["fragments"],
            input_data["manifest"],
            self.output_path,
            self.overlay_manifest_path,
        )
        self.logger.info("[finalization] Overlay artifacts written to %s", self.overlay_dir)
        return {"manifest": manifest, "fragments": input_data["fragments"]}
