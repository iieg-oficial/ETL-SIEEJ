import io
import zipfile
from typing import Optional

import pandas as pd
import requests

from core.pipelines.stage import Stage
from core.pipelines.ilmm.config import settings


class IlmmExtract(Stage):
    def __init__(self, years: list[int]):
        super().__init__("ilmm", "extract")
        self.years = years

    def source(self, input_data: Optional[None] = None) -> list[tuple[int, pd.DataFrame]]:
        results = []
        for year in self.years:
            url = settings.ILMM_BASE_URL.format(year=year)
            self.logger.info(f"[source] Downloading year {year}: {url}")
            response = requests.get(url, timeout=180)
            response.raise_for_status()

            with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                csv_path = settings.CSV_INNER_PATH.format(year=year)
                with zf.open(csv_path) as f:
                    df = pd.read_csv(f, encoding="utf-8-sig")
                    df.columns = df.columns.str.strip().str.lower()

            self.logger.info(f"[source] Year {year}: {len(df)} rows, columns: {df.columns.tolist()}")
            results.append((year, df))

        return results

    def action(self, input_data: list[tuple[int, pd.DataFrame]]) -> pd.DataFrame:
        self.logger.info(f"[action] Combining {len(input_data)} year files")
        dfs = []
        for year, df in input_data:
            df = df.copy()
            df["year"] = year
            dfs.append(df)

        combined = pd.concat(dfs, ignore_index=True)
        self.logger.info(f"[action] Combined: {len(combined)} total rows")
        return combined

    def finalization(self, input_data: pd.DataFrame) -> pd.DataFrame:
        pkl_path = self.work_dir / "ilmm_raw.pkl"
        input_data.to_pickle(pkl_path)
        self.logger.info(f"[finalization] {len(input_data)} rows saved to {pkl_path}")
        return input_data
