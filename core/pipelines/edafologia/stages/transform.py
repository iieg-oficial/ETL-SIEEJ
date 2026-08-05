from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from core.pipelines.edafologia.constants import (
    CANONICAL_SRID,
    MANIFEST_FILENAME,
    MUNICIPAL_OVERLAY_DIRNAME,
    MUNICIPAL_OVERLAY_MANIFEST_FILENAME,
    MUNICIPAL_OVERLAY_OUTPUT_FILENAME,
    PIPELINE_NAME,
    PIPELINE_VERSION,
    TRANSFORM_MANIFEST_FILENAME,
    TRANSFORM_OUTPUT_FILENAME,
    TRANSFORM_OUTPUT_LAYER,
)
from core.pipelines.edafologia.helpers.municipal_overlay import (
    calculate_municipal_overlay,
    read_overlay_inputs,
    write_overlay_artifacts,
)
from core.pipelines.edafologia.helpers.transform import (
    add_traceability,
    apply_catalog_ids,
    prepare_attributes,
    validate_catalog_coverage,
)
from core.pipelines.edafologia.helpers.transform_geometry import (
    build_canonical_mask,
    clip_to_mask,
    dissolve_by_source_objectid,
    final_spatial_validation,
    repair_and_polygonize,
    write_gpkg_atomic,
)
from core.pipelines.edafologia.helpers.transform_inputs import (
    read_boundary_layers,
    read_source_layer,
    validate_extract_manifest,
)
from core.pipelines.stage import Stage
from core.utils.files import sha256_file, write_json_atomic
from core.utils.logger import get_logger


class EdafologiaTransform(Stage):
    """Transform stage for the bootstrap-only Edafologia historical source."""

    def __init__(self, pipeline_name: str = PIPELINE_NAME, mode: str = "bootstrap") -> None:
        self.mode = mode
        super().__init__(pipeline_name, "transform")
        self.logger = get_logger(f"{pipeline_name}.transform")
        self.extract_manifest_path = Path("data") / "extract" / pipeline_name / MANIFEST_FILENAME
        self.output_path = self.work_dir / TRANSFORM_OUTPUT_FILENAME
        self.transform_manifest_path = self.work_dir / TRANSFORM_MANIFEST_FILENAME
        self.overlay_dir = self.work_dir / MUNICIPAL_OVERLAY_DIRNAME
        self.overlay_output_path = self.overlay_dir / MUNICIPAL_OVERLAY_OUTPUT_FILENAME
        self.overlay_manifest_path = self.overlay_dir / MUNICIPAL_OVERLAY_MANIFEST_FILENAME

    def source(self, input_data: Any | None = None) -> dict[str, Any]:
        self.logger.info("[source] Reading extract manifest")
        return validate_extract_manifest(self.extract_manifest_path)

    def action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        processed_at = datetime.now().astimezone()
        source = read_source_layer(input_data)
        initial_crs = str(source.crs)
        initial_geometry_types = sorted(source.geometry.geom_type.dropna().unique().tolist())

        boundaries_iieg, boundaries_inegi, boundary_validations = read_boundary_layers(input_data)
        coverage_canonical, mask_stats = build_canonical_mask(boundaries_iieg, boundaries_inegi)
        coverage_iieg = boundaries_iieg.geometry.union_all()
        coverage_inegi = boundaries_inegi.geometry.union_all()

        source = prepare_attributes(source)
        source_repaired, initial_repair = repair_and_polygonize(source, "source_objectid", "initial")
        projected = source_repaired.to_crs(epsg=CANONICAL_SRID)
        clipped, selected_count = clip_to_mask(projected, coverage_canonical)
        clipped_repaired, clipped_repair = repair_and_polygonize(clipped, "source_objectid", "clipped")
        canonical = dissolve_by_source_objectid(clipped_repaired)
        canonical_repaired, final_repair = repair_and_polygonize(canonical, "source_objectid", "final")
        catalog_validation = validate_catalog_coverage(canonical_repaired)
        with_catalog_ids = apply_catalog_ids(canonical_repaired)
        transformed = add_traceability(with_catalog_ids, input_data, processed_at)
        spatial_validation = final_spatial_validation(transformed, coverage_canonical, coverage_iieg, coverage_inegi)

        output_columns = [column for column in transformed.columns if column != transformed.geometry.name]
        write_gpkg_atomic(transformed, self.output_path, TRANSFORM_OUTPUT_LAYER)

        manifest = {
            "extract_manifest_path": str(self.extract_manifest_path),
            "extract_manifest_sha256": sha256_file(self.extract_manifest_path),
            "output_path": str(self.output_path),
            "output_sha256": sha256_file(self.output_path),
            "output_layer": TRANSFORM_OUTPUT_LAYER,
            "initial_feature_count": int(len(source)),
            "selected_feature_count": selected_count,
            "final_feature_count": int(len(transformed)),
            "initial_crs": initial_crs,
            "final_crs": CANONICAL_SRID,
            "initial_geometry_types": initial_geometry_types,
            "final_geometry_types": spatial_validation["geometry_types"],
            "geometry_repair": {
                "initial": initial_repair,
                "clipped": clipped_repair,
                "final": final_repair,
            },
            "mask_statistics": mask_stats,
            "boundary_validations": boundary_validations,
            "catalog_coverage": catalog_validation["coverage"],
            "unmapped_codes": catalog_validation["unmapped_codes"],
            "spatial_validation": spatial_validation,
            "output_fields": output_columns,
            "processed_at": processed_at.isoformat(),
            "pipeline_version": PIPELINE_VERSION,
        }
        write_json_atomic(manifest, self.transform_manifest_path)
        overlay_inputs = read_overlay_inputs(self.transform_manifest_path)
        fragments, overlay_manifest = calculate_municipal_overlay(overlay_inputs)
        overlay_manifest = write_overlay_artifacts(
            fragments,
            overlay_manifest,
            self.overlay_output_path,
            self.overlay_manifest_path,
        )
        return {
            "gdf": transformed,
            "manifest": manifest,
            "fragments": fragments,
            "overlay_manifest": overlay_manifest,
        }

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        self.logger.info("[finalization] Transform manifest written to %s", self.transform_manifest_path)
        self.logger.info("[finalization] Municipal overlay written to %s", self.overlay_dir)
        return input_data
