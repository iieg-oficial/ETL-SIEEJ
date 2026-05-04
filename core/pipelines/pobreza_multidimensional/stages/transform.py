from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.pobreza_multidimensional.consts import PIPELINE_NAME
from core.pipelines.pobreza_multidimensional.helpers import read_excel, wide_to_tidy
from core.pipelines.stage import Stage
from core.utils.files import clean_directory


class PobrezaMultidimensionalTransform(Stage):
    """Transforma el XLSX wide → tidy (municipio × año) y extrae el catálogo de entidades."""

    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "transform")
        self.mode = mode

    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data or not input_data.get("file_path"):
            raise ValueError("Transform no recibió archivo de Extract")
        return input_data

    def action(self, input_data: Optional[Any] = None) -> dict:
        file_path = input_data["file_path"]
        self.logger.info(f"Leyendo: {file_path}")

        df_wide = read_excel(file_path)
        self.logger.info(f"Leídos {len(df_wide)} municipios, {len(df_wide.columns)} columnas")

        df_tidy = wide_to_tidy(df_wide)
        self.logger.info(f"Filas tidy (municipio × año): {len(df_tidy)}")

        catalogs = self._extract_catalogs(df_wide)

        # Sanitizar NaN/NaT residuales → None para SQLAlchemy
        df_tidy = df_tidy.where(pd.notna(df_tidy), other=None)

        return {"df": df_tidy, "catalogs": catalogs, "row_count": len(df_tidy)}

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        clean_directory(Path(f"data/extract/{PIPELINE_NAME}"), self.logger)
        clean_directory(self.work_dir, self.logger)
        return input_data

    def _extract_catalogs(self, df_wide: pd.DataFrame) -> dict:
        """Extrae el catálogo de entidades federativas."""
        cat_entidad = (
            df_wide[["cve_ent", "nombre_ent"]]
            .dropna(subset=["cve_ent"])
            .drop_duplicates(subset=["cve_ent"])
            .sort_values("cve_ent")
            .rename(columns={"cve_ent": "cve_ent", "nombre_ent": "nombre_entidad"})
            .to_dict("records")
        )
        return {"entidad": cat_entidad}
