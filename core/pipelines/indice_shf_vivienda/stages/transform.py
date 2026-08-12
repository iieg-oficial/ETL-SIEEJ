import pandas as pd
from pathlib import Path
from typing import Any, Optional

from core.pipelines.indice_shf_vivienda.config import PIPELINE_NAME, settings
from core.pipelines.indice_shf_vivienda.constants import (
    FLOAT_COLS,
    INT_COLS,
    LEVEL_COLUMNS,
    LEVEL_ESTATAL,
    LEVEL_GLOBAL,
    LEVEL_MUNICIPAL,
    PERIOD_COLUMNS,
    STRIP_COLS,
)
from core.pipelines.stage import Stage
from core.utils import build_fecha_trimestre


class IndiceShfViviendaTransform(Stage):
    """Normalize types, build the quarter date and split the sheet by level."""

    def __init__(self):
        super().__init__(PIPELINE_NAME, "transform")

    def source(self, input_data: Optional[Any] = None) -> pd.DataFrame:
        pkl = Path(f"data/extract/{settings.PIPELINE_NAME}") / "extract.pkl"

        if pkl.exists():
            self.logger.info("Loading extract pkl file")
            return pd.read_pickle(pkl)

        return input_data

    def action(self, input_data: pd.DataFrame) -> dict[str, pd.DataFrame]:
        if input_data is None or input_data.empty:
            self.logger.warning("Empty input, nothing to transform")
            return {level: pd.DataFrame() for level in LEVEL_COLUMNS}

        df = self._prepare(input_data.copy())
        return self._split_by_level(df)

    def _prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean the names, cast the numbers and build the period, in that order."""
        for col in STRIP_COLS:
            # Un valor de puro espacio se vuelve "" al recortarlo: sin este paso
            # pasaría las máscaras de nivel como si trajera un nombre real.
            df[col] = df[col].str.strip().replace("", None)

        for col in INT_COLS + FLOAT_COLS:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df["fecha"] = build_fecha_trimestre(df["anio"], df["trimestre"]).dt.date

        for col in INT_COLS:
            df[col] = df[col].astype("Int64")

        before = len(df)
        df = df.dropna(subset=["fecha", "indice"])
        if len(df) < before:
            self.logger.warning(f"{before - len(df):,} rows dropped for an unreadable period or index")

        return df

    def _split_by_level(self, df: pd.DataFrame) -> dict[str, pd.DataFrame]:
        """Partition the sheet into its three mutually exclusive levels.

        The source spreads geography across three columns and fills exactly one
        per row, which is what would force a nullable column per level if the
        sheet were stored as published. The masks are verified to be disjoint and
        to cover every row: if SHF ever fills two at once, that has to fail loudly
        rather than duplicate or silently drop the row.
        """
        masks = {
            LEVEL_GLOBAL: df["serie_global"].notna(),
            LEVEL_ESTATAL: df["estado"].notna() & df["municipio"].isna(),
            LEVEL_MUNICIPAL: df["municipio"].notna(),
        }

        assigned = sum(mask.astype(int) for mask in masks.values())
        if not assigned.eq(1).all():
            offenders = df[assigned != 1].head()
            raise ValueError(
                f"{int((assigned != 1).sum()):,} rows do not belong to exactly one level. "
                f"'Global', 'Estado' and 'Municipio' stopped being mutually exclusive:\n{offenders}"
            )

        levels = {level: df[mask][LEVEL_COLUMNS[level] + PERIOD_COLUMNS].copy() for level, mask in masks.items()}
        for level, frame in levels.items():
            self.logger.info(f"{level}: {len(frame):,} rows")

        return levels

    def finalization(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        if all(frame.empty for frame in input_data.values()):
            self.logger.warning("No transformed data, skipping pkl save")
            return input_data

        for level, frame in input_data.items():
            frame.to_pickle(self.work_dir / f"{level}.pkl")
        self.logger.info(f"{len(input_data)} levels saved to {self.work_dir}")
        return input_data
