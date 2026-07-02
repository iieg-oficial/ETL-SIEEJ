from pathlib import Path
from typing import Any, Optional

import pandas as pd
from sqlalchemy import func, select, text

from core.db import Database
from core.pipelines.stage import Stage
from core.pipelines.enoe_microdatos.attributes import EnoeMicrodatosTables as T
from core.pipelines.enoe_microdatos.config import settings
from core.pipelines.enoe_microdatos.schemas import (
    CatEnoeOcupacion,
    CatEnoeSecor,
    CatEnoeSituacionTrabajo,
    StgEnoeMicrodatos,
)
from core.utils.bulk_ops import count_records, insert_records
from core.utils.files import cleanup_pipeline_data
from core.utils.logger import get_logger

PIPELINE_NAME = settings.PIPELINE_NAME

_CATALOG_MAP = [
    (T.CAT_ENOE_SECTOR, CatEnoeSecor, CatEnoeSecor.id.key),
    (T.CAT_ENOE_OCUPACION, CatEnoeOcupacion, CatEnoeOcupacion.id.key),
    (T.CAT_ENOE_SITUACION_TRABAJO, CatEnoeSituacionTrabajo, CatEnoeSituacionTrabajo.id.key),
]


class EnoeMicrodatosLoad(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode
        self.logger = get_logger(f"{PIPELINE_NAME}.load")
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> list[dict]:
        transform_dir = Path(f"data/transform/{PIPELINE_NAME}")
        pkls = sorted(transform_dir.glob("enoe_microdatos_*.pkl"))
        if pkls:
            periods = []
            for df_pkl in pkls:
                stem = df_pkl.stem  # enoe_microdatos_{anio}_{t}
                suffix = stem[len("enoe_microdatos_"):]  # {anio}_{t}
                cat_pkl = transform_dir / f"catalogs_{suffix}.pkl"
                if cat_pkl.exists():
                    periods.append({"df_path": df_pkl, "catalogs_path": cat_pkl})
            self.logger.info(f"[source] Found {len(periods)} transform pkls")
            return periods
        if isinstance(input_data, list):
            return input_data
        return []

    def _period_exists(self, session, anio: int, trimestre: int) -> bool:
        result = session.execute(
            select(func.count())
            .select_from(StgEnoeMicrodatos)
            .where(StgEnoeMicrodatos.anio == anio, StgEnoeMicrodatos.trimestre == trimestre)
        ).scalar()
        return (result or 0) > 0

    def _load_catalogs(self, session, catalogs: dict) -> None:
        for table_key, model, conflict_key in _CATALOG_MAP:
            records = catalogs.get(table_key, [])
            if records:
                insert_records(session, records, model, conflict_keys=[conflict_key])

    def action(self, input_data: list[dict]) -> dict:
        if not input_data:
            self.logger.info("[action] No transform data to load")
            return {}

        self.db.connect()
        try:
            with self.db.get_session() as session:
                records_before = count_records(session, StgEnoeMicrodatos)

            for period in input_data:
                df = pd.read_pickle(period["df_path"])
                catalogs = pd.read_pickle(period["catalogs_path"]).to_dict()

                if df.empty:
                    continue

                anio = int(df["anio"].iloc[0])
                trimestre = int(df["trimestre"].iloc[0])

                with self.db.get_session() as session:
                    if self._period_exists(session, anio, trimestre):
                        self.logger.info(f"[action] {anio} T{trimestre} already loaded, skipping")
                        continue
                    self._load_catalogs(session, catalogs)

                cols = [c for c in StgEnoeMicrodatos.columns() if c != StgEnoeMicrodatos.id.key]
                for col in cols:
                    if col not in df.columns:
                        df[col] = pd.NA
                records = df[cols].astype(object).where(df[cols].notna(), None).to_dict("records")

                with self.db.get_session() as session:
                    insert_records(
                        session,
                        records,
                        StgEnoeMicrodatos,
                        conflict_keys=[
                            StgEnoeMicrodatos.anio.key,
                            StgEnoeMicrodatos.trimestre.key,
                            StgEnoeMicrodatos.cd_a.key,
                            StgEnoeMicrodatos.entidad_id.key,
                            StgEnoeMicrodatos.con.key,
                            StgEnoeMicrodatos.v_sel.key,
                            StgEnoeMicrodatos.n_hog.key,
                            StgEnoeMicrodatos.h_mud.key,
                            StgEnoeMicrodatos.n_ent.key,
                            StgEnoeMicrodatos.n_ren.key,
                        ],
                    )

                self.logger.info(f"[action] Loaded {len(records):,} rows for {anio} T{trimestre}")

        except Exception:
            self.db.disconnect()
            raise

        return {"records_before": records_before}

    def finalization(self, input_data: dict) -> dict:
        if not input_data:
            return input_data
        try:
            with self.db.get_session() as session:
                total = count_records(session, StgEnoeMicrodatos)
            inserted = total - input_data["records_before"]
            self.logger.info(f"[finalization] {total:,} rows in {StgEnoeMicrodatos.__tablename__}")
            self.logger.info(f"[finalization] {inserted:,} rows inserted")
            with self.db.get_session() as session:
                session.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_enoe_microdatos"))
                session.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_enoe_tasas"))
                session.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_enoe_tasas_jalisco"))
            self.logger.info("[finalization] materialized views refreshed")
        finally:
            self.db.disconnect()
            cleanup_pipeline_data(PIPELINE_NAME)
        return input_data
