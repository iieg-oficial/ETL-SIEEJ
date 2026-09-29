from pathlib import Path
from typing import Any, Optional

import pandas as pd
from sqlalchemy import delete, text

from core.constants.geo import JALISCO_CVE_ENTIDAD
from core.db import Database
from core.pipelines.fosas_clandestinas.config import settings
from core.pipelines.fosas_clandestinas.constants import PIPELINE_NAME, PUBLICACIONES_FILE, STG_FILE
from core.pipelines.fosas_clandestinas.queries import MATERIALIZED_VIEWS
from core.pipelines.fosas_clandestinas.schemas import CatPublicaciones, StgFosasClandestinas
from core.pipelines.stage import Stage
from core.utils.bulk_ops import bulk_insert, count_records, get_cvegeo_mapping, get_mapping, upsert_records
from core.utils.files import cleanup_pipeline_data
from core.utils.views import refresh_materialized_views


class FosasClandestinasLoad(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode
        self.db = Database(settings.DB_NAME, settings.database_url)
        self.transform_dir = Path(f"data/transform/{PIPELINE_NAME}")

    def source(self, input_data: Optional[Any] = None) -> dict[str, pd.DataFrame]:
        paths = {"publicaciones": self.transform_dir / PUBLICACIONES_FILE, "stg": self.transform_dir / STG_FILE}
        return {key: pd.read_pickle(path) if path.exists() else pd.DataFrame() for key, path in paths.items()}

    def _resolve_keys(self, session, stg: pd.DataFrame) -> pd.DataFrame:
        publicaciones = get_mapping(session, CatPublicaciones, "fecha_corte", "id")
        municipios = get_cvegeo_mapping(session, cve_ent=JALISCO_CVE_ENTIDAD, is_normalize=True)

        stg = stg.copy()
        stg["publicacion_id"] = stg["fecha_corte"].map(publicaciones)
        stg["cve_ent"] = JALISCO_CVE_ENTIDAD
        stg["cve_mun"] = stg["municipio"].map(municipios).astype("Int64")

        unresolved = stg.loc[stg["cve_mun"].isna(), "municipio"].unique().tolist()
        if unresolved:
            self.logger.warning(f"[action] Unresolved municipios: {unresolved}")

        columns = StgFosasClandestinas.columns()
        return stg[columns].astype(object).where(stg[columns].notna(), None)

    def action(self, input_data: dict[str, pd.DataFrame]) -> int | None:
        publicaciones, stg = input_data["publicaciones"], input_data["stg"]
        if publicaciones.empty:
            self.logger.info("[action] No data to load")
            return None

        self.db.connect()
        with self.db.get_session() as session:
            if self.mode == "bootstrap":
                session.execute(
                    text(
                        f"TRUNCATE {StgFosasClandestinas.__tablename__}, {CatPublicaciones.__tablename__} RESTART IDENTITY"
                    )
                )

            upsert_records(session, publicaciones.to_dict("records"), CatPublicaciones, conflict_keys=["fecha_corte"])
            stg = self._resolve_keys(session, stg)

            # Each publication is replaced whole, so reruns are idempotent
            ids = stg["publicacion_id"].unique().tolist()
            session.execute(delete(StgFosasClandestinas).where(StgFosasClandestinas.publicacion_id.in_(ids)))
            bulk_insert(session, stg.to_dict("records"), StgFosasClandestinas)

        refresh_materialized_views(self.db, MATERIALIZED_VIEWS)
        self.logger.info(f"[action] {len(publicaciones)} publications, {len(stg)} rows loaded")
        return len(stg)

    def finalization(self, input_data: int | None) -> int | None:
        cleanup_pipeline_data(PIPELINE_NAME)
        if input_data is None:
            return None
        try:
            with self.db.get_session() as session:
                for model in (CatPublicaciones, StgFosasClandestinas):
                    count_records(session, model)
        finally:
            self.db.disconnect()
        return input_data
