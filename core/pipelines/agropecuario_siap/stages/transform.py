import pandas as pd
from pathlib import Path
from typing import Any, Optional

from core.pipelines.agropecuario_siap.attributes import AgropecuarioTables as T
from core.pipelines.agropecuario_siap.config import settings
from core.pipelines.agropecuario_siap.constants import FLOAT_COLS, NULL_VALUES, TITLE_COLS
from core.pipelines.agropecuario_siap.mappings import CICLOS, MODALIDADES, UNIDADES_MEDIDA
from core.pipelines.stage import Stage
from core.utils import df_to_records
from core.utils.clean import drop_duplicates_col, list_values_to_null
from core.utils.logger import get_logger
from core.utils.normalize import title_col


class AgropecuarioTransform(Stage):
    def __init__(self, year: int):
        super().__init__(settings.PIPELINE_NAME, "transform")
        self.year = year
        self.logger = get_logger(f"{settings.PIPELINE_NAME}.transform")

    def source(self, input_data: Optional[Any] = None) -> pd.DataFrame:
        pkl_path = Path(f"data/extract/{settings.PIPELINE_NAME}/extract_{self.year}.pkl")
        if pkl_path.exists():
            self.logger.info(f"Loading extract pkl for {self.year}")
            return pd.read_pickle(pkl_path)
        return input_data

    def _build_catalogs(self, df: pd.DataFrame) -> dict:
        catalogs = {}

        cultivos = drop_duplicates_col(df, "cultivo").dropna(subset=["cultivo", "cultivo_id"])
        catalogs[T.CAT_CULTIVOS] = df_to_records(
            cultivos.rename(columns={"cultivo_id": "codigo_siap"}), ["codigo_siap", "cultivo"]
        )

        catalogs[T.CAT_UNIDADES_MEDIDA] = [{"id": k, "unidad_med": v} for k, v in UNIDADES_MEDIDA.items()]
        catalogs[T.CAT_MODALIDADES] = [{"id": k, "modalidad": v} for k, v in MODALIDADES.items()]
        catalogs[T.CAT_CICLOS] = [{"id": k, "tipo_ciclo": v} for k, v in CICLOS.items()]

        ctrs = drop_duplicates_col(df, "ctr_apoyo_des_rural").dropna(
            subset=["ctr_apoyo_des_rural", "ctr_apoyo_des_rural_id"]
        )
        catalogs[T.CAT_CTRS_APOYO_DES_RURAL] = df_to_records(
            ctrs.rename(columns={"ctr_apoyo_des_rural_id": "codigo_siap"}), ["codigo_siap", "ctr_apoyo_des_rural"]
        )

        distritos = drop_duplicates_col(df, "dis_des_rural").dropna(subset=["dis_des_rural", "distrito_des_rural_id"])
        distritos = distritos.drop_duplicates(subset=["distrito_des_rural_id"])
        catalogs[T.CAT_DISTRITOS_DES_RURAL] = df_to_records(
            distritos.rename(columns={"distrito_des_rural_id": "id"}), ["id", "dis_des_rural"]
        )

        for table, records in catalogs.items():
            self.logger.info(f"[catalogs] {table}: {len(records)} entries")

        return catalogs

    def action(self, input_data: pd.DataFrame) -> dict[str, Any]:
        if input_data is None or (isinstance(input_data, pd.DataFrame) and input_data.empty):
            self.logger.info("Empty input, skipping transform")
            return {"df": pd.DataFrame(), "catalogs": {}}

        df = input_data.copy()
        self.logger.info(f"Processing {len(df)} rows for {self.year}")

        for col in FLOAT_COLS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        self.logger.info("mapping NULL values")
        df = list_values_to_null(df, rm_list=NULL_VALUES)
        self.logger.info("Changing title columns")
        for col in TITLE_COLS:
            if col in df.columns:
                title_col(df, col)
        catalogs = self._build_catalogs(df)

        self.logger.info(f"Done: {len(df)} rows processed")
        return {"df": df, "catalogs": catalogs}

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        if input_data["df"].empty:
            self.logger.info("No data, skipping save")
            return input_data
        pkl_path = self.work_dir / f"transform_{self.year}.pkl"
        input_data["df"].to_pickle(pkl_path)
        pd.to_pickle(input_data["catalogs"], self.work_dir / f"catalogs_{self.year}.pkl")
        self.logger.info(f"{self.year}: {len(input_data['df'])} rows, {len(input_data['catalogs'])} catalogs saved")
        return input_data
