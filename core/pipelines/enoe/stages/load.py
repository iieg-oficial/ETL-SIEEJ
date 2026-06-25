from pathlib import Path
from typing import Any, Optional

import pandas as pd
from sqlalchemy import select, func

from core.db import Database
from core.pipelines.stage import Stage
from core.pipelines.enoe.attributes import EnoeTables as T
from core.pipelines.enoe.config import settings
from core.pipelines.enoe.schemas import (
    CatEstadoCivil,
    CatNivelEducativo,
    CatOcupacion,
    CatSector,
    CatSituacionTrabajo,
    CatTipoLocalidad,
    StgEnoe,
)
from core.utils.bulk_ops import count_records, insert_records
from core.utils.files import cleanup_pipeline_data
from core.utils.logger import get_logger

PIPELINE_NAME = settings.PIPELINE_NAME

_CATALOG_MAP = [
    (T.CAT_SECTOR, CatSector, CatSector.id.key),
    (T.CAT_OCUPACION, CatOcupacion, CatOcupacion.id.key),
    (T.CAT_SITUACION_TRABAJO, CatSituacionTrabajo, CatSituacionTrabajo.id.key),
    (T.CAT_TIPO_LOCALIDAD, CatTipoLocalidad, CatTipoLocalidad.id.key),
    (T.CAT_ESTADO_CIVIL, CatEstadoCivil, CatEstadoCivil.id.key),
    (T.CAT_NIVEL_EDUCATIVO, CatNivelEducativo, CatNivelEducativo.id.key),
]


class EnoeLoad(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode
        self.logger = get_logger(f"{PIPELINE_NAME}.load")
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> list[dict]:
        transform_dir = Path(f"data/transform/{PIPELINE_NAME}")
        pkls = sorted(transform_dir.glob("enoe_*.pkl"))
        if pkls:
            periods = []
            for df_pkl in pkls:
                stem = df_pkl.stem  # enoe_{anio}_{t}
                cat_pkl = transform_dir / f"catalogs_{stem[5:]}.pkl"
                if cat_pkl.exists():
                    periods.append({"df_path": df_pkl, "catalogs_path": cat_pkl})
            self.logger.info(f"[source] Found {len(periods)} transform pkls")
            return periods
        if isinstance(input_data, list):
            return input_data
        return []

    def _period_exists(self, session, anio: int, trimestre: int) -> bool:
        result = session.execute(
            select(func.count()).select_from(StgEnoe).where(
                StgEnoe.anio == anio, StgEnoe.trimestre == trimestre
            )
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
                records_before = count_records(session, StgEnoe)

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

                cols = [c for c in StgEnoe.columns() if c != StgEnoe.id.key]
                records = df[cols].astype(object).where(df[cols].notna(), None).to_dict("records")

                with self.db.get_session() as session:
                    insert_records(
                        session,
                        records,
                        StgEnoe,
                        conflict_keys=[
                            StgEnoe.anio.key,
                            StgEnoe.trimestre.key,
                            StgEnoe.cd_a.key,
                            StgEnoe.entidad_id.key,
                            StgEnoe.con.key,
                            StgEnoe.v_sel.key,
                            StgEnoe.n_hog.key,
                            StgEnoe.h_mud.key,
                            StgEnoe.n_ent.key,
                            StgEnoe.n_ren.key,
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
                total = count_records(session, StgEnoe)
            inserted = total - input_data["records_before"]
            self.logger.info(f"[finalization] {total:,} rows in {StgEnoe.__tablename__}")
            self.logger.info(f"[finalization] {inserted:,} rows inserted")
        finally:
            self.db.disconnect()
            cleanup_pipeline_data(PIPELINE_NAME)
        return input_data
