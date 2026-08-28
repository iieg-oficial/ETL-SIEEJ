from __future__ import annotations

from pathlib import Path
from typing import Any

import geopandas as gpd

from core.pipelines.pendientes.constants import LOAD_MANIFEST_FILENAME, PIPELINE_NAME, PRODUCT_CONTRACT, TARGET_SRID
from core.pipelines.pendientes.helpers.publication import (
    validate_lineage_contract,
    validate_pair_consistency,
    validate_product_set,
)
from core.pipelines.stage import Stage
from core.utils.files import read_json, write_json_atomic


class PendientesLoad(Stage):
    """Prepublication contract for the coherent three-raster product family.

    This stage validates and writes a load manifest, but deliberately does not
    publish to an institutional destination until ETL-SIEEJ defines a raster pattern.
    """

    def __init__(self, pipeline_name: str = PIPELINE_NAME, mode: str = "bootstrap") -> None:
        self.mode = mode
        super().__init__(pipeline_name, "load")
        self.products_manifest_path = Path("data") / "transform" / pipeline_name / "products_manifest.json"
        self.load_manifest_path = self.work_dir / LOAD_MANIFEST_FILENAME

    def source(self, input_data: Any | None = None) -> dict[str, Any]:
        manifest = read_json(self.products_manifest_path)
        if manifest is None:
            raise FileNotFoundError(
                "Canonical product manifest is not available; conditioning and slope methods are not promoted yet"
            )
        if set(manifest.get("products", {})) != set(PRODUCT_CONTRACT):
            raise ValueError(f"Products manifest must contain exactly {sorted(PRODUCT_CONTRACT)}")
        return manifest

    def action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        boundary_path = Path(input_data["jalisco_boundary_path"])
        boundary_layer = input_data.get("jalisco_boundary_layer", "jalisco")
        boundary = gpd.read_file(boundary_path, layer=boundary_layer)
        if boundary.empty or boundary.crs is None or boundary.crs.to_epsg() != TARGET_SRID:
            raise ValueError("Products manifest must reference a non-empty EPSG:6368 Jalisco boundary")
        jalisco_geometry = boundary.geometry.unary_union
        products = {name: Path(details["path"]) for name, details in input_data["products"].items()}
        validations = validate_product_set(products, jalisco_geometry)
        lineage = validate_lineage_contract(input_data, validations)
        pair_consistency = validate_pair_consistency(products["pendiente_grados"], products["pendiente_porcentaje"])
        return {
            "status": "validated_pending_institutional_raster_publication_pattern",
            "publication_performed": False,
            "lineage": lineage,
            "validations": validations,
            "pair_consistency": pair_consistency,
        }

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        write_json_atomic(input_data, self.load_manifest_path)
        return input_data
