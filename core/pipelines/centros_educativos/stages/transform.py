from typing import Any, Optional
import pandas as pd
from pathlib import Path

from core.pipelines.stage import Stage
from core.utils import df_to_records
from core.utils.clean import list_values_to_null, drop_duplicates_col
from core.utils.logger import get_logger
from core.utils.normalize import capitalize_col, title_col
from core.utils.parse_datetime import parse_date
from core.pipelines.centros_educativos.attributes.centros_educativos import CentrosEducativosTables as T
from core.pipelines.centros_educativos.constants import NULL_VALUES, CAPITALIZE_COLS, TITLE_COLS
from core.utils.accents import apply_accents


class CentrosEducativosTransform(Stage):
    def __init__(self, pipeline_name: str = 'centros_educativos', mode: str = 'bootstrap', entidad: int = None):
        super().__init__(pipeline_name, 'transform')
        self.mode = mode
        self.logger = get_logger(f"{pipeline_name}.transform")
        self.entidad = entidad
    def source(self, input_data: Optional[Any]) -> Any:
        pkl_path = Path(f"data/extract/centros_educativos/centros_educativos_{self.entidad}.pkl")
        self.logger.info(f"[source] Checking for existing pkl at {pkl_path}")
        if pkl_path.exists():
            self.logger.info(f"[source] Loading from pkl: {pkl_path}")
            return pd.read_pickle(pkl_path)
        self.logger.info(f"[source] pkl not found, using extract output")
        output_data = input_data
        return output_data

    def _build_catalogs(self, df: pd.DataFrame) -> dict:
        self.logger.info("[_build_catalogs] Building catalogs from dataframe")

        localidades_df = drop_duplicates_col(df, "localidad").dropna(subset=["localidad_id", "municipio_id", "entidad_id"])
        localidades = []
        self.logger.info(f"[_build_catalogs] Processing {len(localidades_df)} unique localidades")

        for _, row in localidades_df.iterrows():
            cve_geo_id = int(f"{row['entidad_id']:02}{row['municipio_id']:03}{row['localidad_id']:04}")
            localidades.append({
                "cve_geo_id": cve_geo_id,
                "clave_localidad": row["localidad_id"],
                "municipio_id": row["municipio_id"],
                "entidad_id": row["entidad_id"],
                "localidad": row["localidad"]
            })

        self.logger.info(f"[_build_catalogs] Building domicilios catalog")
        domicilios = df_to_records(
            drop_duplicates_col(df, "domicilio").dropna(subset=["domicilio"]),
            ["domicilio", "numero_exterior", "codigo_postal", "entre_calle", "y_calle", "calle_posterior"],
        )
        self.logger.info(f"[_build_catalogs] Found {len(domicilios)} unique domicilios")

        self.logger.info(f"[_build_catalogs] Building colonias catalog")
        colonias = df_to_records(
            drop_duplicates_col(df, "colonia").dropna(subset=["colonia"]),
            ["colonia", "localidad_id", "municipio_id", "entidad_id"],
        )
        self.logger.info(f"[_build_catalogs] Found {len(colonias)} unique colonias")

        return {
            T.LOCALIDADES: localidades,
            T.DOMICILIOS: domicilios,
            T.COLONIAS: colonias,
        }

    def action(self, input_data: Any) -> Any:
        if input_data.empty:
            self.logger.info("[action] Empty DataFrame, skipping transform")
            return {"df": input_data, "catalogs": {}}

        self.logger.info(f"[action] Starting transformation of {len(input_data)} rows")
        df = input_data.copy()

        self.logger.info("[action] Parsing fecha_actualizacion column")
        df["fecha_actualizacion"] = pd.to_datetime(df["fecha_actualizacion"])

        self.logger.info(f"[action] Capitalizing {len(CAPITALIZE_COLS)} columns")
        for col in CAPITALIZE_COLS:
            if col in df.columns:
                capitalize_col(df, col)

        self.logger.info(f"[action] Title casing {len(TITLE_COLS)} columns and applying accents")
        for col in TITLE_COLS:
            if col in df.columns:
                title_col(df, col)
                df[col] = df[col].apply(apply_accents)

        self.logger.info("[action] Converting null values")
        df = list_values_to_null(df, rm_list=NULL_VALUES)

        self.logger.info(f"[action] {len(df)} rows after sanitization")
        return {"df": df, "catalogs": self._build_catalogs(df)}

    def finalization(self, input_data: Any) -> Any:
        df_pkl_path = self.work_dir / f"centros_educativos_df_{self.entidad}.pkl"
        catalogs_pkl_path = self.work_dir / f"centros_educativos_catalogs_{self.entidad}.pkl"

        input_data["df"].to_pickle(df_pkl_path)
        pd.Series(input_data["catalogs"]).to_pickle(catalogs_pkl_path)

        self.logger.info(f"[finalization] {len(input_data['df'])} rows saved to {df_pkl_path}")
        self.logger.info(f"[finalization] {len(input_data['catalogs'])} catalogs saved to {catalogs_pkl_path}")
        return input_data
