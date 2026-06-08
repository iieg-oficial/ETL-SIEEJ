from datetime import date
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.constants.geo import JALISCO_CVE_ENTIDAD
from core.pipelines.nacimientos_dgis.constants import EDADPADRE_INVALID, PIPELINE_NAME
from core.pipelines.stage import Stage
from core.utils.logger import get_logger


class NacimientosDgisTransform(Stage):
    def __init__(self):
        super().__init__(PIPELINE_NAME, "transform")
        self.logger = get_logger(f"{PIPELINE_NAME}.transform")

    def source(self, input_data: Optional[Any] = None) -> dict[int, pd.DataFrame]:
        extract_dir = Path(f"data/extract/{PIPELINE_NAME}")
        cached = {}

        for pkl in sorted(extract_dir.glob("sinac_*.pkl")):
            year = int(pkl.stem.split("_")[1])
            cached[year] = pd.read_pickle(pkl)
            self.logger.info(f"[source] {year}: loaded {len(cached[year]):,} rows from extract")

        if cached:
            return cached
        return input_data

    def _process_year(self, year: int, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df["ENTIDADRESIDENCIA"] = pd.to_numeric(df["ENTIDADRESIDENCIA"], errors="coerce")
        df = df[df["ENTIDADRESIDENCIA"] == JALISCO_CVE_ENTIDAD]
        self.logger.info(f"[action] {year}: {len(df):,} rows after Jalisco filter")

        df["MUNICIPIORESIDENCIA"] = pd.to_numeric(df["MUNICIPIORESIDENCIA"], errors="coerce")
        df["EDAD"] = pd.to_numeric(df["EDAD"], errors="coerce")
        df["EDADPADRE"] = pd.to_numeric(df["EDADPADRE"], errors="coerce")

        df["cve_geo"] = (df["ENTIDADRESIDENCIA"] * 1000 + df["MUNICIPIORESIDENCIA"]).astype("Int64")

        df["anio"] = pd.to_datetime(df["FECHANACIMIENTO"], format="%d/%m/%Y", errors="coerce").dt.year
        df = df.dropna(subset=["anio", "cve_geo", "EDAD"])
        df["anio"] = df["anio"].astype(int)
        df["cve_geo"] = df["cve_geo"].astype(int)

        df["padre_conocido"] = df["EDADPADRE"].notna() & ~df["EDADPADRE"].isin(EDADPADRE_INVALID)
        df["padre_18_y_mas"] = df["padre_conocido"] & (df["EDADPADRE"] >= 18)
        df["padre_25_y_mas"] = df["padre_conocido"] & (df["EDADPADRE"] >= 25)

        grouped = (
            df.groupby(["anio", "cve_geo", "EDAD"])
            .agg(
                tot_nac=("EDAD", "size"),
                nac_padre_conocido=("padre_conocido", "sum"),
                nac_padre_18_mas=("padre_18_y_mas", "sum"),
                nac_padre_25_mas=("padre_25_y_mas", "sum"),
            )
            .reset_index()
        )

        grouped = grouped.rename(columns={"EDAD": "edad_madre"})
        grouped["edad_madre"] = grouped["edad_madre"].astype(int)
        grouped["nac_padre_conocido"] = grouped["nac_padre_conocido"].astype(int)
        grouped["nac_padre_18_mas"] = grouped["nac_padre_18_mas"].astype(int)
        grouped["nac_padre_25_mas"] = grouped["nac_padre_25_mas"].astype(int)
        grouped["fecha_actualizacion"] = date.today()

        self.logger.info(f"[action] {year}: {len(grouped):,} aggregated rows")
        return grouped

    def action(self, input_data: dict[int, pd.DataFrame]) -> pd.DataFrame:
        if not input_data:
            self.logger.info("[action] Empty input, skipping transform")
            return pd.DataFrame()

        frames = []
        for year in sorted(input_data):
            df = input_data[year]
            if df.empty:
                continue
            frames.append(self._process_year(year, df))

        if not frames:
            return pd.DataFrame()

        result = pd.concat(frames, ignore_index=True)
        self.logger.info(f"[action] {len(result):,} total aggregated rows")
        return result

    def finalization(self, input_data: pd.DataFrame) -> pd.DataFrame:
        if input_data.empty:
            return input_data

        input_data.to_pickle(self.work_dir / "nacimientos.pkl")
        self.logger.info(f"[finalization] {len(input_data):,} rows saved")
        return input_data
