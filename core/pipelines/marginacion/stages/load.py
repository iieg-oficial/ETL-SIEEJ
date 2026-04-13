import numpy as np
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.db import Database
from core.pipelines.marginacion.attributes import MarginacionTables as T
from core.pipelines.marginacion.config import settings
from core.pipelines.marginacion.mappings import GradosMarginacion as GradosMarginacionMap
from core.pipelines.marginacion.schemas import (
    GradosMarginacion,
    Localidades,
    MarginacionesLocalidades,
    MarginacionesMunicipales,
)
from core.pipelines.stage import Stage
from core.utils import df_to_records
from core.utils.bulk_ops import (
    bulk_insert,
    count_records,
    get_mapping,
    insert_records,
    sync_id_sequence,
)
from core.utils.files import cleanup_pipeline_data
from core.utils.logger import get_logger
from core.utils.normalize import normalize_col


class MarginacionLoad(Stage):
    def __init__(self, year: int):
        super().__init__("marginacion", "load")
        self.year = year
        self.logger = get_logger("marginacion.load")
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> dict[str, Any]:
        pkl_municipal = Path(f"data/transform/marginacion/municipal_{self.year}.pkl")
        pkl_localidad = Path(f"data/transform/marginacion/localidad_{self.year}.pkl")
        pkl_catalogs = Path(f"data/transform/marginacion/catalogs_{self.year}.pkl")

        if pkl_municipal.exists() and pkl_localidad.exists() and pkl_catalogs.exists():
            self.logger.info(f"[source] Loading transform pkl files for {self.year}")
            return {
                "df_municipal": pd.read_pickle(pkl_municipal),
                "df_localidad": pd.read_pickle(pkl_localidad),
                "catalogs": pd.read_pickle(pkl_catalogs),
            }

        return input_data

    def _load_catalogs(self, session, catalogs: dict) -> None:
        insert_records(
            session,
            GradosMarginacionMap.to_records(GradosMarginacion.grado_marginacion.key),
            GradosMarginacion,
            conflict_keys=[GradosMarginacion.id.key],
        )

        sync_id_sequence(session, Localidades)
        insert_records(
            session,
            catalogs[T.LOCALIDADES],
            Localidades,
            conflict_keys=[Localidades.cve_geo_id.key],
        )
        self.logger.info(f"[_load_catalogs] Catalogs loaded for {self.year}")

    def _map_foreign_keys(self, session, df_municipal: pd.DataFrame, df_localidad: pd.DataFrame):
        grados_map = get_mapping(
            session,
            GradosMarginacion,
            GradosMarginacion.grado_marginacion.key,
            GradosMarginacion.id.key,
            is_normalize=True,
        )
        localidades_map = get_mapping(session, Localidades, Localidades.cve_geo_id.key, Localidades.id.key)

        df_municipal = df_municipal.copy()
        df_municipal[MarginacionesMunicipales.grado_marginacion_id.key] = normalize_col(
            df_municipal, GradosMarginacion.grado_marginacion.key
        ).map(grados_map)

        df_localidad = df_localidad.copy()
        df_localidad[MarginacionesLocalidades.grado_marginacion_id.key] = normalize_col(
            df_localidad, GradosMarginacion.grado_marginacion.key
        ).map(grados_map)
        df_localidad[MarginacionesLocalidades.localidad_id.key] = df_localidad[Localidades.cve_geo_id.key].map(
            localidades_map
        )

        return df_municipal.replace({np.nan: None}), df_localidad.replace({np.nan: None})

    def action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        df_municipal = input_data["df_municipal"]
        df_localidad = input_data["df_localidad"]

        if df_municipal.empty and df_localidad.empty:
            self.logger.info("[action] Empty input, skipping load")
            return None

        self.logger.info(
            f"[action] Loading {len(df_municipal)} municipal, {len(df_localidad)} localidad rows for {self.year}"
        )

        try:
            self.db.connect()
            with self.db.get_session() as session:
                self._load_catalogs(session, input_data["catalogs"])
                df_municipal, df_localidad = self._map_foreign_keys(session, df_municipal, df_localidad)

                records_before_municipal = count_records(session, MarginacionesMunicipales)
                records_before_localidad = count_records(session, MarginacionesLocalidades)

                sync_id_sequence(session, MarginacionesMunicipales)
                municipal_cols = [c for c in MarginacionesMunicipales.columns() if c != MarginacionesMunicipales.id.key]
                bulk_insert(
                    session,
                    df_to_records(df_municipal.astype(object).where(df_municipal.notna(), None), municipal_cols),
                    MarginacionesMunicipales,
                )

                sync_id_sequence(session, MarginacionesLocalidades)
                localidad_cols = [c for c in MarginacionesLocalidades.columns() if c != MarginacionesLocalidades.id.key]
                bulk_insert(
                    session,
                    df_to_records(df_localidad.astype(object).where(df_localidad.notna(), None), localidad_cols),
                    MarginacionesLocalidades,
                )

        except Exception:
            self.db.disconnect()
            raise

        return {
            "data": input_data,
            "records_before_municipal": records_before_municipal,
            "records_before_localidad": records_before_localidad,
        }

    def finalization(self, input_data: Any) -> Any:
        cleanup_pipeline_data("marginacion")
        if input_data is None:
            return None
        try:
            with self.db.get_session() as session:
                total_municipal = count_records(session, MarginacionesMunicipales)
                total_localidad = count_records(session, MarginacionesLocalidades)
                inserted_municipal = total_municipal - input_data["records_before_municipal"]
                inserted_localidad = total_localidad - input_data["records_before_localidad"]
            self.logger.info(
                f"[finalization] {total_municipal:,} marginaciones_municipales in database ({inserted_municipal:,} inserted)"
            )
            self.logger.info(
                f"[finalization] {total_localidad:,} marginaciones_localidades in database ({inserted_localidad:,} inserted)"
            )
        finally:
            self.db.disconnect()

        return input_data["data"]
