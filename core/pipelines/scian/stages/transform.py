from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

from core.pipelines.scian.constants import (
    NIVELES,
    NULL_VALUES,
    SHEET_COLUMNS,
    TRINACIONAL_NIVELES,
    TRINACIONAL_SUFFIX,
)
from core.pipelines.stage import Stage
from core.utils.clean import list_values_to_null
from core.utils.logger import get_logger

logger = get_logger("scian.transform")


class ScianTransform(Stage):
    def __init__(self):
        super().__init__("scian", "transform")

    def source(self, input_data: Optional[Any] = None) -> pd.DataFrame:
        pkl_estructura = Path("data/extract/scian/df_estructura.pkl")

        if pkl_estructura.exists():
            logger.info("Loading transform input from extract pkl file")
            return pd.read_pickle(pkl_estructura)

        return input_data

    def _to_long(self, df: pd.DataFrame) -> pd.DataFrame:
        # Cada fila trae exactamente dos celdas llenas y contiguas: el codigo en la
        # columna que corresponde a su nivel y la descripcion en la siguiente.
        valores = df[SHEET_COLUMNS].to_numpy()
        nivel = df[SHEET_COLUMNS].notna().to_numpy().argmax(axis=1)

        fuera_de_nivel = int((nivel >= len(NIVELES)).sum())
        if fuera_de_nivel:
            raise ValueError(f"{fuera_de_nivel} rows with a code outside the {len(NIVELES)} SCIAN levels")

        filas = np.arange(len(df))
        niveles = pd.DataFrame(
            {
                "nivel": nivel,
                "codigo": valores[filas, nivel],
                "descripcion": valores[filas, nivel + 1],
            },
            index=df.index,
        )

        niveles = list_values_to_null(niveles, rm_list=NULL_VALUES)
        incompletas = int(niveles["descripcion"].isna().sum())
        if incompletas:
            raise ValueError(f"{incompletas} rows without a description next to the code")

        return niveles

    def _resolve_jerarquia(self, niveles: pd.DataFrame) -> pd.DataFrame:
        ancestros = niveles.pivot(columns="nivel", values="codigo").ffill().reindex(niveles.index)
        posiciones = (niveles["nivel"] - 1).clip(lower=0)
        padres = ancestros.to_numpy()[np.arange(len(niveles)), posiciones]

        niveles["padre"] = np.where(niveles["nivel"] == 0, None, padres)
        return niveles

    def _limpiar_descripcion(self, niveles: pd.DataFrame) -> pd.DataFrame:
        niveles["comparable_trinacional"] = niveles["descripcion"].str.endswith(TRINACIONAL_SUFFIX)
        niveles["descripcion"] = niveles["descripcion"].str.removesuffix(TRINACIONAL_SUFFIX).str.strip()
        return niveles

    def action(self, input_data: pd.DataFrame) -> dict[str, pd.DataFrame]:
        if input_data.empty:
            logger.info("Empty DataFrame, skipping transform")
            return {f"df_{nivel}": pd.DataFrame() for nivel in NIVELES}

        niveles = self._to_long(input_data)
        niveles = self._resolve_jerarquia(niveles)
        niveles = self._limpiar_descripcion(niveles)

        salida = {}
        for posicion, nombre in enumerate(NIVELES):
            cols = ["codigo", "descripcion"]
            if posicion > 0:
                cols.append("padre")
            if nombre in TRINACIONAL_NIVELES:
                cols.append("comparable_trinacional")

            df_nivel = niveles.loc[niveles["nivel"] == posicion, cols].reset_index(drop=True)
            salida[f"df_{nombre}"] = df_nivel
            logger.info(f"{nombre}: {len(df_nivel)} rows")

        return salida

    def finalization(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        for key, df in input_data.items():
            pkl_path = self.work_dir / f"{key}.pkl"
            df.to_pickle(pkl_path)
            logger.info(f"Saved {key}: {len(df)} rows to {pkl_path}")
        return input_data
