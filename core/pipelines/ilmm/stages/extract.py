import io
import zipfile
from typing import Optional

import pandas as pd
import requests

from core.pipelines.stage import Stage
from core.pipelines.ilmm.config import settings

_EST_CATALOG_PATH_IN_ZIP = "catalogos/est.csv"

# Column aliases introduced in the 2025 release
_COLUMN_ALIASES: dict[str, str] = {
    "cve_ent": "ent",
    "cve_mun": "mun",
}


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Rename aliased columns to the canonical schema expected by transform
    df = df.rename(columns=_COLUMN_ALIASES)
    # Drop spurious unnamed columns produced by trailing delimiters in newer CSVs
    unnamed = [c for c in df.columns if c.startswith("unnamed")]
    if unnamed:
        df = df.drop(columns=unnamed)
    return df


def _read_csv_auto_encoding(raw: bytes, **kwargs) -> pd.DataFrame:
    for enc in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(io.BytesIO(raw), encoding=enc, **kwargs)
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode CSV with utf-8-sig or latin-1")


class IlmmExtract(Stage):
    def __init__(self, years: list[int]):
        super().__init__("ilmm", "extract")
        self.years = years

    def source(self, input_data: Optional[None] = None) -> list[tuple[int, pd.DataFrame, pd.DataFrame | None]]:
        results = []
        df_est: pd.DataFrame | None = None
        for year in self.years:
            url = settings.ILMM_BASE_URL.format(year=year)
            self.logger.info(f"[source] Downloading year {year}: {url}")
            response = requests.get(url, timeout=180)
            response.raise_for_status()

            with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                csv_path = settings.CSV_INNER_PATH.format(year=year)
                with zf.open(csv_path) as f:
                    raw = f.read()
                df = _read_csv_auto_encoding(raw)
                df.columns = df.columns.str.strip().str.lower()
                df = _normalize_columns(df)

                # Extract est.csv catalog only from the first year processed
                if df_est is None and _EST_CATALOG_PATH_IN_ZIP in zf.namelist():
                    with zf.open(_EST_CATALOG_PATH_IN_ZIP) as f:
                        raw_est = f.read()
                    df_est = _read_csv_auto_encoding(raw_est)
                    df_est.columns = df_est.columns.str.strip().str.lower()
                    self.logger.info(f"[source] est catalog: {len(df_est)} rows")

            self.logger.info(f"[source] Year {year}: {len(df)} rows, columns: {df.columns.tolist()}")
            results.append((year, df, df_est))

        return results

    def action(
        self, input_data: list[tuple[int, pd.DataFrame, pd.DataFrame | None]]
    ) -> tuple[pd.DataFrame, pd.DataFrame | None]:
        self.logger.info(f"[action] Combining {len(input_data)} year files")
        dfs = []
        df_est = None
        for year, df, df_est_year in input_data:
            df = df.copy()
            df["year"] = year
            dfs.append(df)
            if df_est is None and df_est_year is not None:
                df_est = df_est_year

        combined = pd.concat(dfs, ignore_index=True)
        self.logger.info(f"[action] Combined: {len(combined)} total rows")
        return combined, df_est

    def finalization(
        self, input_data: tuple[pd.DataFrame, pd.DataFrame | None]
    ) -> tuple[pd.DataFrame, pd.DataFrame | None]:
        combined, df_est = input_data
        pkl_path = self.work_dir / "ilmm_raw.pkl"
        combined.to_pickle(pkl_path)
        self.logger.info(f"[finalization] {len(combined)} rows saved to {pkl_path}")

        if df_est is not None:
            est_path = self.work_dir / "cat_estimador.pkl"
            df_est.to_pickle(est_path)
            self.logger.info(f"[finalization] est catalog saved to {est_path}")

        return combined, df_est
