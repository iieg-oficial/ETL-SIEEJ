from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd

from core.pipelines.stage import Stage


class IlmmTransform(Stage):
    def __init__(self):
        super().__init__("ilmm", "transform")

    def source(self, input_data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        pkl_path = Path("data/extract/ilmm/ilmm_raw.pkl")
        if pkl_path.exists():
            self.logger.info(f"[source] Loading {pkl_path}")
            return pd.read_pickle(pkl_path)
        self.logger.info("[source] pkl not found, using extract output")
        return input_data

    def action(self, df: pd.DataFrame) -> pd.DataFrame:
        self.logger.info(f"[action] Transforming {len(df)} raw rows")

        # Cast key columns to int (they may arrive as float from CSV)
        for col in ("ent", "mun", "est"):
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Filter out national/state aggregates (ent=0 or mun=0)
        df = df[(df["ent"] != 0) & (df["mun"] != 0)].copy()
        self.logger.info(f"[action] After filtering aggregates: {len(df)} rows")

        # Keep only est=1 (Valor) and est=2 (Error estándar)
        df = df[df["est"].isin([1, 2])].copy()
        self.logger.info(f"[action] After filtering est IN (1,2): {len(df)} rows")

        # Build clave_municipio
        df["clave_municipio"] = df["ent"].astype(int).astype(str).str.zfill(2) + df["mun"].astype(int).astype(
            str
        ).str.zfill(3)

        # Cast indicator columns to numeric
        for col in ("ocupados", "informales"):
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Split by estimador
        df_val = df[df["est"] == 1][["clave_municipio", "year", "ocupados", "informales"]].copy()
        df_err = df[df["est"] == 2][["clave_municipio", "year", "ocupados", "informales"]].copy()

        # Merge value and std-error rows on (clave_municipio, year)
        merged = df_val.merge(
            df_err,
            on=["clave_municipio", "year"],
            suffixes=("_val", "_err"),
        )
        self.logger.info(f"[action] After merge: {len(merged)} pairs")

        # indicador_id=1: tasa_desocupacion
        # valor = 100 - ocupados(est=1),  error_estandar = ocupados(est=2)
        td = merged[["clave_municipio", "year", "ocupados_val", "ocupados_err"]].copy()
        td["indicador_id"] = 1
        td["valor"] = (100 - td["ocupados_val"]).round(4)
        td["error_estandar"] = td["ocupados_err"].round(4)
        td = td.drop(columns=["ocupados_val", "ocupados_err"])

        # indicador_id=2: porcentaje_ocupacion_informal
        # valor = informales(est=1),  error_estandar = informales(est=2)
        pi = merged[["clave_municipio", "year", "informales_val", "informales_err"]].copy()
        pi["indicador_id"] = 2
        pi["valor"] = pi["informales_val"].round(4)
        pi["error_estandar"] = pi["informales_err"].round(4)
        pi = pi.drop(columns=["informales_val", "informales_err"])

        result = pd.concat([td, pi], ignore_index=True)
        result["fecha"] = result["year"].apply(lambda y: date(int(y), 1, 1))
        result = result[["clave_municipio", "fecha", "indicador_id", "valor", "error_estandar"]]
        result = result.dropna(subset=["clave_municipio", "fecha", "indicador_id"])

        self.logger.info(f"[action] {len(result)} transformed rows ready for load")
        return result

    def finalization(self, input_data: pd.DataFrame) -> pd.DataFrame:
        pkl_path = self.work_dir / "ilmm_transformed.pkl"
        input_data.to_pickle(pkl_path)
        self.logger.info(f"[finalization] {len(input_data)} rows saved to {pkl_path}")
        return input_data
