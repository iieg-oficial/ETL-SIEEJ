from pathlib import Path
from typing import Optional

import pandas as pd
from more_itertools import chunked
from sqlalchemy.dialects.postgresql import insert

from core.db import Database
from core.pipelines.stage import Stage
from core.pipelines.ilmm.config import settings
from core.pipelines.ilmm.queries import MATERIALIZED_VIEWS
from core.pipelines.ilmm.schemas import Ilmm, IlmmEstimador
from core.utils.bulk_ops import count_records
from core.utils.files import cleanup_pipeline_data
from core.utils.views import refresh_materialized_views


class IlmmLoad(Stage):
    def __init__(self):
        super().__init__("ilmm", "load")
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(
        self, input_data: Optional[tuple[pd.DataFrame, pd.DataFrame | None]] = None
    ) -> tuple[pd.DataFrame, pd.DataFrame | None]:
        pkl_path = Path("data/transform/ilmm/ilmm_transformed.pkl")
        est_path = Path("data/extract/ilmm/cat_estimador.pkl")
        if pkl_path.exists():
            self.logger.info(f"[source] Loading {pkl_path}")
            df = pd.read_pickle(pkl_path)
            df_est = pd.read_pickle(est_path) if est_path.exists() else None
            return df, df_est
        self.logger.info("[source] pkl not found, using transform output")
        return input_data

    def _seed_estimador(self, session, df_est: pd.DataFrame) -> None:
        records = [{"id": int(row["cve"]), "descripcion": str(row["descrip"])} for _, row in df_est.iterrows()]
        stmt = insert(IlmmEstimador).values(records).on_conflict_do_nothing(index_elements=["id"])
        session.execute(stmt)
        session.flush()
        self.logger.info(f"[action] Seeded {len(records)} rows into {IlmmEstimador.__tablename__}")

    def _refresh_views(self) -> None:
        refresh_materialized_views(self.db, MATERIALIZED_VIEWS)
        self.logger.info("[action] materialized views refreshed")

    def action(self, input_data: tuple[pd.DataFrame, pd.DataFrame | None]) -> dict:
        df, df_est = input_data
        self.logger.info(f"[action] Loading {len(df)} rows into DB")

        if df.empty:
            self.logger.info("[action] Empty DataFrame — nothing to insert")
            return {"df": df, "records_before": 0}

        cols = [c for c in Ilmm.columns() if c != Ilmm.id.key]
        df_safe = df[cols].astype(object).where(df[cols].notna(), None)
        records = df_safe.to_dict("records")

        try:
            self.db.connect()
            with self.db.get_session() as session:
                if df_est is not None:
                    self._seed_estimador(session, df_est)

                records_before = count_records(session, Ilmm)

                total = len(records)
                conflict_cols = ["clave_municipio", "fecha", "estimador_id"]
                chunk_size = 5_000
                for i, chunk in enumerate(chunked(records, chunk_size), start=1):
                    stmt = insert(Ilmm).values(chunk).on_conflict_do_nothing(index_elements=conflict_cols)
                    session.execute(stmt)
                    session.flush()
                    self.logger.info(f"  chunk {i}: {min(i * chunk_size, total)}/{total}")

            self._refresh_views()

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
