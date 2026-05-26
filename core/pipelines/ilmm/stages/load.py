from pathlib import Path
from typing import Optional

import pandas as pd
from more_itertools import chunked
from sqlalchemy.dialects.postgresql import insert

from core.db import Database
from core.pipelines.stage import Stage
from core.pipelines.ilmm.config import settings
from core.pipelines.ilmm.schemas import Ilmm
from core.utils.bulk_ops import count_records
from core.utils.files import cleanup_pipeline_data


class IlmmLoad(Stage):
    def __init__(self):
        super().__init__("ilmm", "load")
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(self, input_data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        pkl_path = Path("data/transform/ilmm/ilmm_transformed.pkl")
        if pkl_path.exists():
            self.logger.info(f"[source] Loading {pkl_path}")
            return pd.read_pickle(pkl_path)
        self.logger.info("[source] pkl not found, using transform output")
        return input_data

    def action(self, df: pd.DataFrame) -> dict:
        self.logger.info(f"[action] Loading {len(df)} rows into DB")

        if df.empty:
            self.logger.info("[action] Empty DataFrame — nothing to insert")
            return {"df": df, "records_before": 0}

        cols = [c for c in Ilmm.columns() if c != Ilmm.id.key]

        # Convert any pd.NA / numpy NaN to None before building records
        df_safe = df[cols].astype(object).where(df[cols].notna(), None)
        records = df_safe.to_dict("records")

        try:
            self.db.connect()
            with self.db.get_session() as session:
                records_before = count_records(session, Ilmm)

                total = len(records)
                conflict_cols = ["clave_municipio", "fecha", "indicador_id"]
                chunk_size = 5_000
                for i, chunk in enumerate(chunked(records, chunk_size), start=1):
                    stmt = insert(Ilmm).values(chunk).on_conflict_do_nothing(index_elements=conflict_cols)
                    session.execute(stmt)
                    session.flush()
                    self.logger.info(f"  chunk {i}: {min(i * chunk_size, total)}/{total}")

        except Exception:
            self.db.disconnect()
            raise

        return {"df": df, "records_before": records_before}

    def finalization(self, input_data: dict) -> dict:
        cleanup_pipeline_data("ilmm")
        try:
            with self.db.get_session() as session:
                total = count_records(session, Ilmm)
                inserted = total - input_data["records_before"]
                self.logger.info(f"[finalization] ilmm: {format(total, ',')} total, {format(inserted, ',')} inserted")
        finally:
            self.db.disconnect()

        return input_data["df"]
