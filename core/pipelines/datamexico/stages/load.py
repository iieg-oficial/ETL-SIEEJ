import pandas as pd
from pathlib import Path
from typing import Any

from core.db import Database
from core.pipelines.datamexico.attributes import DataMexicoTables as T
from core.pipelines.datamexico.config import settings
from core.pipelines.datamexico.schemas import (
    FlujoComercio,
    Paises,
    Periodos,
    Productos,
    TiposFlujoComercial,
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


class DataMexicoLoad(Stage):
    def __init__(self):
        super().__init__("datamexico", "load")
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(self, input_data: Any = None) -> dict[str, pd.DataFrame]:
        transform_dir = Path("data/transform/datamexico")
        pkls = {name: transform_dir / f"{name}.pkl" for name in T}
        if all(p.exists() for p in pkls.values()):
            self.logger.info("[source] Loading from transform pickles")
            return {name: pd.read_pickle(path) for name, path in pkls.items()}
        self.logger.info("[source] Using transform output")
        return input_data

    def _load_catalogs(self, session, dfs: dict[str, pd.DataFrame]) -> None:
        insert_records(
            session,
            df_to_records(dfs[T.PERIODOS], Periodos.columns()),
            Periodos,
            conflict_keys=[Periodos.id.key],
        )
        insert_records(
            session,
            df_to_records(dfs[T.TIPOS_FLUJOS_COMERCIALES], TiposFlujoComercial.columns()),
            TiposFlujoComercial,
            conflict_keys=[TiposFlujoComercial.id.key],
        )
        insert_records(
            session,
            df_to_records(dfs[T.PRODUCTOS], Productos.columns()),
            Productos,
            conflict_keys=[Productos.id.key],
        )
        sync_id_sequence(session, Paises)
        insert_records(
            session,
            df_to_records(dfs[T.PAISES], [Paises.codigo_pais.key, Paises.nombre_pais.key]),
            Paises,
            conflict_keys=[Paises.codigo_pais.key],
        )

    def _map_foreign_keys(self, session, df: pd.DataFrame) -> pd.DataFrame:
        paises_map = get_mapping(session, Paises, Paises.codigo_pais.key, Paises.id.key)
        df = df.copy()
        df[FlujoComercio.pais_id.key] = df[Paises.codigo_pais.key].map(paises_map)
        df = df.drop(columns=[Paises.codigo_pais.key])
        return df

    def action(self, input_data: dict[str, pd.DataFrame]) -> dict[str, Any]:
        if input_data[T.FLUJO_COMERCIO].empty:
            self.logger.info("[action] No data to load")
            return {"records_before": 0}
        self.logger.info("[action] Loading into DB")
        try:
            self.db.connect()
            with self.db.get_session() as session:
                self._load_catalogs(session, input_data)
                df = self._map_foreign_keys(session, input_data[T.FLUJO_COMERCIO])
                records_before = count_records(session, FlujoComercio)
                flujo_cols = [c for c in FlujoComercio.columns() if c != FlujoComercio.id.key]
                bulk_insert(session, df_to_records(df, flujo_cols), FlujoComercio, chunk_size=settings.CHUNK_SIZE)
        except Exception:
            self.db.disconnect()
            raise

        return {"records_before": records_before}

    def finalization(self, input_data: dict[str, Any]) -> None:
        cleanup_pipeline_data(self.pipeline_name)
        if not self.db.is_connected:
            self.logger.info("[finalization] No data loaded")
            return
        try:
            with self.db.get_session() as session:
                total = count_records(session, FlujoComercio)
                inserted = total - input_data["records_before"]
            self.logger.info(f"[finalization] {format(total, ',')} records in flujo_comercio")
            self.logger.info(f"[finalization] {format(inserted, ',')} records inserted")
        finally:
            self.db.disconnect()
