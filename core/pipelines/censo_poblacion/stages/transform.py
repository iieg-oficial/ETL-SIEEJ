from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.stage import Stage
from core.pipelines.censo_poblacion.attributes.censo_poblacion import CensoPoblacionTables as T
from core.pipelines.censo_poblacion.constants import LOC_FILTER_VALUES, NULL_VALUES, NUMERIC_COLS, POBLACION_COLS
from core.pipelines.censo_poblacion.mappings import FUENTES_FECHA
from core.utils.clean import list_values_to_null
from core.utils.logger import get_logger

logger = get_logger("censo_poblacion.transform")


class CensoPoblacionTransform(Stage):
    def __init__(self):
        super().__init__("censo_poblacion", "transform")

    def source(self, input_data: Optional[Any] = None) -> dict[str, pd.DataFrame]:
        pkl_2010 = Path("data/extract/censo_poblacion/df_2010.pkl")
        pkl_2015 = Path("data/extract/censo_poblacion/df_2015.pkl")
        pkl_2020 = Path("data/extract/censo_poblacion/df_2020.pkl")

        if pkl_2010.exists() and pkl_2015.exists() and pkl_2020.exists():
            logger.info("Loading transform input from extract pkl files")
            return {
                "df_2010": pd.read_pickle(pkl_2010),
                "df_2015": pd.read_pickle(pkl_2015),
                "df_2020": pd.read_pickle(pkl_2020),
            }

        return input_data

    def _process_iter(self, df: pd.DataFrame, fuente_id: int) -> tuple[pd.DataFrame, list[dict]]:
        df = df[~df["localidad_id"].isin(LOC_FILTER_VALUES)].copy()
        df = list_values_to_null(df, rm_list=NULL_VALUES)

        for col in NUMERIC_COLS:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=["total"])
        df["total"] = df["total"].astype(int)
        for col in ["total_mujeres", "total_hombres", "viviendas_habitadas"]:
            df[col] = df[col].where(df[col].notna(), other=None)

        df["cve_geo_id"] = df.apply(
            lambda row: int(f"{int(row['entidad_id']):02}{int(row['municipio_id']):03}{int(row['localidad_id']):04}"),
            axis=1,
        )

        localidades = (
            df[["cve_geo_id", "localidad"]]
            .drop_duplicates(subset=["cve_geo_id"])
            .dropna(subset=["localidad"])
            .rename(columns={"cve_geo_id": "id"})
            .to_dict("records")
        )

        df["localidad_id"] = df["cve_geo_id"]
        df["fuente_id"] = fuente_id
        return df[POBLACION_COLS], localidades

    def _process_2015(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.dropna(subset=["entidad", "municipio"]).copy()
        df = df[df["municipio"].str.match(r"^\d+")]

        df["entidad_id"] = df["entidad"].str.extract(r"^(\d+)").squeeze().astype(int)
        df["municipio_id"] = df["municipio"].str.extract(r"^(\d+)").squeeze().astype(int)

        df_pivot = df.pivot_table(
            index=["entidad_id", "municipio_id"],
            columns="sexo",
            values="total",
            aggfunc="first",
        ).reset_index()
        df_pivot.columns.name = None
        df_pivot = df_pivot.rename(columns={"Total": "total", "Hombres": "total_hombres", "Mujeres": "total_mujeres"})

        df_pivot = df_pivot.dropna(subset=["total"])
        df_pivot["total"] = df_pivot["total"].astype(int)
        df_pivot["localidad_id"] = None
        df_pivot["viviendas_habitadas"] = None
        df_pivot["fuente_id"] = 2
        return df_pivot[POBLACION_COLS]

    def _build_localidades(self, localidades_2010: list[dict], localidades_2020: list[dict]) -> list[dict]:
        combined = {r["id"]: r for r in localidades_2010}
        combined.update({r["id"]: r for r in localidades_2020})
        return list(combined.values())

    def action(self, input_data: dict[str, pd.DataFrame]) -> dict[str, Any]:
        logger.info("Processing 2010 census data")
        df_2010, localidades_2010 = self._process_iter(input_data["df_2010"], fuente_id=1)
        logger.info(f"2010: {len(df_2010)} locality rows, {len(localidades_2010)} localidades")

        logger.info("Processing 2020 census data")
        df_2020, localidades_2020 = self._process_iter(input_data["df_2020"], fuente_id=3)
        logger.info(f"2020: {len(df_2020)} locality rows, {len(localidades_2020)} localidades")

        logger.info("Processing 2015 intercensal data")
        df_2015 = self._process_2015(input_data["df_2015"])
        logger.info(f"2015: {len(df_2015)} municipality rows")

        localidades = self._build_localidades(localidades_2010, localidades_2020)
        logger.info(f"Total unique localidades: {len(localidades)}")

        fuentes = [
            {"id": fuente_id, "descripcion": desc, "fecha": FUENTES_FECHA[fuente_id]}
            for fuente_id, desc in [
                (1, "Censo de Población y Vivienda 2010"),
                (2, "Encuesta Intercensal 2015"),
                (3, "Censo de Población y Vivienda 2020"),
            ]
        ]

        df_poblacion = pd.concat([df_2010, df_2015, df_2020], ignore_index=True)
        logger.info(f"Total poblacion rows: {len(df_poblacion)}")

        return {
            "df": df_poblacion,
            "catalogs": {
                T.LOCALIDADES: localidades,
                T.FUENTES: fuentes,
            },
        }

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        df_pkl = self.work_dir / "poblacion_df.pkl"
        catalogs_pkl = self.work_dir / "poblacion_catalogs.pkl"

        input_data["df"].to_pickle(df_pkl)
        pd.Series(input_data["catalogs"]).to_pickle(catalogs_pkl)

        logger.info(f"Saved {len(input_data['df'])} rows to {df_pkl}")
        logger.info(f"Saved {len(input_data['catalogs'])} catalogs to {catalogs_pkl}")
        return input_data
