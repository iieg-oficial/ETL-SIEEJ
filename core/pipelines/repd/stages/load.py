import pandas as pd

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import text

from core.db import Database
from core.pipelines.repd.config import settings
from core.pipelines.repd.consts import (
    CATALOG_COLUMNS,
    HASH_FIELDS,
    MUNICIPALITY_COLUMNS,
    PIPELINE_NAME,
    SKIP_MUNICIPALITY_VALUES,
)
from core.pipelines.repd.queries import MATERIALIZED_VIEWS
from core.pipelines.repd.schemas import (
    CATALOG_MODELS,
    CaseCurrent,
    CaseHistory,
    RepdBase,
)
from core.pipelines.stage import Stage
from core.utils.bulk_ops import (
    bulk_insert,
    get_mapping,
    insert_records,
    sync_id_sequence,
)
from core.utils.files import clean_directory
from core.utils.normalize import normalize_text
from core.utils.records import compute_record_hash
from core.utils.views import refresh_materialized_views


class REPDLoader(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode
        self.db: Database | None = None
        self._catalog_caches: dict[str, dict[str, int]] = {}
        self._municipality_cache: dict[tuple[str, str], int] = {}

    # Conecta a la BD y verifica tablas
    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data:
            raise ValueError("Load no recibio datos de Transform.")

        self.db = Database(PIPELINE_NAME, settings.database_url)
        self.db.connect()

        RepdBase.metadata.create_all(self.db.engine)
        self.logger.info("Tablas verificadas/creadas.")

        return input_data

    # Carga catalogos, resuelve FKs y persiste registros
    def action(self, input_data: Optional[Any] = None) -> dict:
        df: pd.DataFrame = input_data["df"]
        catalog_values: dict[str, list[str]] = input_data["catalogs"]

        with self.db.get_session() as session:
            self._load_catalogs(session, catalog_values)
            self._load_municipality_cache(session)

        df = self._resolve_catalog_ids(df)
        df = self._resolve_municipality_ids(df)

        # Calcular record_hash
        df["record_hash"] = df.apply(lambda row: compute_record_hash(row.to_dict(), HASH_FIELDS), axis=1)

        if self.mode == "bootstrap":
            stats = self._load_bootstrap(df)
        else:
            stats = self._load_update(df)

        self._refresh_views()

        return stats

    # Refresca las vistas materializadas despues de cargar datos
    def _refresh_views(self) -> None:
        refresh_materialized_views(self.db, MATERIALIZED_VIEWS)

    # Sincroniza secuencias, limpia carpeta de datos y desconecta
    def finalization(self, input_data: Optional[Any] = None) -> dict:
        with self.db.get_session() as session:
            for model in CATALOG_MODELS.values():
                sync_id_sequence(session, model)
            sync_id_sequence(session, CaseCurrent)
            sync_id_sequence(session, CaseHistory)

        clean_directory(self.work_dir, self.logger)

        self.db.disconnect()
        self.logger.info(f"Etapa Load completa. Estadisticas: {input_data}")
        return input_data

    # Inserta valores en tablas catalogo y construye caches name->id
    def _load_catalogs(self, session, catalog_values: dict[str, list[str]]) -> None:
        for cat_key, values in catalog_values.items():
            model = CATALOG_MODELS[cat_key]
            records = [{"name": v} for v in values]
            insert_records(session, records, model, conflict_keys=["name"])
            self.logger.info(f"Catalogo '{cat_key}': {len(records)} valores sincronizados.")

        session.flush()

        for cat_key, model in CATALOG_MODELS.items():
            self._catalog_caches[cat_key] = get_mapping(session, model, "name", "id", is_normalize=True)

    # Inserta nuevos valores en un catalogo y refresca su cache
    def _refresh_catalog(self, session, cat_key: str, new_values: list[str]) -> None:
        model = CATALOG_MODELS[cat_key]
        records = [{"name": v} for v in new_values]
        insert_records(session, records, model, conflict_keys=["name"])
        session.flush()
        self._catalog_caches[cat_key] = get_mapping(session, model, "name", "id", is_normalize=True)

    # Carga el mapping (estado, municipio)->id desde cvegeo via FDW
    def _load_municipality_cache(self, session) -> None:
        results = session.execute(text("SELECT nom_ent, nomgeo, id FROM cvegeo_municipalities")).all()
        self._municipality_cache = {(normalize_text(row[0]), normalize_text(row[1])): row[2] for row in results}
        self.logger.info(f"Cache de municipios cvegeo: {len(self._municipality_cache)} entradas")

    # Resuelve (estado, municipio) a ID de cvegeo
    def _resolve_municipality_id(self, state: str | None, name: str | None) -> int | None:
        if name is None or name in SKIP_MUNICIPALITY_VALUES:
            return None
        if state is None:
            return None
        normalized_name = normalize_text(name)
        key = (normalize_text(state), normalized_name)
        return self._municipality_cache.get(key)

    # Agrega columnas *_id mapeando nombre->id de catalogo
    def _resolve_catalog_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in CATALOG_COLUMNS:
            cache = self._catalog_caches[col]
            series = df[col].apply(lambda v: cache.get(normalize_text(v)) if v is not None else None).astype(object)
            df[f"{col}_id"] = series.where(pd.notna(series), other=None)
        return df

    # Resuelve columnas de municipio a IDs de cvegeo
    def _resolve_municipality_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        for mun_col, state_col, id_col in MUNICIPALITY_COLUMNS:
            series = df.apply(
                lambda row: self._resolve_municipality_id(row.get(state_col), row.get(mun_col)),
                axis=1,
            ).astype(object)
            df[id_col] = series.where(pd.notna(series), other=None)
        return df

    # Carga inicial: inserta todos los registros en current e history
    def _load_bootstrap(self, df: pd.DataFrame) -> dict:
        now = datetime.utcnow()

        current_records = []
        history_records = []

        for _, row in df.iterrows():
            rec = self._build_case_record(row)
            current_records.append(
                {
                    **rec,
                    "current_version": 1,
                    "created_at": now,
                    "updated_at": now,
                }
            )
            history_records.append(
                {
                    **rec,
                    "version_num": 1,
                    "is_current": True,
                    "valid_from": now,
                    "valid_to": None,
                    "created_at": now,
                }
            )

        batch_size = settings.REPD_LOAD_BATCH_SIZE

        with self.db.get_session() as session:
            bulk_insert(session, current_records, CaseCurrent, chunk_size=batch_size)
            self.logger.info(f"Insertados {len(current_records)} registros en case_current.")

        # Asociar case_current_id a history
        with self.db.get_session() as session:
            feb_to_id = get_mapping(session, CaseCurrent, "feb", "id")

        for rec in history_records:
            rec["case_current_id"] = feb_to_id.get(rec["feb"])

        with self.db.get_session() as session:
            bulk_insert(session, history_records, CaseHistory, chunk_size=batch_size)
            self.logger.info(f"Insertados {len(history_records)} registros en case_history.")

        return {
            "mode": "bootstrap",
            "current_inserted": len(current_records),
            "history_inserted": len(history_records),
        }

    # Carga incremental: detecta cambios por hash y versiona (SCD2)
    def _load_update(self, df: pd.DataFrame) -> dict:
        now = datetime.utcnow()

        # Prefetch: feb -> {id, record_hash, current_version}
        with self.db.get_session() as session:
            existing_rows = session.query(
                CaseCurrent.id,
                CaseCurrent.feb,
                CaseCurrent.record_hash,
                CaseCurrent.current_version,
            ).all()
        existing_by_feb = {
            row.feb: {
                "id": row.id,
                "hash": row.record_hash,
                "version": row.current_version,
            }
            for row in existing_rows
        }
        self.logger.info(f"Registros existentes en current: {len(existing_by_feb)}")

        new_current = []
        new_history = []
        updated_current = []
        closed_history = []
        updated_history = []

        for _, row in df.iterrows():
            rec = self._build_case_record(row)
            feb = rec["feb"]
            existing = existing_by_feb.get(feb)

            if existing is None:
                # Registro nuevo
                new_current.append(
                    {
                        **rec,
                        "current_version": 1,
                        "created_at": now,
                        "updated_at": now,
                    }
                )
                new_history.append(
                    {
                        **rec,
                        "version_num": 1,
                        "is_current": True,
                        "valid_from": now,
                        "valid_to": None,
                        "created_at": now,
                    }
                )

            elif existing["hash"] != rec["record_hash"]:
                # Registro cambio: crear nueva version
                new_version = existing["version"] + 1
                updated_current.append(
                    {
                        "feb": feb,
                        "case_id": existing["id"],
                        "record": {
                            **rec,
                            "current_version": new_version,
                            "updated_at": now,
                        },
                    }
                )
                closed_history.append(
                    {
                        "feb": feb,
                        "old_version": existing["version"],
                        "valid_to": now,
                    }
                )
                updated_history.append(
                    {
                        **rec,
                        "case_current_id": existing["id"],
                        "version_num": new_version,
                        "is_current": True,
                        "valid_from": now,
                        "valid_to": None,
                        "created_at": now,
                    }
                )

        batch_size = settings.REPD_LOAD_BATCH_SIZE

        # Insertar registros nuevos
        if new_current:
            with self.db.get_session() as session:
                bulk_insert(session, new_current, CaseCurrent, chunk_size=batch_size)

            with self.db.get_session() as session:
                feb_to_id = get_mapping(session, CaseCurrent, "feb", "id")
            for rec in new_history:
                rec["case_current_id"] = feb_to_id.get(rec["feb"])

            with self.db.get_session() as session:
                bulk_insert(session, new_history, CaseHistory, chunk_size=batch_size)

        # Actualizar registros que cambiaron
        if updated_current:
            with self.db.get_session() as session:
                for item in updated_current:
                    session.query(CaseCurrent).filter(CaseCurrent.id == item["case_id"]).update(item["record"])

                for item in closed_history:
                    session.query(CaseHistory).filter(
                        CaseHistory.feb == item["feb"],
                        CaseHistory.version_num == item["old_version"],
                    ).update(
                        {
                            "is_current": False,
                            "valid_to": item["valid_to"],
                        }
                    )

            with self.db.get_session() as session:
                bulk_insert(session, updated_history, CaseHistory, chunk_size=batch_size)

        unchanged = len(df) - len(new_current) - len(updated_current)
        self.logger.info(
            f"Update: {len(new_current)} nuevos, {len(updated_current)} actualizados, {unchanged} sin cambios"
        )

        return {
            "mode": "update",
            "new": len(new_current),
            "updated": len(updated_current),
            "unchanged": unchanged,
        }

    # Construye dict con campos de negocio a partir de una fila del DataFrame
    @staticmethod
    def _build_case_record(row: pd.Series) -> dict:
        return {
            "feb": row["feb"],
            "sex_id": row.get("sex_id"),
            "nationality_id": row.get("nationality_id"),
            "age_range_id": row.get("age_range_id"),
            "report_date": row.get("report_date"),
            "disappearance_date": row.get("disappearance_date"),
            "disappearance_state_name": row.get("disappearance_state_name"),
            "disappearance_municipality_id": row.get("disappearance_municipality_id"),
            "status_id": row.get("status_id"),
            "location_date": row.get("location_date"),
            "location_condition_id": row.get("location_condition_id"),
            "location_classification_id": row.get("location_classification_id"),
            "location_state_name": row.get("location_state_name"),
            "location_municipality_id": row.get("location_municipality_id"),
            "closure_date": row.get("closure_date"),
            "closure_type_id": row.get("closure_type_id"),
            "linked_feb": row.get("linked_feb"),
            "has_investigation_folder": row.get("has_investigation_folder"),
            "record_hash": row.get("record_hash"),
        }
