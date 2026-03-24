import pandas as pd
from pathlib import Path
from typing import Any, Optional

from core.pipelines.stage import Stage
from core.pipelines.inpc.attributes import InpcTables as T
from core.pipelines.inpc.constants import CITY_NUMERICAL_COLS, NULL_VALUES
from core.pipelines.inpc.mappings import ObjetoGasto
from core.utils.clean import list_values_to_null


class InpcTransform(Stage):
    def __init__(self, date_from=None):
        super().__init__("inpc", "transform")
        self.date_from = pd.Timestamp(date_from) if date_from else None

    def source(self, input_data: Optional[Any] = None) -> dict[str, pd.DataFrame]:
        result = {}
        for name in ("cities", "entities", "national"):
            pkl_path = Path(f"data/extract/inpc/inpc_{name}.pkl")
            if pkl_path.exists():
                self.logger.info(f"[source] Loading {pkl_path}")
                result[name] = pd.read_pickle(pkl_path)
            else:
                self.logger.info(f"[source] pkl not found for {name}, using extract output")
                result[name] = input_data[name]
        return result

    def _build_catalogs(self, df_cities: pd.DataFrame) -> dict:
        ciudades = (
            df_cities[["ciudad_id", "ciudad", "entidad"]]
            .drop_duplicates(subset=["ciudad_id"])
            .rename(columns={"ciudad_id": "id"})
            .to_dict("records")
        )
        objetos_gasto = ObjetoGasto.to_records("objeto_gasto")
        return {
            T.CIUDADES: ciudades,
            T.OBJETOS_GASTO: objetos_gasto,
        }

    def _melt(self, df: pd.DataFrame, id_cols: list[str]) -> pd.DataFrame:
        objeto_gasto_map = {m.name: m.id for m in ObjetoGasto}
        df = list_values_to_null(df, rm_list=NULL_VALUES)
        df[CITY_NUMERICAL_COLS] = df[CITY_NUMERICAL_COLS].astype(float).round(3)
        df = df.melt(
            id_vars=id_cols,
            value_vars=CITY_NUMERICAL_COLS,
            var_name="objeto_gasto",
            value_name="indice_de_precios",
        )
        df["objeto_gasto_id"] = df["objeto_gasto"].map(objeto_gasto_map)
        return df.drop(columns=["objeto_gasto"])

    def _filter(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.date_from is not None:
            return df[df["fecha"] > self.date_from].copy()
        return df

    def action(self, input_data: dict[str, pd.DataFrame]) -> dict:
        self.logger.info("[action] Starting transform")

        df_cities = self._melt(
            self._filter(input_data["cities"]),
            id_cols=["ciudad_id", "fecha", "fecha_actualizacion"],
        )
        df_entities = self._melt(
            self._filter(input_data["entities"]),
            id_cols=["entidad_id", "entity", "fecha", "fecha_actualizacion"],
        )
        df_national = self._melt(
            self._filter(input_data["national"]),
            id_cols=["fecha", "fecha_actualizacion"],
        )

        self.logger.info(
            f"[action] cities: {len(df_cities)} rows, entities: {len(df_entities)} rows, national: {len(df_national)} rows"
        )

        return {
            "dfs": {
                "cities": df_cities,
                "entities": df_entities,
                "national": df_national,
            },
            "catalogs": self._build_catalogs(input_data["cities"]),
        }

    def finalization(self, input_data: dict) -> dict:
        for name, df in input_data["dfs"].items():
            pkl_path = self.work_dir / f"inpc_{name}.pkl"
            df.to_pickle(pkl_path)
            self.logger.info(f"[finalization] {len(df)} rows saved to {pkl_path}")
        return input_data
