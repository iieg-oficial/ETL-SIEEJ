import pandas as pd
from pathlib import Path
from typing import Any, Optional

from core.pipelines.enec.attributes import EnecTables as T
from core.pipelines.enec.config import PIPELINE_NAME, settings
from core.pipelines.enec.constants import CVEGEO_NACIONAL, FLOAT_COLS, INT_COLS, NULL_VALUES
from core.pipelines.enec.mappings import ESTATUS_SEED
from core.pipelines.stage import Stage
from core.utils import build_fecha, df_to_records
from core.utils.clean import drop_duplicates_col, list_values_to_null


class EnecTransform(Stage):
    """Normalize types, build the period date and derive the catalogs."""

    def __init__(self):
        super().__init__(PIPELINE_NAME, "transform")

    def source(self, input_data: Optional[Any] = None) -> dict[str, pd.DataFrame]:
        base = Path(f"data/extract/{settings.PIPELINE_NAME}")
        pkl_nacional, pkl_entidad = base / "nacional.pkl", base / "entidad.pkl"

        if pkl_nacional.exists() and pkl_entidad.exists():
            self.logger.info("Loading extract pkl files")
            return {"nacional": pd.read_pickle(pkl_nacional), "entidad": pd.read_pickle(pkl_entidad)}

        return input_data

    def action(self, input_data: dict[str, pd.DataFrame]) -> dict[str, Any]:
        nacional = input_data["nacional"] if input_data else None
        entidad = input_data["entidad"] if input_data else None

        if nacional is None or entidad is None or (nacional.empty and entidad.empty):
            self.logger.warning("Empty input, nothing to transform")
            return {"nacional": pd.DataFrame(), "entidad": pd.DataFrame(), "catalogs": {}}

        nacional = self._prepare(nacional.copy(), "national")
        nacional["codigo_actividad"] = pd.to_numeric(nacional["codigo_actividad"], errors="coerce").astype("Int64")
        nacional = nacional.dropna(subset=["fecha", "codigo_actividad"])

        entidad = self._prepare(entidad.copy(), "state")
        entidad = self._drop_national_rows(entidad)
        entidad["entidad_id"] = pd.to_numeric(entidad["entidad_id"], errors="coerce").astype("Int64")
        entidad = entidad.dropna(subset=["fecha", "entidad_id"])

        self.logger.info(f"{len(nacional):,} national rows and {len(entidad):,} state rows kept")

        catalogs = self._build_catalogs(nacional, entidad)
        return {"nacional": nacional, "entidad": entidad, "catalogs": catalogs}

    def _prepare(self, df: pd.DataFrame, label: str) -> pd.DataFrame:
        """Cast the measures, build the period and clean nulls, in that order."""
        for col in INT_COLS + FLOAT_COLS:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        fecha = build_fecha(df["anio"], df["mes"])
        df = list_values_to_null(df, rm_list=NULL_VALUES)
        df["fecha"] = fecha.dt.date

        for col in INT_COLS:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

        self.logger.info(f"{len(df):,} {label} rows processed")
        return df

    def _drop_national_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove the national aggregate that ships inside the state dataset.

        CVEGEO 00 in the state file is byte-identical to the activity-23 row of
        the national file. Keeping it here would store the national total twice,
        in two tables that could then drift apart.

        CVEGEO 33 ("Obra en el extranjero") stays: it is not a state and does not
        join against cvegeo_states, but it IS part of the national total — the
        32 states alone do not add up to the published value of production.
        """
        national = df["entidad_id"].astype(str).str.strip() == CVEGEO_NACIONAL
        if national.any():
            self.logger.info(f"{int(national.sum()):,} national rows dropped from the state dataset")
        return df[~national]

    def _build_catalogs(self, nacional: pd.DataFrame, entidad: pd.DataFrame) -> dict[str, list[dict]]:
        catalogs = {
            T.CAT_ESTATUS: self._estatus_records(nacional, entidad),
            T.CAT_ACTIVIDAD: self._actividad_records(nacional),
        }

        for table, records in catalogs.items():
            self.logger.info(f"{table}: {len(records)} entries")
        return catalogs

    @staticmethod
    def _estatus_records(nacional: pd.DataFrame, entidad: pd.DataFrame) -> list[dict]:
        """Seed the documented statuses in a fixed order, then add anything new."""
        published = pd.concat([nacional["estatus"], entidad["estatus"]], ignore_index=True).dropna().tolist()
        estatus = pd.DataFrame({"estatus": ESTATUS_SEED + published})
        return df_to_records(drop_duplicates_col(estatus, "estatus"), ["estatus"])

    def _actividad_records(self, nacional: pd.DataFrame) -> list[dict]:
        """Derive the activity catalog from the data: this ZIP ships no catalogs folder."""
        cat = nacional[["codigo_actividad", "descripcion_actividad"]].copy()
        cat = cat.rename(columns={"descripcion_actividad": "descripcion"})
        cat["descripcion"] = cat["descripcion"].str.strip()

        cat = cat.dropna(subset=["codigo_actividad", "descripcion"])
        cat = cat.drop_duplicates(subset=["codigo_actividad"]).sort_values("codigo_actividad")
        return df_to_records(cat, ["codigo_actividad", "descripcion"])

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        if input_data["nacional"].empty and input_data["entidad"].empty:
            self.logger.warning("No transformed data, skipping pkl save")
            return input_data

        input_data["nacional"].to_pickle(self.work_dir / "nacional.pkl")
        input_data["entidad"].to_pickle(self.work_dir / "entidad.pkl")
        pd.to_pickle(input_data["catalogs"], self.work_dir / "catalogs.pkl")
        self.logger.info(f"{len(input_data['catalogs'])} catalogs saved")
        return input_data
