import pandas as pd
from datetime import date
from pathlib import Path
from typing import Any, Optional

from core.db import Database
from core.pipelines.enec.attributes import EnecTables as T
from core.pipelines.enec.config import PIPELINE_NAME, settings
from core.pipelines.enec.constants import ENTIDAD_CONFLICT_KEYS, NACIONAL_CONFLICT_KEYS
from core.pipelines.enec.schemas import CatActividad, CatEstatus, StgEnecEntidad, StgEnecNacional
from core.pipelines.stage import Stage
from core.utils import df_to_records, normalize_text
from core.utils.bulk_ops import count_records, get_mapping, insert_records, sync_id_sequence, upsert_records
from core.utils.files import cleanup_pipeline_data


class EnecLoad(Stage):
    """Load the catalogs, resolve the status FK and upsert both staging tables."""

    def __init__(self):
        super().__init__(PIPELINE_NAME, "load")
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> dict[str, Any]:
        base = Path(f"data/transform/{settings.PIPELINE_NAME}")
        pkl_nacional, pkl_entidad, pkl_catalogs = base / "nacional.pkl", base / "entidad.pkl", base / "catalogs.pkl"

        if pkl_nacional.exists() and pkl_entidad.exists() and pkl_catalogs.exists():
            self.logger.info("Loading transform pkl files")
            return {
                "nacional": pd.read_pickle(pkl_nacional),
                "entidad": pd.read_pickle(pkl_entidad),
                "catalogs": pd.read_pickle(pkl_catalogs),
            }

        return input_data

    def _load_catalogs(self, session, catalogs: dict[str, list[dict]]) -> dict[str, int]:
        """Insert the catalogs and return the normalized status -> id mapping read from the DB.

        cat_estatus ids are assigned by PostgreSQL (SERIAL) and never by the
        DataFrame, so a new status in the source cannot shift ids already
        referenced by the staging tables. cat_actividad is upserted because
        INEGI does reword descriptions between editions, while codigo_actividad
        — the key both staging tables point at — stays put.
        """
        insert_records(session, catalogs[T.CAT_ESTATUS], CatEstatus, conflict_keys=["estatus"])
        sync_id_sequence(session, CatEstatus)

        upsert_records(
            session,
            catalogs[T.CAT_ACTIVIDAD],
            CatActividad,
            conflict_keys=["codigo_actividad"],
            chunk_size=settings.CHUNK_SIZE,
        )
        sync_id_sequence(session, CatActividad)

        return get_mapping(session, CatEstatus, "estatus", CatEstatus.id.key, is_normalize=True)

    def _resolve_estatus(self, df: pd.DataFrame, mapping: dict[str, int]) -> pd.DataFrame:
        df["estatus_id"] = df["estatus"].map(normalize_text).map(mapping).astype("Int64")

        unresolved = int(df["estatus_id"].isna().sum() - df["estatus"].isna().sum())
        if unresolved > 0:
            self.logger.warning(f"{unresolved:,} 'estatus' values with no match in cat_estatus")
        return df

    def _upsert(self, session, df: pd.DataFrame, model, conflict_keys: list[str], mapping: dict[str, int]) -> None:
        if df.empty:
            self.logger.warning(f"No rows to load into {model.__tablename__}")
            return

        df = self._resolve_estatus(df.copy(), mapping)
        df["fecha_actualizacion"] = date.today()

        cols = [c for c in model.columns() if c != model.id.key]
        df = df.drop_duplicates(subset=conflict_keys, keep="last")
        df_clean = df.astype(object).where(df.notna(), None)
        upsert_records(
            session,
            df_to_records(df_clean, cols),
            model,
            conflict_keys=conflict_keys,
            chunk_size=settings.CHUNK_SIZE,
        )

    def action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        nacional, entidad = input_data["nacional"], input_data["entidad"]
        if nacional.empty and entidad.empty:
            self.logger.warning("No data to load")
            return {"records_before": None}

        try:
            self.db.connect()
            with self.db.get_session() as session:
                mapping = self._load_catalogs(session, input_data["catalogs"])

                records_before = {
                    T.STG_ENEC_NACIONAL: count_records(session, StgEnecNacional),
                    T.STG_ENEC_ENTIDAD: count_records(session, StgEnecEntidad),
                }

                self._upsert(session, nacional, StgEnecNacional, NACIONAL_CONFLICT_KEYS, mapping)
                self._upsert(session, entidad, StgEnecEntidad, ENTIDAD_CONFLICT_KEYS, mapping)
        except Exception:
            self.db.disconnect()
            raise

        return {"records_before": records_before}

    def finalization(self, input_data: dict[str, Any]) -> None:
        cleanup_pipeline_data(settings.PIPELINE_NAME)
        if input_data is None or input_data.get("records_before") is None:
            return
        try:
            with self.db.get_session() as session:
                for table, model in ((T.STG_ENEC_NACIONAL, StgEnecNacional), (T.STG_ENEC_ENTIDAD, StgEnecEntidad)):
                    total = count_records(session, model)
                    inserted = total - input_data["records_before"][table]
                    self.logger.info(f"{total:,} records in {table} ({inserted:,} new in this run)")
        finally:
            self.db.disconnect()
