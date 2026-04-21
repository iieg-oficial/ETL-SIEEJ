import pandas as pd
from datetime import date
from io import StringIO
from time import sleep
from typing import Any, Optional

from core.pipelines.stage import Stage
from core.pipelines.inpc.constants import (
    RENAME_HEADER,
    REPLACE_MONTHS,
    SKIP_ROWS,
    LOCATION_ITEMS,
)
from core.pipelines.inpc.helpers.builders import idE
from core.pipelines.inpc.helpers.inpc_series import discover_series_ids
from core.pipelines.inpc.helpers.download_inpc import download_inpc_csv


class InpcExtract(Stage):
    def __init__(
        self,
        start_year: int = 1979,
        anio_fin: int = date.today().year,
    ):
        super().__init__("inpc", "extract")
        self.start_year = start_year
        self.anio_fin = anio_fin

    def source(self, input_data: Optional[Any] = None) -> list[tuple[str, str, Any, Any]]:
        results = []

        for location_type, items in LOCATION_ITEMS.items():
            for code, info in items:
                if location_type == "National":
                    self.logger.info("[source] Downloading national data")
                    id_estructura = idE("National")
                elif location_type == "City":
                    self.logger.info(f"[source] Downloading City {info.city}")
                    id_estructura = idE("City", code)
                else:
                    self.logger.info(f"[source] Downloading Entity {info.entity}")
                    id_estructura = idE("Entity", code)

                series_ids = discover_series_ids(id_estructura)
                sleep(1)
                csv_text = download_inpc_csv(id_estructura, series_ids, self.start_year, self.anio_fin)
                results.append((csv_text, location_type, code, info))

        self.logger.info(f"[source] {len(results)} files downloaded")
        return results

    def _parse(self, csv_text: str, location_type: str, code: Any, info: Any) -> pd.DataFrame:
        df = pd.read_csv(StringIO(csv_text), encoding="latin-1", skiprows=4)
        df = df.iloc[SKIP_ROWS:].copy()
        df = df.rename(columns=dict(zip(df.columns, RENAME_HEADER)))
        df.columns = df.columns.str.strip()
        if location_type == "City":
            df["ciudad_id"] = code
            df["ciudad"] = info.city
            df["entidad"] = info.state
        elif location_type == "Entity":
            df["entidad_id"] = code
            df["entity"] = info.entity
        df["fecha"] = df["fecha"].replace(REPLACE_MONTHS, regex=True)
        df["fecha"] = pd.to_datetime(df["fecha"], format="%m %Y")
        df["fecha_actualizacion"] = pd.Timestamp(date.today())
        return df

    def action(self, input_data: list[tuple[str, str, Any, Any]]) -> dict[str, pd.DataFrame]:
        self.logger.info(f"[action] Parsing {len(input_data)} files")
        buckets: dict[str, list] = {"City": [], "Entity": [], "National": []}

        for csv_text, location_type, code, info in input_data:
            buckets[location_type].append(self._parse(csv_text, location_type, code, info))

        return {
            "cities": pd.concat(buckets["City"], ignore_index=True),
            "entities": pd.concat(buckets["Entity"], ignore_index=True),
            "national": pd.concat(buckets["National"], ignore_index=True),
        }

    def finalization(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        for name, df in input_data.items():
            pkl_path = self.work_dir / f"inpc_{name}.pkl"
            df.to_pickle(pkl_path)
            self.logger.info(f"[finalization] {len(df)} rows saved to {pkl_path}")
        return input_data
