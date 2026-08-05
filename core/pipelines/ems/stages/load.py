from datetime import date
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.db import Database
from core.pipelines.ems.attributes import EmsTables as T
from core.pipelines.ems.config import PIPELINE_NAME, settings
from core.pipelines.ems.constants import CONFLICT_KEYS
from core.pipelines.ems.schemas import CatActividad, CatEstatus, StgEms
from core.pipelines.stage import Stage
from core.utils import df_to_records, normalize_text
from core.utils.bulk_ops import count_records, get_mapping, insert_records, sync_id_sequence, upsert_records
from core.utils.files import cleanup_pipeline_data


class EmsLoad(Stage):
    """Load the catalogs, resolve the status FK and upsert the staging table."""

    def __init__(self):
        super().__init__(PIPELINE_NAME, "load")
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> dict[str, Any]:
        base = Path(f"data/transform/{settings.PIPELINE_NAME}")
        pkl_df, pkl_catalogs = base / "transform.pkl", base / "catalogs.pkl"

        if pkl_df.exists() and pkl_catalogs.exists():
            self.logger.info("Loading transform pkl files")
            return {"df": pd.read_pickle(pkl_df), "catalogs": pd.read_pickle(pkl_catalogs)}

        return input_data

    def _load_catalogs(self, session, catalogs: dict[str, list[dict]]) -> dict[str, int]:
        """Insert the catalogs and return the normalized status -> id mapping read from the DB.

        cat_estatus ids are assigned by PostgreSQL (SERIAL) and never by the
        DataFrame, so a new status in the source cannot shift ids already
        referenced by stg_ems. cat_actividad is upserted instead of skipped
        because INEGI does reword the SCIAN descriptions between editions, while
        codigo_actividad — the key stg_ems points at — stays put.
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

    def action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        df = input_data["df"]
        if df.empty:
            self.logger.warning("No data to load")
            return {"records_before": None}

        try:
            self.db.connect()
            with self.db.get_session() as session:
                estatus_mapping = self._load_catalogs(session, input_data["catalogs"])
                df = self._resolve_estatus(df.copy(), estatus_mapping)
                df["fecha_actualizacion"] = date.today()

                records_before = count_records(session, StgEms)

                stg_cols = [c for c in StgEms.columns() if c != StgEms.id.key]
                df = df.drop_duplicates(subset=CONFLICT_KEYS, keep="last")
                df_clean = df.astype(object).where(df.notna(), None)
                upsert_records(
                    session,
                    df_to_records(df_clean, stg_cols),
                    StgEms,
                    conflict_keys=CONFLICT_KEYS,
                    chunk_size=settings.CHUNK_SIZE,
                )
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
                total = count_records(session, StgEms)
                inserted = total - input_data["records_before"]
            self.logger.info(f"{total:,} records in stg_ems ({inserted:,} new in this run)")
        finally:
            self.db.disconnect()
