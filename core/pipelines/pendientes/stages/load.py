from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from core.db import Database
from core.pipelines.pendientes.config import settings
from core.pipelines.pendientes.constants import (
    FINAL_DIRECTORY_NAME,
    FINAL_TRANSFORM_MANIFEST_FILENAME,
    LOAD_ANALYTICAL_DIRECTORY_NAME,
    LOAD_GEOPORTAL_DIRECTORY_NAME,
    MUNICIPAL_BOUNDARY_SOURCES,
    PIPELINE_NAME,
    RELEASE_MANIFEST_FILENAME,
)
from core.pipelines.pendientes.helpers.cog import validate_cog_structure
from core.pipelines.pendientes.helpers.release import materialize_release_file
from core.pipelines.pendientes.schemas import FuentesLimitesMunicipales, EstadisticasPendienteMunicipales
from core.pipelines.stage import Stage
from core.utils.bulk_ops import upsert_records
from core.utils.files import read_json, sha256_file, write_json_atomic


class PendientesLoad(Stage):
    """Materialize validated COGs and load only municipal tabular results."""

    def __init__(self, pipeline_name: str = PIPELINE_NAME, mode: str = "bootstrap") -> None:
        self.mode = mode
        super().__init__(pipeline_name, "load")
        self.transform_manifest_path = (
            Path("data") / "transform" / pipeline_name / FINAL_DIRECTORY_NAME / FINAL_TRANSFORM_MANIFEST_FILENAME
        )
        self.release_manifest_path = self.work_dir / RELEASE_MANIFEST_FILENAME
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(self, input_data: Any | None = None) -> dict[str, Any]:
        manifest = read_json(self.transform_manifest_path)
        if manifest is None or manifest.get("status") != "transform_complete":
            raise ValueError("Load requires a completed, validated final Transform manifest")
        if len(manifest.get("rasters", {})) != 5:
            raise ValueError("Load requires exactly three continuous and two classified COG products")
        reference_grid = None
        for product, details in manifest["rasters"].items():
            path = Path(details["path"])
            if not path.is_file() or sha256_file(path) != details["sha256"]:
                raise ValueError(f"Transform COG changed before Load: {product}")
            structure = validate_cog_structure(path)
            classified = details["product_role"] == "classified"
            expected = {
                "compression": "DEFLATE",
                "block_shape": [512, 512],
                "dtype": "uint8" if classified else "float32",
                "nodata": 255.0 if classified else -9999.0,
                "crs_epsg": 6368,
                "resolution": [15.0, 15.0],
            }
            failed = {key: [structure[key], value] for key, value in expected.items() if structure[key] != value}
            if failed or not structure["overviews"]:
                raise ValueError(f"Transform COG contract failed for {product}: {failed}")
            grid = (structure["transform"], structure["bounds"])
            reference_grid = grid if reference_grid is None else reference_grid
            if grid != reference_grid:
                raise ValueError(f"Transform COG grid differs from the coherent product set: {product}")
            if not details.get("hard_gates", {}).get("all_passed") or not details.get("lossless"):
                raise ValueError(f"Transform lossless packaging QA is not approved: {product}")
        table = manifest["municipal_statistics"]
        table_path = Path(table["path"])
        if not table_path.is_file() or sha256_file(table_path) != table["sha256"]:
            raise ValueError("Municipal statistics changed before Load")
        frame = pd.read_parquet(table_path)
        sources = manifest["municipal_boundaries"]["sources"]
        expected_rows = sum(int(source["municipality_count"]) for source in sources.values())
        if len(frame) != expected_rows:
            raise ValueError("Load municipal statistics row count differs from the validated snapshot")
        if frame.duplicated(["municipality_id", "fuente_limite_municipal_id"]).any():
            raise ValueError("Load municipal statistics contain duplicated source-municipality keys")
        return {"manifest": manifest, "statistics": frame}

    def _materialize_rasters(self, rasters: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        materialized = {}
        for product, details in rasters.items():
            subdirectory = (
                LOAD_ANALYTICAL_DIRECTORY_NAME
                if details["product_role"] == "continuous"
                else LOAD_GEOPORTAL_DIRECTORY_NAME
            )
            destination = self.work_dir / subdirectory / Path(details["path"]).name
            report = materialize_release_file(Path(details["path"]), destination, details["sha256"])
            materialized[product] = {
                **report,
                "format": "COG",
                "cloud_optimized": True,
                "compression": details["compression"],
                "lossless": details["lossless"],
                "block_size": details["block_size"],
                "overview_levels": details["overview_levels"],
                "overview_resampling": details["overview_resampling"],
                "scientific_sha256": details["scientific_sha256"],
                "lineage": details["analytical_parent"],
            }
        return materialized

    @staticmethod
    def _catalog_records() -> list[dict[str, Any]]:
        names = {"iieg": "Límite municipal IIEG", "inegi": "Límite municipal INEGI"}
        return [
            {
                "id": int(source["id"]),
                "clave": key,
                "nombre_fuente": names[key],
                "descripcion": f"Estadística zonal por geometría {source['geometry_column']} de cvegeo.",
                "version": "snapshot congelado por Extract",
                "procedencia": "base cvegeo institucional",
            }
            for key, source in MUNICIPAL_BOUNDARY_SOURCES.items()
        ]

    def _load_statistics(self, frame: pd.DataFrame) -> dict[str, Any]:
        records = frame.to_dict(orient="records")
        for record in records:
            record["fecha_actualizacion"] = date.today()
            record.pop("fuente_limite_clave", None)
        self.db.connect()
        try:
            with self.db.get_session() as session:
                upsert_records(
                    session,
                    self._catalog_records(),
                    FuentesLimitesMunicipales,
                    conflict_keys=[FuentesLimitesMunicipales.id.key],
                    update_keys=[
                        FuentesLimitesMunicipales.clave.key,
                        FuentesLimitesMunicipales.nombre_fuente.key,
                        FuentesLimitesMunicipales.descripcion.key,
                        FuentesLimitesMunicipales.version.key,
                        FuentesLimitesMunicipales.procedencia.key,
                    ],
                )
                upsert_records(
                    session,
                    records,
                    EstadisticasPendienteMunicipales,
                    conflict_keys=[
                        EstadisticasPendienteMunicipales.municipality_id.key,
                        EstadisticasPendienteMunicipales.fuente_limite_municipal_id.key,
                    ],
                    update_keys=[
                        key for key in records[0] if key not in {"municipality_id", "fuente_limite_municipal_id"}
                    ],
                )
        finally:
            self.db.disconnect()
        return {"catalog_rows": 2, "municipal_statistics_rows": len(records), "transactional": True}

    def action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        rasters = self._materialize_rasters(input_data["manifest"]["rasters"])
        base_manifest = {
            "created_at": datetime.now().astimezone().isoformat(),
            "transform_manifest_path": str(self.transform_manifest_path),
            "transform_manifest_sha256": sha256_file(self.transform_manifest_path),
            "raster_release_status": "validated_and_materialized",
            "municipal_statistics_status": "validated_for_load",
            "raster_products": rasters,
            "tabular_products": {
                "municipal_statistics": input_data["manifest"]["municipal_statistics"],
                "indicators": input_data["manifest"]["indicators"],
            },
            "municipal_snapshot": input_data["manifest"]["municipal_boundaries"],
            "lineage": input_data["manifest"]["lineage"],
            "raster_database_load": False,
            "cog_conversion_performed_by_load": False,
        }
        try:
            database = self._load_statistics(input_data["statistics"])
        except Exception as error:
            failed = {
                **base_manifest,
                "status": "load_incomplete",
                "database_load_status": "failed",
                "database_load": {"status": "failed", "error_type": type(error).__name__},
            }
            write_json_atomic(failed, self.release_manifest_path)
            raise
        return {
            **base_manifest,
            "status": "load_complete",
            "database_load_status": "loaded",
            "database_load": {**database, "status": "loaded", "idempotent_upsert": True},
        }

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        write_json_atomic(input_data, self.release_manifest_path)
        return input_data
