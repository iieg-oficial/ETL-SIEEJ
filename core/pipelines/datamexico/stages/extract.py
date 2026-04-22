import pandas as pd
from typing import Any

from core.pipelines.datamexico.attributes import DataMexicoTables as T
from core.pipelines.datamexico.constants import (
    RENAME_COMERCIO,
    RENAME_FLUJOS,
    RENAME_PAISES,
    RENAME_PERIODOS,
    RENAME_PRODUCTOS,
)
from core.pipelines.datamexico.helpers.download_datamexico import fetch_catalog, fetch_trade_data
from core.pipelines.stage import Stage


class DataMexicoExtract(Stage):
    def __init__(self, start_quarter: int = 20201):
        super().__init__("datamexico", "extract")
        self.start_quarter = start_quarter

    def source(self, input_data: Any = None) -> dict[str, pd.DataFrame]:
        self.logger.info(f"[source] Fetching catalogs and trade data (start_quarter={self.start_quarter})")
        return {
            T.PAISES: fetch_catalog("Country"),
            T.TIPOS_FLUJOS_COMERCIALES: fetch_catalog("Flow"),
            T.PRODUCTOS: fetch_catalog("HS6"),
            T.PERIODOS: fetch_catalog("Quarter"),
            T.FLUJO_COMERCIO: fetch_trade_data(
                ["Flow", "Quarter", "State", "HS6", "Country"],
                start_quarter=self.start_quarter,
            ),
        }

    def action(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        if input_data[T.FLUJO_COMERCIO].empty:
            self.logger.info("[action] No new quarters to process")
            return {name: pd.DataFrame() for name in T}
        self.logger.info("[action] Renaming columns")
        periodos = _parse_periodos(input_data[T.PERIODOS].rename(columns=RENAME_PERIODOS))
        comercio = input_data[T.FLUJO_COMERCIO].rename(columns=RENAME_COMERCIO)[list(RENAME_COMERCIO.values())]
        return {
            T.PAISES: input_data[T.PAISES]
            .rename(columns=RENAME_PAISES)[list(RENAME_PAISES.values())]
            .drop_duplicates(),
            T.TIPOS_FLUJOS_COMERCIALES: input_data[T.TIPOS_FLUJOS_COMERCIALES]
            .rename(columns=RENAME_FLUJOS)[list(RENAME_FLUJOS.values())]
            .drop_duplicates(),
            T.PRODUCTOS: input_data[T.PRODUCTOS]
            .rename(columns=RENAME_PRODUCTOS)[list(RENAME_PRODUCTOS.values())]
            .drop_duplicates(),
            T.PERIODOS: periodos,
            T.FLUJO_COMERCIO: comercio,
        }

    def finalization(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        for name, df in input_data.items():
            path = self.work_dir / f"{name}.pkl"
            df.to_pickle(path)
            self.logger.info(f"[finalization] {name}: {len(df)} rows -> {path.name}")
        return input_data


def _parse_periodos(df: pd.DataFrame) -> pd.DataFrame:
    df["id"] = df["id"].astype(int)
    df["anio"] = df["id"] // 10
    df["trimestre"] = df["id"] % 10
    return df[["id", "anio", "trimestre", "etiqueta_trimestre"]].drop_duplicates()
