import pandas as pd
from pathlib import Path
from sqlalchemy import select
from typing import Any, Optional

from core.db import Database
from core.pipelines.agropecuario_siap.attributes import AgropecuarioTables as T
from core.pipelines.agropecuario_siap.config import settings
from core.pipelines.agropecuario_siap.schemas import (
    CatCiclos,
    CatCtrsApoyoDesRural,
    CatCultivos,
    CatDistritosDesRural,
    CatModalidades,
    CatUnidadesMedida,
    StgAgricola,
)
from core.pipelines.stage import Stage
from core.utils import df_to_records
from core.utils.bulk_ops import count_records, insert_records, upsert_records
from core.utils.files import cleanup_pipeline_data
from core.utils.logger import get_logger


class AgropecuarioLoad(Stage):
    def __init__(self, year: int):
        super().__init__(settings.PIPELINE_NAME, "load")
        self.year = year
        self.logger = get_logger(f"{settings.PIPELINE_NAME}.load")
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> dict[str, Any]:
        pkl_path = Path(f"data/transform/{settings.PIPELINE_NAME}/transform_{self.year}.pkl")
        pkl_catalogs = Path(f"data/transform/{settings.PIPELINE_NAME}/catalogs_{self.year}.pkl")

        if pkl_path.exists() and pkl_catalogs.exists():
            self.logger.info(f"Loading transform pkl files for {self.year}")
            return {
                "df": pd.read_pickle(pkl_path),
                "catalogs": pd.read_pickle(pkl_catalogs),
            }

        return input_data

    def _catalog_map(self, session, model, name_col: str) -> dict:
        col = getattr(model, name_col)
        rows = session.execute(select(col, model.id)).all()
        return {name: id_ for name, id_ in rows}

    def _load_catalogs(self, session, catalogs: dict) -> None:
        insert_records(session, catalogs[T.CAT_CULTIVOS], CatCultivos, conflict_keys=[CatCultivos.cultivo.key])
        insert_records(
            session, catalogs[T.CAT_UNIDADES_MEDIDA], CatUnidadesMedida, conflict_keys=[CatUnidadesMedida.id.key]
        )
        insert_records(session, catalogs[T.CAT_MODALIDADES], CatModalidades, conflict_keys=[CatModalidades.id.key])
        insert_records(session, catalogs[T.CAT_CICLOS], CatCiclos, conflict_keys=[CatCiclos.id.key])
        insert_records(
            session,
            catalogs[T.CAT_CTRS_APOYO_DES_RURAL],
            CatCtrsApoyoDesRural,
            conflict_keys=[CatCtrsApoyoDesRural.ctr_apoyo_des_rural.key],
        )
        insert_records(
            session,
            catalogs[T.CAT_DISTRITOS_DES_RURAL],
            CatDistritosDesRural,
            conflict_keys=[CatDistritosDesRural.id.key],
        )
        self.logger.info(f"All catalogs loaded for {self.year}")

    def _remap_fks(self, session, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["cultivo_id"] = df["cultivo"].map(self._catalog_map(session, CatCultivos, "cultivo"))
        df["ctr_apoyo_des_rural_id"] = df["ctr_apoyo_des_rural"].map(
            self._catalog_map(session, CatCtrsApoyoDesRural, "ctr_apoyo_des_rural")
        )
        return df

    def action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        df = input_data["df"]
        catalogs = input_data["catalogs"]

        if df.empty:
            self.logger.info("Empty input, skipping load")
            return {"records_before": None}

        self.logger.info(f"Loading {len(df)} rows for {self.year}")

        try:
            self.db.connect()
            with self.db.get_session() as session:
                self._load_catalogs(session, catalogs)
                df = self._remap_fks(session, df)

                records_before = count_records(session, StgAgricola)

                agricola_cols = [c for c in StgAgricola.columns() if c != StgAgricola.id.key]
                conflict_keys = [
                    "anio",
                    "entidad_id",
                    "municipio_id",
                    "distrito_des_rural_id",
                    "ctr_apoyo_des_rural_id",
                    "cultivo_id",
                    "tipo_ciclo_id",
                    "modalidad_id",
                ]
                df = df.drop_duplicates(subset=conflict_keys, keep="last")
                df_clean = df.astype(object).where(df.notna(), None)
                upsert_records(
                    session,
                    df_to_records(df_clean, agricola_cols),
                    StgAgricola,
                    conflict_keys=conflict_keys,
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
                total = count_records(session, StgAgricola)
                inserted = total - input_data["records_before"]
            self.logger.info(f"{total:,} stg_agricola in database ({inserted:,} upserted for {self.year})")
        finally:
            self.db.disconnect()
