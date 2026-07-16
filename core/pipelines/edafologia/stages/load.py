from __future__ import annotations

from pathlib import Path
from typing import Any

from core.db import Database
from core.pipelines.edafologia.config import settings
from core.pipelines.edafologia.constants import PIPELINE_NAME, TRANSFORM_MANIFEST_FILENAME
from core.pipelines.edafologia.helpers.load import (
    boundary_source_records,
    canonical_records,
    catalog_count_summary,
    catalog_records,
    read_transform_manifest,
    read_transformed_layer,
    resolve_catalog_ids,
    source_identity,
    validate_catalog_counts,
    validate_transform_manifest,
    validate_transformed_frame,
    validate_version_collision,
)
from core.pipelines.edafologia.mappings import CALIFICADORES_EDAFOLOGICOS, GRUPOS_EDAFOLOGICOS
from core.pipelines.edafologia.schemas import (
    CalificadoresEdafologicos,
    Edafologias,
    FuentesLimitesMunicipales,
    GruposEdafologicos,
)
from core.pipelines.edafologia.helpers.mode import validate_bootstrap_mode
from core.pipelines.stage import Stage
from core.utils.bulk_ops import count_records, get_mapping, sync_id_sequence, upsert_records
from core.utils.logger import get_logger


class EdafologiaLoad(Stage):
    """Canonical load stage for the bootstrap-only Edafologia historical source."""

    def __init__(self, pipeline_name: str = PIPELINE_NAME, mode: str = "bootstrap") -> None:
        self.mode = validate_bootstrap_mode(mode)
        super().__init__(pipeline_name, "load")
        self.logger = get_logger(f"{pipeline_name}.load")
        self.db = Database(settings.DB_NAME, settings.database_url)
        self.transform_manifest_path = Path("data") / "transform" / pipeline_name / TRANSFORM_MANIFEST_FILENAME

    def source(self, input_data: Any | None = None) -> dict[str, Any]:
        self.logger.info("[source] Reading transform manifest")
        manifest = read_transform_manifest(self.transform_manifest_path)
        validate_transform_manifest(manifest, self.transform_manifest_path)
        frame = read_transformed_layer(manifest)
        validate_transformed_frame(frame, manifest)
        return {"manifest": manifest, "frame": frame}

    def _load_catalogs(self, session) -> dict[str, int]:
        group_records = catalog_records(GRUPOS_EDAFOLOGICOS)
        qualifier_records = catalog_records(CALIFICADORES_EDAFOLOGICOS)
        limit_records = boundary_source_records()
        validate_catalog_counts(group_records, qualifier_records, limit_records)

        upsert_records(
            session,
            group_records,
            GruposEdafologicos,
            conflict_keys=[GruposEdafologicos.clave.key],
            update_keys=[GruposEdafologicos.descripcion.key],
            chunk_size=settings.CHUNK_SIZE,
        )
        upsert_records(
            session,
            qualifier_records,
            CalificadoresEdafologicos,
            conflict_keys=[CalificadoresEdafologicos.clave.key],
            update_keys=[CalificadoresEdafologicos.descripcion.key],
            chunk_size=settings.CHUNK_SIZE,
        )
        upsert_records(
            session,
            limit_records,
            FuentesLimitesMunicipales,
            conflict_keys=[FuentesLimitesMunicipales.clave.key],
            update_keys=[
                FuentesLimitesMunicipales.nombre.key,
                FuentesLimitesMunicipales.descripcion.key,
                FuentesLimitesMunicipales.version.key,
                FuentesLimitesMunicipales.procedencia.key,
            ],
            chunk_size=settings.CHUNK_SIZE,
        )
        for model in (GruposEdafologicos, CalificadoresEdafologicos):
            sync_id_sequence(session, model)
        return catalog_count_summary(group_records, qualifier_records, limit_records)

    def _canonical_records(self, session, frame) -> list[dict[str, Any]]:
        grupo_ids = get_mapping(session, GruposEdafologicos, GruposEdafologicos.clave.key, GruposEdafologicos.id.key)
        calificador_ids = get_mapping(
            session,
            CalificadoresEdafologicos,
            CalificadoresEdafologicos.clave.key,
            CalificadoresEdafologicos.id.key,
        )
        resolved = resolve_catalog_ids(frame, grupo_ids, calificador_ids)
        return canonical_records(resolved)

    def action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        manifest = input_data["manifest"]
        frame = input_data["frame"]
        self.logger.info("[action] Loading canonical Edafologia records")

        try:
            self.db.connect()
            with self.db.get_session() as session:
                source_version, source_file_sha256 = source_identity(frame)
                validate_version_collision(session, source_version, source_file_sha256)
                catalog_counts = self._load_catalogs(session)
                records_before = count_records(session, Edafologias)
                records = self._canonical_records(session, frame)
                upsert_records(
                    session,
                    records,
                    Edafologias,
                    conflict_keys=[Edafologias.source_version.key, Edafologias.source_objectid.key],
                    update_keys=[
                        key
                        for key in records[0]
                        if key not in {Edafologias.source_version.key, Edafologias.source_objectid.key}
                    ],
                    chunk_size=settings.CHUNK_SIZE,
                )
                records_after = count_records(session, Edafologias)
        except Exception:
            self.db.disconnect()
            raise

        return {
            "manifest": manifest,
            "catalog_counts": catalog_counts,
            "canonical_records": len(records),
            "records_before": records_before,
            "records_after": records_after,
            "inserted_or_net_new": records_after - records_before,
        }

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        try:
            self.logger.info(
                "[finalization] %s canonical edafologia records processed; %s net new rows",
                input_data["canonical_records"],
                input_data["inserted_or_net_new"],
            )
            return input_data
        finally:
            self.db.disconnect()
