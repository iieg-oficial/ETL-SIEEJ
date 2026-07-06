from datetime import date
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from sqlalchemy import delete, select

from core.db import Database
from core.pipelines.defunciones.config import settings
from core.pipelines.defunciones.constants import (
    ANIO_COLUMN,
    CAPITULO_GRUPO_DATASET,
    CATALOG_FK_COLUMNS,
    CHAPTER_TOTAL_GPO,
    CODED_SOURCE_COLUMNS,
    COLUMN_CATALOG,
    EDAD_DATASET,
    EDICION_DATASET,
    FACT_DATASET,
    GEO_ROLES,
    NOMBRE_EDAD_COL,
    PIPELINE_NAME,
    VERSIONED_SOURCE_COLUMNS,
)
from core.utils.geo import resolve_municipio_ids
from core.pipelines.defunciones.schemas import (
    CATALOG_MODELS,
    CODED_MODELS,
    OVERRIDE_MODELS,
    VERSIONED_MODELS,
    CatCapituloGrupo,
    CatEdad,
    CatEdicion,
    StgDefunciones,
)
from core.pipelines.stage import Stage
from core.utils.bulk_ops import (
    bulk_insert,
    count_records,
    get_cvegeo_mapping,
    sync_id_sequence,
    upsert_records,
)
from core.utils.files import cleanup_pipeline_data
from core.utils.logger import get_logger

_MODELS_BY_TABLE: dict[str, type] = {
    model.__tablename__: model for model in (CatEdad, *CATALOG_MODELS, *OVERRIDE_MODELS)
}

CATALOG_SPECS: dict[str, tuple[type, str]] = {
    EDAD_DATASET: (CatEdad, NOMBRE_EDAD_COL),
    **{model.__tablename__: (model, "descripcion") for model in (*CATALOG_MODELS, *OVERRIDE_MODELS)},
}

FK_CATALOGS: dict[str, type] = {
    CATALOG_FK_COLUMNS[col]: _MODELS_BY_TABLE[table]
    for col, table in COLUMN_CATALOG.items()
    if col not in VERSIONED_SOURCE_COLUMNS and col not in CODED_SOURCE_COLUMNS
}

_VERSIONED_BY_TABLE: dict[str, type] = {m.__tablename__: m for m in VERSIONED_MODELS}
VERSIONED_FK_MODELS: dict[str, type] = {
    CATALOG_FK_COLUMNS[col]: _VERSIONED_BY_TABLE[table] for col, table in VERSIONED_SOURCE_COLUMNS.items()
}

_CODED_BY_TABLE: dict[str, type] = {m.__tablename__: m for m in CODED_MODELS}
CODED_FK_MODELS: dict[str, type] = {
    CATALOG_FK_COLUMNS[col]: _CODED_BY_TABLE[table] for col, table in CODED_SOURCE_COLUMNS.items()
}


class DefuncionesLoad(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode
        self.logger = get_logger(f"{PIPELINE_NAME}.load")
        self.db = Database(PIPELINE_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> dict[str, Any]:
        if input_data and "catalogs" in input_data:
            return input_data

        transform_path = Path("data/transform") / PIPELINE_NAME / "transform.pkl"
        if not transform_path.exists():
            raise FileNotFoundError(f"[source] Missing transform pickle: {transform_path}")
        self.logger.info("[source] Loading %s", transform_path)
        return pd.read_pickle(transform_path)

    def _load_catalogs(self, session, catalogs: dict[str, list[dict[str, Any]]]) -> None:
        for name, (model, update_key) in CATALOG_SPECS.items():
            if name not in catalogs:
                continue
            upsert_records(
                session,
                catalogs[name],
                model,
                conflict_keys=["id"],
                update_keys=[update_key],
            )

    def _load_capitulo_grupo(self, session, catalogs: dict[str, list[dict[str, Any]]]) -> None:
        records = catalogs.get(CAPITULO_GRUPO_DATASET)
        if not records:
            return
        sync_id_sequence(session, CatCapituloGrupo)
        upsert_records(session, records, CatCapituloGrupo, conflict_keys=["cap", "gpo"], update_keys=["descripcion"])

    def _load_edicion(self, session, catalogs: dict[str, list[dict[str, Any]]]) -> None:
        records = catalogs.get(EDICION_DATASET)
        if not records:
            return
        sync_id_sequence(session, CatEdicion)
        upsert_records(session, records, CatEdicion, conflict_keys=["anio"], update_keys=["descripcion"])

    def _edicion_map(self, session) -> dict[int, int]:
        return {anio: eid for anio, eid in session.execute(select(CatEdicion.anio, CatEdicion.id))}

    def _load_versioned(self, session, catalogs: dict[str, list[dict[str, Any]]]) -> None:
        edicion_map = self._edicion_map(session)
        for model in VERSIONED_MODELS:
            records = catalogs.get(model.__tablename__)
            if not records:
                continue
            for record in records:
                record["edicion_id"] = edicion_map.get(record.pop("anio"))
            records = [r for r in records if r["edicion_id"] is not None]
            sync_id_sequence(session, model)
            upsert_records(session, records, model, conflict_keys=["codigo", "edicion_id"], update_keys=["descripcion"])

    def _resolve_versioned(self, session, records: list[dict[str, Any]]) -> None:
        edicion_map = self._edicion_map(session)
        for record in records:
            record["edicion_id"] = edicion_map.get(record.get(ANIO_COLUMN))
        for fk_col, model in VERSIONED_FK_MODELS.items():
            mapping = {
                (codigo, eid): sid
                for codigo, eid, sid in session.execute(select(model.codigo, model.edicion_id, model.id))
            }
            for record in records:
                code = record.get(fk_col)
                record[fk_col] = mapping.get((code, record.get("edicion_id"))) if code is not None else None

    def _load_coded(self, session, catalogs: dict[str, list[dict[str, Any]]]) -> None:
        for model in CODED_MODELS:
            records = catalogs.get(model.__tablename__)
            if not records:
                continue
            sync_id_sequence(session, model)
            upsert_records(session, records, model, conflict_keys=["codigo"], update_keys=["descripcion"])

    def _resolve_coded(self, session, records: list[dict[str, Any]]) -> None:
        for fk_col, model in CODED_FK_MODELS.items():
            mapping = {codigo: sid for codigo, sid in session.execute(select(model.codigo, model.id))}
            for record in records:
                code = record.get(fk_col)
                record[fk_col] = mapping.get(code) if code is not None else None

    def _resolve_capitulo_grupo(self, session, records: list[dict[str, Any]]) -> None:
        mapping = {
            (cap, gpo): rid
            for cap, gpo, rid in session.execute(
                select(CatCapituloGrupo.cap, CatCapituloGrupo.gpo, CatCapituloGrupo.id)
            )
        }
        for record in records:
            cap = record.get("capitulo")
            if cap is None:
                record["capitulo_grupo_id"] = None
                continue
            gpo = record.get("grupo")
            gpo = CHAPTER_TOTAL_GPO if gpo is None else gpo
            record["capitulo_grupo_id"] = mapping.get((cap, gpo))

    @staticmethod
    def _apply_fk_nulls(records: list[dict[str, Any]], valid: dict[str, set[int]]) -> None:
        for record in records:
            for column, ids in valid.items():
                if record.get(column) is not None and record[column] not in ids:
                    record[column] = None

    def _null_invalid_fks(self, session, records: list[dict[str, Any]]) -> None:
        valid = {column: {row[0] for row in session.execute(select(model.id))} for column, model in FK_CATALOGS.items()}
        self._apply_fk_nulls(records, valid)

    def _resolve_geo(self, session, records: list[dict[str, Any]]) -> None:
        try:
            with session.begin_nested():
                mapping = get_cvegeo_mapping(session, "cvegeo_municipalities", key="cvegeo", value="id")
        except Exception as error:  # noqa: BLE001 - infra optional in some envs
            self.logger.warning("[facts] cvegeo mapping unavailable; municipio ids NULL (%s)", error)
            return
        resolve_municipio_ids(records, GEO_ROLES, mapping)

    def _load_facts(self, session, records: list[dict[str, Any]]) -> None:
        load_date = date.today()
        for record in records:
            record["fecha_actualizacion"] = load_date

        self._resolve_versioned(session, records)
        self._resolve_coded(session, records)
        self._null_invalid_fks(session, records)
        self._resolve_geo(session, records)
        self._resolve_capitulo_grupo(session, records)

        years = {r[ANIO_COLUMN] for r in records if r.get(ANIO_COLUMN) is not None}
        if years:
            session.execute(delete(StgDefunciones).where(StgDefunciones.anio_registro_id.in_(years)))
            session.flush()
            self.logger.info("[facts] Reloading years: %s", sorted(years))

        bulk_insert(session, records, StgDefunciones, chunk_size=settings.CHUNK_SIZE)

    def action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        catalogs = input_data["catalogs"]
        facts = input_data["facts"][FACT_DATASET]

        self.db.connect()
        try:
            with self.db.get_session() as session:
                before = {name: count_records(session, model) for name, (model, _) in CATALOG_SPECS.items()}
                before[FACT_DATASET] = count_records(session, StgDefunciones)

                self._load_catalogs(session, catalogs)
                self._load_coded(session, catalogs)
                self._load_capitulo_grupo(session, catalogs)
                self._load_edicion(session, catalogs)
                self._load_versioned(session, catalogs)
                self._load_facts(session, facts)
        except Exception:
            self.db.disconnect()
            raise

        incoming = {name: len(catalogs.get(name, [])) for name in CATALOG_SPECS}
        incoming[FACT_DATASET] = len(facts)
        return {"before": before, "incoming": incoming}

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        try:
            with self.db.get_session() as session:
                after = {name: count_records(session, model) for name, (model, _) in CATALOG_SPECS.items()}
                after[FACT_DATASET] = count_records(session, StgDefunciones)
        finally:
            self.db.disconnect()
            cleanup_pipeline_data(PIPELINE_NAME)

        for name in (*CATALOG_SPECS, FACT_DATASET):
            self.logger.info(
                "[finalization] %s: before=%s incoming=%s after=%s",
                name,
                input_data["before"][name],
                input_data["incoming"][name],
                after[name],
            )
        return {**input_data, "after": after}
