from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.db import Database
from core.pipelines.stage import Stage
from core.pipelines.censos_economicos.config import settings
from core.pipelines.censos_economicos.constants import (
    CE_YEARS_CONFIG,
    GEO_LEVEL_ESTATAL,
    GEO_LEVEL_MUNICIPAL,
    GEO_LEVEL_NACIONAL,
)
from core.pipelines.censos_economicos.mappings import (
    CAT_ESTRATOS,
    CENSO_METADATA,
    CLASIFICADOR_CODIGO_MAP,
    ESTRATOS_CODIGO_MAP,
    STG_MODEL_MAP,
)
from core.pipelines.censos_economicos.schemas import (
    CatActividadesEconomicas,
    CatClasificadoresCodigos,
    CatEstratos,
    CatCensos,
)
from core.utils import df_to_records
from core.utils.bulk_ops import bulk_insert, get_all_records, get_mapping, insert_records, sync_id_sequence
from core.utils.files import cleanup_pipeline_data
from core.utils.logger import get_logger

PIPELINE_NAME = settings.PIPELINE_NAME


class CensosEconomicosLoader(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.logger = get_logger(f"{PIPELINE_NAME}.load")
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> dict:
        transform_dir = Path(f"data/transform/{PIPELINE_NAME}")
        result = {}

        for year in CE_YEARS_CONFIG:
            year_data = {}
            use_pkl = True

            for key in [GEO_LEVEL_NACIONAL, GEO_LEVEL_ESTATAL, GEO_LEVEL_MUNICIPAL, "cat_actividad"]:
                pkl = transform_dir / f"{year}_{key}.pkl"
                if pkl.exists():
                    year_data[key] = pd.read_pickle(pkl)
                else:
                    use_pkl = False
                    break

            if use_pkl:
                self.logger.info(f"[source] Year {year}: loading from pkl")
                result[year] = year_data
            elif input_data and year in input_data:
                self.logger.info(f"[source] Year {year}: using transform output")
                result[year] = input_data[year]
            else:
                self.logger.warning(f"[source] Year {year}: no data found")

        return result

    def _load_static_catalogs(self, session) -> None:
        self.logger.info("[_load_static_catalogs] Loading clasificadores")
        clasificadores = [{"id": k, "clasificador": v} for k, v in CLASIFICADOR_CODIGO_MAP.items()]
        insert_records(
            session, clasificadores, CatClasificadoresCodigos, conflict_keys=[CatClasificadoresCodigos.id.key]
        )

        self.logger.info("[_load_static_catalogs] Loading censos")
        sync_id_sequence(session, CatCensos)
        censos = [
            {
                "anio": meta["anio"],
                "descripcion": meta["descripcion"],
                "fecha_publicacion": meta["fecha_publicacion"],
                "fuente": meta["fuente"],
            }
            for meta in CENSO_METADATA.values()
        ]
        insert_records(session, censos, CatCensos, conflict_keys=[CatCensos.anio.key])

        self.logger.info("[_load_static_catalogs] Loading estratos")
        insert_records(session, CAT_ESTRATOS, CatEstratos, conflict_keys=[CatEstratos.id.key])

    def _load_actividades(self, session, year: int, cat_df: pd.DataFrame, censo_id: int) -> None:
        self.logger.info(f"[_load_actividades] Year {year}: {len(cat_df)} actividades")
        sync_id_sequence(session, CatActividadesEconomicas)

        cols_needed = [c for c in CatActividadesEconomicas.columns() if c != CatActividadesEconomicas.id.key]
        df = cat_df.copy()
        df["censo_id"] = censo_id
        df["codigo_id"] = pd.to_numeric(df["clasificador_codigo"], errors="coerce").astype("Int64")
        df = df[["censo_id", "codigo", "descripcion", "codigo_id"]]
        df = df.dropna(subset=["descripcion"])

        records = df_to_records(df.astype(object).where(df.notna(), None), cols_needed)
        insert_records(
            session,
            records,
            CatActividadesEconomicas,
            conflict_keys=["codigo", "codigo_id", "censo_id"],
        )

    def _build_actividades_map(self, session, censo_id: int) -> dict:
        rows = get_all_records(
            session,
            CatActividadesEconomicas,
            [
                CatActividadesEconomicas.id.key,
                CatActividadesEconomicas.codigo.key,
                CatActividadesEconomicas.censo_id.key,
            ],
        )
        return {r["codigo"]: r["id"] for r in rows if r["censo_id"] == censo_id}

    def _map_and_load_stg(
        self,
        session,
        df: pd.DataFrame,
        model,
        censo_id: int,
        actividades_map: dict,
    ) -> None:
        if df.empty:
            return

        df = df.copy()
        df["censo_id"] = censo_id

        df["actividad_economica_id"] = df["codigo"].map(actividades_map)
        df["id_estrato"] = pd.to_numeric(df["id_estrato"], errors="coerce")
        is_null_estrato = df["id_estrato"].isna()
        df["estrato_id"] = df["id_estrato"].map({k: v for k, v in ESTRATOS_CODIGO_MAP.items() if k is not None})
        df.loc[is_null_estrato, "estrato_id"] = ESTRATOS_CODIGO_MAP[None]

        cols = [c for c in model.columns() if c != model.id.key]
        existing_cols = [c for c in cols if c in df.columns]

        records = df_to_records(
            df[existing_cols].astype(object).where(df[existing_cols].notna(), None),
            existing_cols,
        )
        self.logger.info(f"[_map_and_load_stg] {model.__tablename__}: {len(records)} records")
        bulk_insert(session, records, model, chunk_size=settings.BULK_SIZE)

    def action(self, input_data: dict) -> dict:
        if not input_data:
            self.logger.info("[action] No data to load")
            return {}

        try:
            self.db.connect()
            with self.db.get_session() as session:
                self._load_static_catalogs(session)

                censos_map = get_mapping(session, CatCensos, CatCensos.anio.key, CatCensos.id.key)

                for year, year_data in input_data.items():
                    censo_id = censos_map[year]
                    self.logger.info(f"[action] Year {year}, censo_id={censo_id}")

                    self._load_actividades(session, year, year_data["cat_actividad"], censo_id)

                    actividades_map = self._build_actividades_map(session, censo_id)

                    for geo_level in [GEO_LEVEL_NACIONAL, GEO_LEVEL_ESTATAL, GEO_LEVEL_MUNICIPAL]:
                        model = STG_MODEL_MAP[year][geo_level]
                        df = year_data[geo_level]
                        self._map_and_load_stg(session, df, model, censo_id, actividades_map)

        except Exception:
            self.db.disconnect()
            raise

        return input_data

    def finalization(self, input_data: Any) -> Any:
        cleanup_pipeline_data(PIPELINE_NAME)
        self.db.disconnect()
        self.logger.info("[finalization] Load complete")
        return input_data
