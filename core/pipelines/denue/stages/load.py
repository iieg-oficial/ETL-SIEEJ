import pandas as pd
from pathlib import Path
from typing import Any, Optional

from core.db import Database
from core.pipelines.stage import Stage
from core.pipelines.denue.attributes import DenueTables as T
from core.pipelines.denue.config import settings
from core.pipelines.denue.mappings import RANGOS_PERSONAL, TIPOS_ESTABLECIMIENTOS, get_sector_codigo
from core.pipelines.denue.schemas import (
    CatActualizaciones,
    CatClasesActividad,
    CatLocalidades,
    CatRamas,
    CatRangosPersonal,
    CatSectores,
    CatSubramas,
    CatSubsectores,
    CatTiposEstablecimientos,
    StgEstablecimientos,
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
        insert_records(session, RANGOS_PERSONAL, CatRangosPersonal, conflict_keys=[CatRangosPersonal.id.key])
        insert_records(
            session, TIPOS_ESTABLECIMIENTOS, CatTiposEstablecimientos, conflict_keys=[CatTiposEstablecimientos.id.key]
        )

        self.logger.info(f"[_load_catalogs] Loading {len(catalogs[T.CAT_ACTUALIZACIONES])} actualizaciones")
        insert_records(
            session,
            catalogs[T.CAT_ACTUALIZACIONES],
            CatActualizaciones,
            conflict_keys=[CatActualizaciones.fecha_actualizacion.key],
        )

        self.logger.info(f"[_load_catalogs] Loading {len(catalogs[T.CAT_LOCALIDADES])} localidades")
        insert_records(
            session, catalogs[T.CAT_LOCALIDADES], CatLocalidades, conflict_keys=[CatLocalidades.cve_geo_id.key]
        )

        scian_catalogs = [
            (T.CAT_SECTORES, CatSectores, CatSectores.codigo.key),
            (T.CAT_SUBSECTORES, CatSubsectores, CatSubsectores.codigo.key),
            (T.CAT_RAMAS, CatRamas, CatRamas.codigo.key),
            (T.CAT_SUBRAMAS, CatSubramas, CatSubramas.codigo.key),
            (T.CAT_CLASES_ACTIVIDAD, CatClasesActividad, CatClasesActividad.codigo.key),
        ]
        for table_key, model, conflict_key in scian_catalogs:
            records = catalogs.get(table_key, [])
            self.logger.info(f"[_load_catalogs] Loading {len(records)} {table_key}")
            insert_records(session, records, model, conflict_keys=[conflict_key])

        for model in [
            CatActualizaciones,
            CatLocalidades,
            CatSectores,
            CatSubsectores,
            CatRamas,
            CatSubramas,
            CatClasesActividad,
        ]:
            sync_id_sequence(session, model)

    def _map_foreign_keys(self, session, df: pd.DataFrame) -> pd.DataFrame:
        self.logger.info("[_map_foreign_keys] Building actualizaciones mapping")
        actualizaciones_map = get_mapping(
            session,
            CatActualizaciones,
            CatActualizaciones.fecha_actualizacion.key,
            CatActualizaciones.id.key,
        )

        self.logger.info("[_map_foreign_keys] Building localidades mapping")
        localidades_rows = get_all_records(
            session,
            CatLocalidades,
            [CatLocalidades.id.key, CatLocalidades.cve_geo_id.key],
        )
        localidades_map = {r[CatLocalidades.cve_geo_id.key]: r[CatLocalidades.id.key] for r in localidades_rows}

        self.logger.info("[_map_foreign_keys] Building SCIAN mappings")
        sectores_map = get_mapping(session, CatSectores, CatSectores.codigo.key, CatSectores.id.key)
        subsectores_map = get_mapping(session, CatSubsectores, CatSubsectores.codigo.key, CatSubsectores.id.key)
        ramas_map = get_mapping(session, CatRamas, CatRamas.codigo.key, CatRamas.id.key)
        subramas_map = get_mapping(session, CatSubramas, CatSubramas.codigo.key, CatSubramas.id.key)
        clases_map = get_mapping(session, CatClasesActividad, CatClasesActividad.codigo.key, CatClasesActividad.id.key)

        df = df.copy()
        df[StgEstablecimientos.actualizacion_id.key] = df["fecha_actualizacion"].map(actualizaciones_map)

        df["cve_geo_id"] = df.apply(
            lambda row: (
                int(f"{int(row['entidad_id']):02}{int(row['cve_mun']):03}{int(row['localidad_id']):04}")
                if pd.notna(row["cve_mun"]) and pd.notna(row["localidad_id"])
                else None
            ),
            axis=1,
        )
        df["localidad_id"] = df["cve_geo_id"].map(localidades_map)

        codigo_str = df["codigo_actividad"].apply(lambda x: str(int(x)) if pd.notna(x) else None)
        df["sector_id"] = codigo_str.apply(lambda x: sectores_map.get(get_sector_codigo(x)) if x else None)
        df["subsector_id"] = codigo_str.apply(lambda x: subsectores_map.get(x[:3]) if x and len(x) >= 3 else None)
        df["rama_id"] = codigo_str.apply(lambda x: ramas_map.get(x[:4]) if x and len(x) >= 4 else None)
        df["subrama_id"] = codigo_str.apply(lambda x: subramas_map.get(x[:5]) if x and len(x) >= 5 else None)
        df["clase_actividad_id"] = codigo_str.apply(lambda x: clases_map.get(x) if x else None)

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
                records_before = count_records(session, StgEstablecimientos)
                self._load_catalogs(session, catalogs)
                df = self._map_foreign_keys(session, df)

                cols = [c for c in StgEstablecimientos.columns() if c != StgEstablecimientos.id.key]
                cols = [StgEstablecimientos.id.key] + cols
                records = df_to_records(df, cols)
                upsert_records(
                    session,
                    records,
                    StgEstablecimientos,
                    conflict_keys=[StgEstablecimientos.id.key, StgEstablecimientos.actualizacion_id.key],
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
                total = count_records(session, StgEstablecimientos)
                inserted = total - input_data["records_before"]
            self.logger.info(f"[finalization] {format(total, ',')} establecimientos in database")
            self.logger.info(f"[finalization] {format(inserted, ',')} establecimientos inserted/updated")
        finally:
            self.db.disconnect()
        return input_data["data"]
