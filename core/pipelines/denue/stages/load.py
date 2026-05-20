import pandas as pd
from pathlib import Path
from typing import Any, Optional

from core.db import Database
from core.pipelines.stage import Stage
from core.pipelines.denue.attributes import DenueTables as T
from core.pipelines.denue.config import settings
from core.pipelines.denue.mappings import RANGOS_PERSONAL, TIPOS_ESTABLECIMIENTOS
from core.pipelines.denue.schemas import (
    Actualizaciones,
    ActividadesEconomicas,
    Establecimientos,
    Localidades,
    RangosPersonal,
    TiposEstablecimientos,
)
from core.utils import df_to_records
from core.utils.bulk_ops import (
    count_records,
    get_all_records,
    get_mapping,
    insert_records,
    sync_id_sequence,
    upsert_records,
)

from core.utils.logger import get_logger

PIPELINE_NAME = settings.PIPELINE_NAME


class DenueLoad(Stage):
    def __init__(self, mode: str = "bootstrap", entidad: int = None):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode
        self.entidad = entidad
        self.logger = get_logger(f"{PIPELINE_NAME}.load")
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> Any:
        pkl_df = Path(f"data/transform/{PIPELINE_NAME}/denue_df_{self.entidad}.pkl")
        pkl_catalogs = Path(f"data/transform/{PIPELINE_NAME}/denue_catalogs_{self.entidad}.pkl")
        self.logger.info("[source] Checking for pkl files")
        if pkl_df.exists() and pkl_catalogs.exists():
            self.logger.info("[source] Loading from pkl files")
            df = pd.read_pickle(pkl_df)
            catalogs = pd.read_pickle(pkl_catalogs).to_dict()
            return {"df": df, "catalogs": catalogs}
        self.logger.info("[source] pkl not found, using transform output")
        return input_data

    def _load_catalogs(self, session, catalogs: dict) -> None:
        self.logger.info("[_load_catalogs] Loading static catalogs")
        insert_records(session, RANGOS_PERSONAL, RangosPersonal, conflict_keys=[RangosPersonal.id.key])
        insert_records(
            session, TIPOS_ESTABLECIMIENTOS, TiposEstablecimientos, conflict_keys=[TiposEstablecimientos.id.key]
        )

        self.logger.info(f"[_load_catalogs] Loading {len(catalogs[T.ACTUALIZACIONES])} actualizaciones")
        insert_records(
            session,
            catalogs[T.ACTUALIZACIONES],
            Actualizaciones,
            conflict_keys=[Actualizaciones.fecha_actualizacion.key],
        )

        self.logger.info(f"[_load_catalogs] Loading {len(catalogs[T.LOCALIDADES])} localidades")
        insert_records(session, catalogs[T.LOCALIDADES], Localidades, conflict_keys=[Localidades.cve_geo_id.key])

        self.logger.info(f"[_load_catalogs] Loading {len(catalogs[T.ACTIVIDADES_ECONOMICAS])} actividades economicas")
        insert_records(
            session,
            catalogs[T.ACTIVIDADES_ECONOMICAS],
            ActividadesEconomicas,
            conflict_keys=[ActividadesEconomicas.id.key],
        )

        self.logger.info("[_load_catalogs] Syncing sequences for dynamic tables")
        for model in [Actualizaciones, Localidades]:
            sync_id_sequence(session, model)

    def _map_foreign_keys(self, session, df: pd.DataFrame) -> pd.DataFrame:
        self.logger.info("[_map_foreign_keys] Building actualizaciones mapping")
        actualizaciones_map = get_mapping(
            session,
            Actualizaciones,
            Actualizaciones.fecha_actualizacion.key,
            Actualizaciones.id.key,
        )

        self.logger.info("[_map_foreign_keys] Building localidades mapping")
        localidades_rows = get_all_records(
            session,
            Localidades,
            [Localidades.id.key, Localidades.cve_geo_id.key],
        )
        localidades_map = {r[Localidades.cve_geo_id.key]: r[Localidades.id.key] for r in localidades_rows}

        df = df.copy()
        df[Establecimientos.actualizacion_id.key] = df["fecha_actualizacion"].map(actualizaciones_map)

        df["cve_geo_id"] = df.apply(
            lambda row: (
                int(f"{int(row['entidad_id']):02}{int(row['cve_mun']):03}{int(row['clave_localidad']):04}")
                if pd.notna(row["cve_mun"]) and pd.notna(row["clave_localidad"])
                else None
            ),
            axis=1,
        )
        df[Establecimientos.localidad_id.key] = df["cve_geo_id"].map(localidades_map)

        return df.astype(object).where(df.notna(), None)

    def action(self, input_data: Any) -> Any:
        df = input_data["df"]
        if df.empty:
            self.logger.info("[action] Empty DataFrame, skipping load")
            return None

        catalogs = input_data["catalogs"]
        self.logger.info(f"[action] Loading {len(df)} rows")

        try:
            self.db.connect()
            with self.db.get_session() as session:
                records_before = count_records(session, Establecimientos)
                self._load_catalogs(session, catalogs)
                df = self._map_foreign_keys(session, df)

                cols = [c for c in Establecimientos.columns() if c != Establecimientos.id.key]
                cols = [Establecimientos.id.key] + cols
                records = df_to_records(df, cols)
                upsert_records(
                    session,
                    records,
                    Establecimientos,
                    conflict_keys=[Establecimientos.id.key, Establecimientos.actualizacion_id.key],
                    chunk_size=settings.CHUNK_SIZE,
                )
        except Exception:
            self.db.disconnect()
            raise

        return {"data": input_data, "records_before": records_before}

    def finalization(self, input_data: Any) -> Any:
        if input_data is None:
            return None
        try:
            with self.db.get_session() as session:
                total = count_records(session, Establecimientos)
                inserted = total - input_data["records_before"]
            self.logger.info(f"[finalization] {format(total, ',')} establecimientos in database")
            self.logger.info(f"[finalization] {format(inserted, ',')} establecimientos inserted/updated")
        finally:
            self.db.disconnect()
        return input_data["data"]
