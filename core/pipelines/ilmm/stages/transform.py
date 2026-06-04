from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd

from core.pipelines.stage import Stage


class IlmmTransform(Stage):
    def __init__(self):
        super().__init__("ilmm", "transform")

    def source(
        self, input_data: Optional[tuple[pd.DataFrame, pd.DataFrame | None]] = None
    ) -> tuple[pd.DataFrame, pd.DataFrame | None]:
        pkl_path = Path("data/extract/ilmm/ilmm_raw.pkl")
        est_path = Path("data/extract/ilmm/cat_estimador.pkl")
        if pkl_path.exists():
            self.logger.info(f"[source] Loading {pkl_path}")
            df = pd.read_pickle(pkl_path)
            df_est = pd.read_pickle(est_path) if est_path.exists() else None
            return df, df_est
        self.logger.info("[source] pkl not found, using extract output")
        return input_data

    def action(self, input_data: tuple[pd.DataFrame, pd.DataFrame | None]) -> tuple[pd.DataFrame, pd.DataFrame | None]:
        df, df_est = input_data
        self.logger.info(f"[action] Transforming {len(df)} raw rows")

        # Cast key columns to numeric
        for col in ("ent", "mun", "est"):
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Filter out national/state aggregates (ent=0 or mun=0) and any rows with NaN in key columns
        df = df[df["ent"].notna() & df["mun"].notna() & (df["ent"] != 0) & (df["mun"] != 0)].copy()
        self.logger.info(f"[action] After filtering aggregates: {len(df)} rows")

        # Build clave_municipio (5-digit INEGI key)
        df["clave_municipio"] = df["ent"].astype(int).astype(str).str.zfill(2) + df["mun"].astype(int).astype(
            str
        ).str.zfill(3)

        # Cast indicator columns to numeric
        for col in ("pea", "ocupados", "informales"):
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Build fecha from year
        df["fecha"] = df["year"].apply(lambda y: date(int(y), 1, 1))

        # Rename columns to match schema
        df = df.rename(columns={"est": "estimador_id", "pea": "pob_econo_activa"})

        result = df[["clave_municipio", "fecha", "estimador_id", "pob_econo_activa", "ocupados", "informales"]].copy()

        # Round numeric columns
        for col in ("pob_econo_activa", "ocupados", "informales"):
            result[col] = result[col].round(4)

        result = result.dropna(subset=["clave_municipio", "fecha", "estimador_id"])
        result["estimador_id"] = result["estimador_id"].astype(int)

        self.logger.info(f"[action] {len(result)} transformed rows ready for load")
        return result, df_est

    def finalization(
        self, input_data: tuple[pd.DataFrame, pd.DataFrame | None]
    ) -> tuple[pd.DataFrame, pd.DataFrame | None]:
        result, df_est = input_data
        pkl_path = self.work_dir / "ilmm_transformed.pkl"
        result.to_pickle(pkl_path)
        self.logger.info(f"[finalization] {len(result)} rows saved to {pkl_path}")
        return result, df_est
