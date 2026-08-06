from datetime import date
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.db import Database
from core.pipelines.rastros.attributes import RastrosTables as T
from core.pipelines.rastros.config import PIPELINE_NAME, settings
from core.pipelines.rastros.constants import CATALOG_FK_RESOLUTION, CATALOG_TEXT_COLS, CONFLICT_KEYS
from core.pipelines.rastros.schemas import (
    CatEspeciesGanaderas,
    CatEstatus,
    CatTipoCifra,
    StgRastros,
)
from core.pipelines.stage import Stage
from core.utils import df_to_records, normalize_text
from core.utils.bulk_ops import count_records, get_mapping, insert_records, sync_id_sequence, upsert_records
from core.utils.files import cleanup_pipeline_data


class RastrosLoad(Stage):
    """Load catalogs, resolve FKs against the database and upsert the staging table."""

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

    def _load_catalogs(self, session, catalogs: dict[str, list[dict]]) -> dict[str, dict]:
        """Insert the catalogs and return the normalized-text -> id mapping read back from the DB.

        Ids are assigned by PostgreSQL (SERIAL), never by the DataFrame: that way a
        new value in the source cannot shift ids already referenced by the staging table.
        """
        models = {
            T.CAT_ESTATUS: CatEstatus,
            T.CAT_ESPECIES_GANADERAS: CatEspeciesGanaderas,
            T.CAT_TIPO_CIFRA: CatTipoCifra,
        }

        mappings = {}
        for table, text_col in CATALOG_TEXT_COLS.items():
            model = models[table]
            insert_records(session, catalogs[table], model, conflict_keys=[text_col])
            sync_id_sequence(session, model)
            mappings[table] = get_mapping(session, model, text_col, model.id.key, is_normalize=True)
        return mappings

    def _resolve_foreign_keys(self, df: pd.DataFrame, mappings: dict[str, dict]) -> pd.DataFrame:
        for text_col, (table, fk_col) in CATALOG_FK_RESOLUTION.items():
            mapping = mappings[table]
            df[fk_col] = df[text_col].map(normalize_text).map(mapping).astype("Int64")

            unresolved = int(df[fk_col].isna().sum() - df[text_col].isna().sum())
            if unresolved > 0:
                self.logger.warning(f"{unresolved:,} '{text_col}' values with no match in their catalog")
        return df

    def action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        df = input_data["df"]
        if df.empty:
            self.logger.warning("No data to load")
            return {"records_before": None}

        try:
            self.db.connect()
            with self.db.get_session() as session:
                mappings = self._load_catalogs(session, input_data["catalogs"])
                df = self._resolve_foreign_keys(df.copy(), mappings)
                df["fecha_actualizacion"] = date.today()

                records_before = count_records(session, StgRastros)

                stg_cols = [c for c in StgRastros.columns() if c != StgRastros.id.key]
                df = df.drop_duplicates(subset=CONFLICT_KEYS, keep="last")
                df_clean = df.astype(object).where(df.notna(), None)
                upsert_records(
                    session,
                    df_to_records(df_clean, stg_cols),
                    StgRastros,
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
                total = count_records(session, StgRastros)
                inserted = total - input_data["records_before"]
            self.logger.info(f"{total:,} records in stg_rastros ({inserted:,} new in this run)")
        finally:
            self.db.disconnect()
