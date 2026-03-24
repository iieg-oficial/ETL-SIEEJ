import pandas as pd
from pathlib import Path
from typing import Any

from core.pipelines.datamexico.attributes import DataMexicoTables as T
from core.pipelines.datamexico.constants import CAPITALIZE_COLS, TITLE_COLS
from core.pipelines.stage import Stage
from core.utils.normalize import capitalize_col, title_col


class DataMexicoTransform(Stage):
    def __init__(self):
        super().__init__("datamexico", "transform")

    def source(self, input_data: Any = None) -> dict[str, pd.DataFrame]:
        extract_dir = Path("data/extract/datamexico")
        pkls = {name: extract_dir / f"{name}.pkl" for name in T}
        if all(p.exists() for p in pkls.values()):
            self.logger.info("[source] Loading from extract pickles")
            return {name: pd.read_pickle(path) for name, path in pkls.items()}
        self.logger.info(f"[source] Using extract output ({sum(len(df) for df in input_data.values())} rows total)")
        return input_data

    def action(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        if input_data[T.FLUJO_COMERCIO].empty:
            self.logger.info("[action] No data to transform")
            return input_data
        self.logger.info("[action] Casting dtypes")
        dfs = input_data.copy()

        for name in [T.PERIODOS, T.TIPOS_FLUJOS_COMERCIALES, T.PRODUCTOS]:
            dfs[name]["id"] = dfs[name]["id"].astype(int)

        comercio = dfs[T.FLUJO_COMERCIO]
        comercio["periodo_id"] = comercio["periodo_id"].astype(int)
        comercio["tipo_flujo_id"] = comercio["tipo_flujo_id"].astype(int)
        comercio["producto_id"] = comercio["producto_id"].astype(int)
        comercio["entidad_id"] = comercio["entidad_id"].astype(int)
        comercio["valor_comercio"] = comercio["valor_comercio"].astype(float)
        dfs[T.FLUJO_COMERCIO] = comercio

        for name, df in dfs.items():
            for col in TITLE_COLS:
                if col in df.columns:
                    title_col(df, col)
            for col in CAPITALIZE_COLS:
                if col in df.columns:
                    capitalize_col(df, col)

        for name, df in dfs.items():
            self.logger.info(f"[action] {name}: {len(df)} rows")

        return dfs

    def finalization(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        for name, df in input_data.items():
            path = self.work_dir / f"{name}.pkl"
            df.to_pickle(path)
            self.logger.info(f"[finalization] {name}: {len(df)} rows -> {path.name}")
        return input_data
