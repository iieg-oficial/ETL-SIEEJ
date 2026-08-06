from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.db import Database
from core.pipelines.conapo.attributes import ConapoTables as T
from core.pipelines.conapo.config import settings
from core.pipelines.conapo.queries import MATERIALIZED_VIEWS
from core.pipelines.conapo.schemas import (
    CatSexo,
    StgGrandesGruposEdad,
    StgIndicadoresDemograficos,
    StgPoblacionMitadAnio,
)
from core.pipelines.stage import Stage
from core.utils import df_to_records
from core.utils.bulk_ops import (
    bulk_insert,
    count_records,
    insert_records,
    sync_id_sequence,
)
from core.utils.files import cleanup_pipeline_data
from core.utils.logger import get_logger
from core.utils.views import refresh_materialized_views


class ConapoLoad(Stage):
    def __init__(self):
        super().__init__("conapo", "load")
        self.logger = get_logger("conapo.load")
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> dict[str, Any]:
        pkl_pma = Path("data/transform/conapo/pma.pkl")
        pkl_gge = Path("data/transform/conapo/gge.pkl")
        pkl_idd = Path("data/transform/conapo/idd.pkl")
        pkl_catalogs = Path("data/transform/conapo/catalogs.pkl")

        if pkl_pma.exists() and pkl_gge.exists() and pkl_idd.exists() and pkl_catalogs.exists():
            self.logger.info("[source] Loading transform pkl files")
            return {
                "df_pma": pd.read_pickle(pkl_pma),
                "df_gge": pd.read_pickle(pkl_gge),
                "df_idd": pd.read_pickle(pkl_idd),
                "catalogs": pd.read_pickle(pkl_catalogs),
            }

        return input_data

    def _load_catalogs(self, session, catalogs: dict) -> None:
        """Load catalog tables."""
        insert_records(
            session,
            catalogs[T.CAT_SEXO],
            CatSexo,
            conflict_keys=[CatSexo.id.key],
        )
        self.logger.info("[_load_catalogs] Catalogs loaded")

    def action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        df_pma = input_data["df_pma"]
        df_gge = input_data["df_gge"]
        df_idd = input_data["df_idd"]

        if df_pma.empty and df_gge.empty and df_idd.empty:
            self.logger.info("[action] Empty input, skipping load")
            return None

        self.logger.info(f"[action] Loading {len(df_pma)} PMA, {len(df_gge)} GGE, {len(df_idd)} IDD rows")

        try:
            self.db.connect()
            with self.db.get_session() as session:
                self._load_catalogs(session, input_data["catalogs"])

                records_before_pma = count_records(session, StgPoblacionMitadAnio)
                records_before_gge = count_records(session, StgGrandesGruposEdad)
                records_before_idd = count_records(session, StgIndicadoresDemograficos)

                # Load PMA
                sync_id_sequence(session, StgPoblacionMitadAnio)
                if not df_pma.empty:
                    pma_cols = [c for c in StgPoblacionMitadAnio.columns() if c != StgPoblacionMitadAnio.id.key]
                    bulk_insert(
                        session,
                        df_to_records(df_pma.astype(object).where(df_pma.notna(), None), pma_cols),
                        StgPoblacionMitadAnio,
                    )

                # Load GGE
                sync_id_sequence(session, StgGrandesGruposEdad)
                if not df_gge.empty:
                    gge_cols = [c for c in StgGrandesGruposEdad.columns() if c != StgGrandesGruposEdad.id.key]
                    bulk_insert(
                        session,
                        df_to_records(df_gge.astype(object).where(df_gge.notna(), None), gge_cols),
                        StgGrandesGruposEdad,
                    )

                # Load IDD
                sync_id_sequence(session, StgIndicadoresDemograficos)
                if not df_idd.empty:
                    idd_cols = [
                        c for c in StgIndicadoresDemograficos.columns() if c != StgIndicadoresDemograficos.id.key
                    ]
                    bulk_insert(
                        session,
                        df_to_records(df_idd.astype(object).where(df_idd.notna(), None), idd_cols),
                        StgIndicadoresDemograficos,
                    )

            refresh_materialized_views(self.db, MATERIALIZED_VIEWS)

        except Exception:
            self.db.disconnect()
            raise

        return {
            "data": input_data,
            "records_before_pma": records_before_pma,
            "records_before_gge": records_before_gge,
            "records_before_idd": records_before_idd,
        }

    def finalization(self, input_data: Any) -> Any:
        cleanup_pipeline_data("conapo")
        if input_data is None:
            return None
        try:
            with self.db.get_session() as session:
                total_pma = count_records(session, StgPoblacionMitadAnio)
                total_gge = count_records(session, StgGrandesGruposEdad)
                total_idd = count_records(session, StgIndicadoresDemograficos)
                inserted_pma = total_pma - input_data["records_before_pma"]
                inserted_gge = total_gge - input_data["records_before_gge"]
                inserted_idd = total_idd - input_data["records_before_idd"]
            self.logger.info(
                f"[finalization] {total_pma:,} stg_poblacion_mitad_anio in database ({inserted_pma:,} inserted)"
            )
            self.logger.info(
                f"[finalization] {total_gge:,} stg_grandes_grupos_edad in database ({inserted_gge:,} inserted)"
            )
            self.logger.info(
                f"[finalization] {total_idd:,} stg_indicadores_demograficos in database ({inserted_idd:,} inserted)"
            )
        finally:
            self.db.disconnect()

        return input_data["data"]
