from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.delitos_fuero_comun.config import PIPELINE_NAME
from core.pipelines.stage import Stage
from core.utils.files import clean_directory

RENAME: dict[str, str] = {
    "Año": "anio",
    "Clave_Ent": "clave_ent",
    "Entidad": "entidad",
    "Cve. Municipio": "cve_municipio",
    "Municipio": "municipio",
    "Bien jurídico afectado": "bien_juridico_afectado",
    "Tipo de delito": "tipo_delito",
    "Subtipo de delito": "subtipo_delito",
    "Modalidad": "modalidad",
    "Enero": "enero",
    "Febrero": "febrero",
    "Marzo": "marzo",
    "Abril": "abril",
    "Mayo": "mayo",
    "Junio": "junio",
    "Julio": "julio",
    "Agosto": "agosto",
    "Septiembre": "septiembre",
    "Octubre": "octubre",
    "Noviembre": "noviembre",
    "Diciembre": "diciembre",
}

MONTH_COLS: list[str] = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
]


class DelitosTransform(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "transform")
        self.mode = mode

    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data or not input_data.get("csv_2026"):
            raise ValueError("Transform no recibió CSV 2026 de Extract")
        return input_data

    def action(self, input_data: Optional[Any] = None) -> dict:
        df_historico = None
        if self.mode == "bootstrap" and input_data.get("csv_historico"):
            df_historico = self._read_and_normalize(input_data["csv_historico"])
            self.logger.info(f"Histórico: {len(df_historico)} filas")

        df_2026 = self._read_and_normalize(input_data["csv_2026"])
        self.logger.info(f"2026: {len(df_2026)} filas")

        dfs = [d for d in [df_historico, df_2026] if d is not None]
        catalogs = self._extract_catalogs(dfs)

        return {
            "df_historico": df_historico,
            "df_2026": df_2026,
            "catalogs": catalogs,
        }

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        clean_directory(Path(f"data/extract/{PIPELINE_NAME}"), self.logger)
        return input_data

    def _read_and_normalize(self, path: str) -> pd.DataFrame:
        df = pd.read_csv(path, encoding="latin1", dtype=str)
        df = df.rename(columns=RENAME)
        df["clave_ent"] = df["clave_ent"].str.zfill(2)
        df["anio"] = pd.array(df["anio"], dtype="Int16")
        for col in MONTH_COLS:
            df[col] = pd.array(df[col], dtype="Int32")
        return df

    def _extract_catalogs(self, dfs: list[pd.DataFrame]) -> dict:
        combined = pd.concat(dfs, ignore_index=True)

        municipio = (
            combined[["cve_municipio", "clave_ent", "entidad", "municipio"]]
            .drop_duplicates(subset=["cve_municipio"])
            .to_dict("records")
        )
        bien_juridico = combined[["bien_juridico_afectado"]].drop_duplicates().to_dict("records")
        tipo = combined[["tipo_delito"]].drop_duplicates().to_dict("records")
        subtipo = (
            combined[["subtipo_delito", "tipo_delito"]].drop_duplicates(subset=["subtipo_delito"]).to_dict("records")
        )
        modalidad = combined[["modalidad", "subtipo_delito"]].drop_duplicates(subset=["modalidad"]).to_dict("records")

        return {
            "municipio": municipio,
            "bien_juridico_afectado": bien_juridico,
            "tipo_delito": tipo,
            "subtipo_delito": subtipo,
            "modalidad": modalidad,
        }
