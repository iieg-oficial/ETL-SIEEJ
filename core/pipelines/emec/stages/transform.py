import pandas as pd
from pathlib import Path
from typing import Any, Optional

from core.pipelines.emec.attributes import EmecTables as T
from core.pipelines.emec.config import PIPELINE_NAME, settings
from core.pipelines.emec.constants import FLOAT_COLS, NULL_VALUES
from core.pipelines.emec.mappings import ESTATUS_SEED
from core.pipelines.stage import Stage
from core.utils import build_fecha, df_to_records
from core.utils.clean import drop_duplicates_col, list_values_to_null


class EmecTransform(Stage):
    """Normalize types, build the period date, resolve the entity key and derive the catalogs."""

    def __init__(self):
        super().__init__(PIPELINE_NAME, "transform")

    def source(self, input_data: Optional[Any] = None) -> dict[str, pd.DataFrame]:
        base = Path(f"data/extract/{settings.PIPELINE_NAME}")
        pkl_df, pkl_actividades = base / "extract.pkl", base / "actividades.pkl"

        if pkl_df.exists() and pkl_actividades.exists():
            self.logger.info("Loading extract pkl files")
            return {"df": pd.read_pickle(pkl_df), "actividades": pd.read_pickle(pkl_actividades)}

        return input_data

    def action(self, input_data: dict[str, pd.DataFrame]) -> dict[str, Any]:
        df = input_data["df"] if input_data else None
        if df is None or df.empty:
            self.logger.warning("Empty input, nothing to transform")
            return {"df": pd.DataFrame(), "catalogs": {}}

        df = df.copy()
        self.logger.info(f"Processing {len(df):,} rows")

        for col in FLOAT_COLS:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        fecha = build_fecha(df["anio"], df["mes"])

        df = list_values_to_null(df, rm_list=NULL_VALUES)

        df["fecha"] = fecha.dt.date
        df["codigo_actividad"] = pd.to_numeric(df["codigo_actividad"], errors="coerce").astype("Int64")

        df = df.dropna(subset=["fecha", "codigo_actividad", "entidad"])
        self.logger.info(f"{len(df):,} rows with a valid period, entity and activity code")

        catalogs = self._build_catalogs(df, input_data["actividades"])
        return {"df": df, "catalogs": catalogs}

    def _build_catalogs(self, df: pd.DataFrame, actividades: pd.DataFrame) -> dict[str, list[dict]]:
        catalogs = {
            T.CAT_ESTATUS: self._estatus_records(df),
            T.CAT_ACTIVIDAD: self._actividad_records(actividades),
        }

        for table, records in catalogs.items():
            self.logger.info(f"{table}: {len(records)} entries")
        return catalogs

    @staticmethod
    def _estatus_records(df: pd.DataFrame) -> list[dict]:
        """Seed the three documented statuses, then add anything new the edition brings.

        The seed goes first so the ids stay stable across editions: a revision
        that introduces "Cifras revisadas" must not renumber the statuses that
        stg_emec already points at.
        """
        published = df["estatus"].dropna().tolist()
        estatus = pd.DataFrame({"estatus": ESTATUS_SEED + published})
        return df_to_records(drop_duplicates_col(estatus, "estatus"), ["estatus"])

    def _actividad_records(self, actividades: pd.DataFrame) -> list[dict]:
        cat = actividades.copy()
        cat["codigo_actividad"] = pd.to_numeric(cat["codigo_actividad"], errors="coerce").astype("Int64")
        cat["descripcion"] = cat["descripcion"].str.strip()

        cat = cat.dropna(subset=["codigo_actividad", "descripcion"])
        cat = cat.drop_duplicates(subset=["codigo_actividad"])
        return df_to_records(cat, ["codigo_actividad", "descripcion"])

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        if input_data["df"].empty:
            self.logger.warning("No transformed data, skipping pkl save")
            return input_data

        input_data["df"].to_pickle(self.work_dir / "transform.pkl")
        pd.to_pickle(input_data["catalogs"], self.work_dir / "catalogs.pkl")
        self.logger.info(f"{len(input_data['df']):,} rows and {len(input_data['catalogs'])} catalogs saved")
        return input_data
