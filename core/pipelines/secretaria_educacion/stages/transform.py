from datetime import date
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.constants.geo import JALISCO_CVE_ENTIDAD
from core.pipelines.secretaria_educacion.constants import (
    AULAS_COLUMNS,
    AULAS_GOOGLE_DATASET,
    AULAS_RENAMES,
    CAPITALIZE_COLS,
    CATALOGS_FILENAME,
    DIRECTORIO_COLUMNS,
    DIRECTORIO_DATASET,
    DIRECTORIO_FLOAT_COLUMNS,
    DIRECTORIO_NUMERIC_COLUMNS,
    DIRECTORIO_RENAMES,
    MANIFEST_FILENAME,
    NULL_VALUES,
    PIPELINE_NAME,
    PLAIN_TITLE_COLS,
    PROGRAMAS_COLUMNS,
    PROGRAMAS_DATASET,
    PROGRAMAS_RENAMES,
    SENTINEL_VALUES,
    TITLE_COLS,
    ZERO_TO_NULL_COLUMNS,
)
from core.pipelines.secretaria_educacion.helpers.values import capitalize_es, plain_title, title_es
from core.pipelines.secretaria_educacion.mappings import TURNO_LABELS
from core.pipelines.stage import Stage
from core.utils.clean import list_values_to_null
from core.utils.files import read_json
from core.utils.logger import get_logger
from core.utils.normalize import normalize_text


class SecretariaEducacionTransform(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "transform")
        self.mode = mode
        self.logger = get_logger(f"{PIPELINE_NAME}.transform")

    def source(self, input_data: Optional[Any] = None) -> dict[str, Any]:
        extract_dir = Path("data/extract") / PIPELINE_NAME
        manifest = read_json(extract_dir / MANIFEST_FILENAME) or {}

        frames = {}
        for dataset in manifest:
            pickle_path = extract_dir / f"{dataset}.pkl"
            if pickle_path.exists():
                frames[dataset] = pd.read_pickle(pickle_path)

        if frames:
            self.logger.info(f"[source] Loaded {len(frames)} dataset(s) from extract")
            return {"frames": frames, "manifest": manifest}

        if input_data:
            return input_data

        self.logger.info("[source] No datasets to transform")
        return {"frames": {}, "manifest": manifest}

    def _standardize(self, df: pd.DataFrame, columns: list[str], renames: dict[str, str]) -> pd.DataFrame:
        """Normalize headers, rename to the schema names and keep the modeled columns."""
        df = df.copy()
        df.columns = [normalize_text(column) for column in df.columns]
        df = df.rename(columns=renames)

        missing = [column for column in columns if column not in df.columns]
        if missing:
            raise KeyError(f"Source is missing modeled columns: {missing}")

        return df[columns]

    def _normalize_text_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Turn the all-caps source into readable text with accents restored."""
        for columns, caster in [
            (TITLE_COLS, title_es),
            (CAPITALIZE_COLS, capitalize_es),
            (PLAIN_TITLE_COLS, plain_title),
        ]:
            for column in columns:
                if column in df.columns:
                    df[column] = df[column].map(caster)

        return df

    def _add_dates(self, df: pd.DataFrame, meta: dict[str, Any]) -> pd.DataFrame:
        df["fecha_corte"] = pd.to_datetime(meta["fecha_corte"]).date()
        df["fecha_actualizacion_fuente"] = (
            pd.to_datetime(meta["fecha_actualizacion"]).date() if meta.get("fecha_actualizacion") else None
        )
        df["fecha_actualizacion"] = date.today()
        return df

    def _prepare_directorio(self, df: pd.DataFrame, meta: dict[str, Any]) -> pd.DataFrame:
        df = self._standardize(df, DIRECTORIO_COLUMNS, DIRECTORIO_RENAMES)
        df = self._normalize_text_columns(df)

        # Se expande antes de construir el catálogo, para que columna y catálogo coincidan.
        df["turno"] = df["turno"].replace(TURNO_LABELS)

        df = list_values_to_null(df, rm_list=NULL_VALUES)

        for column in DIRECTORIO_NUMERIC_COLUMNS:
            df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")

        for column in DIRECTORIO_FLOAT_COLUMNS:
            df[column] = pd.to_numeric(df[column], errors="coerce")

        for column in ZERO_TO_NULL_COLUMNS:
            df.loc[df[column].astype(str).isin(["0", "0.0"]), column] = pd.NA

        for column, sentinels in SENTINEL_VALUES.items():
            if column in df.columns:
                df.loc[df[column].isin(sentinels), column] = pd.NA

        df["entidad_id"] = JALISCO_CVE_ENTIDAD
        return self._add_dates(df, meta)

    def _prepare_programas(self, df: pd.DataFrame, meta: dict[str, Any]) -> pd.DataFrame:
        df = self._standardize(df, PROGRAMAS_COLUMNS, PROGRAMAS_RENAMES)

        df["programa_estrategico"] = df["programa_estrategico"].str.replace("_", " ", regex=False)

        df = self._normalize_text_columns(df)
        df = list_values_to_null(df, rm_list=NULL_VALUES)
        return self._add_dates(df, meta)

    def _prepare_aulas(self, df: pd.DataFrame, meta: dict[str, Any]) -> pd.DataFrame:
        # El export del origen arrastra filas vacías al final.
        df = df.dropna(how="all")

        df = self._standardize(df, AULAS_COLUMNS, AULAS_RENAMES)
        df = self._normalize_text_columns(df)
        df = list_values_to_null(df, rm_list=NULL_VALUES)

        df["aulas_asignadas"] = pd.to_numeric(df["aulas_asignadas"], errors="coerce").astype("Int64")
        df["entidad_id"] = JALISCO_CVE_ENTIDAD
        return self._add_dates(df, meta)

    def _build_localidades(self, directorio: pd.DataFrame) -> list[dict[str, Any]]:
        """Localities are catalogued here because cvegeo only covers state and municipality."""
        columns = ["entidad_id", "municipio_id", "clave_localidad", "localidad"]
        unique = directorio[columns].dropna().drop_duplicates(subset=columns[:3])

        registros = []
        for row in unique.itertuples(index=False):
            cve_geo_id = int(f"{row.entidad_id:02}{row.municipio_id:03}{row.clave_localidad:04}")
            registros.append(
                {
                    "cve_geo_id": cve_geo_id,
                    "entidad_id": int(row.entidad_id),
                    "municipio_id": int(row.municipio_id),
                    "clave_localidad": int(row.clave_localidad),
                    "localidad": row.localidad,
                }
            )

        return sorted(registros, key=lambda item: item["cve_geo_id"])

    def _build_colonias(self, directorio: pd.DataFrame) -> list[dict[str, Any]]:
        """Colonias hang from their locality, which is the level cvegeo stops at."""
        columns = ["entidad_id", "municipio_id", "clave_localidad", "clave_colonia", "colonia"]
        unique = directorio[columns].dropna(subset=columns[:3] + ["colonia"]).drop_duplicates(subset=columns[:4])

        registros = []
        for row in unique.itertuples(index=False):
            registros.append(
                {
                    "cve_geo_id": int(f"{row.entidad_id:02}{row.municipio_id:03}{row.clave_localidad:04}"),
                    "clave_colonia": int(row.clave_colonia) if pd.notna(row.clave_colonia) else None,
                    "colonia": row.colonia,
                }
            )

        return registros

    def _build_catalogs(self, prepared: dict[str, pd.DataFrame]) -> dict[str, list[dict[str, Any]]]:
        catalogs: dict[str, list[dict[str, Any]]] = {}

        if DIRECTORIO_DATASET in prepared:
            directorio = prepared[DIRECTORIO_DATASET]
            catalogs["turnos"] = (
                directorio[["turno_id", "turno"]]
                .dropna()
                .drop_duplicates()
                .rename(columns={"turno_id": "id"})
                .sort_values("id")
                .to_dict("records")
            )
            catalogs["regiones"] = (
                directorio[["region_id", "region"]]
                .dropna()
                .drop_duplicates()
                .rename(columns={"region_id": "id"})
                .sort_values("id")
                .to_dict("records")
            )
            for name, column in [
                ("medios", "medio"),
                ("sostenimientos", "sostenimiento"),
                ("niveles", "nivel"),
                ("programas", "programa"),
            ]:
                values = sorted(directorio[column].dropna().unique())
                catalogs[name] = [{column: value} for value in values]

            catalogs["localidades"] = self._build_localidades(directorio)
            catalogs["colonias"] = self._build_colonias(directorio)

        if PROGRAMAS_DATASET in prepared:
            values = sorted(prepared[PROGRAMAS_DATASET]["programa_estrategico"].dropna().unique())
            catalogs["programas_estrategicos"] = [{"programa_estrategico": value} for value in values]

        if AULAS_GOOGLE_DATASET in prepared:
            values = sorted(prepared[AULAS_GOOGLE_DATASET]["region_operativa"].dropna().unique())
            catalogs["regiones_operativas"] = [{"region_operativa": value} for value in values]

        return catalogs

    def action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        frames = input_data["frames"]
        manifest = input_data["manifest"]

        if not frames:
            self.logger.info("[action] Nothing to transform")
            return {"frames": {}, "manifest": manifest, "catalogs": {}}
        preparers = {
            DIRECTORIO_DATASET: self._prepare_directorio,
            PROGRAMAS_DATASET: self._prepare_programas,
            AULAS_GOOGLE_DATASET: self._prepare_aulas,
        }

        prepared = {}
        for dataset, df in frames.items():
            prepared[dataset] = preparers[dataset](df, manifest[dataset])
            self.logger.info(f"[action] {dataset}: {len(prepared[dataset]):,} rows prepared")

        return {"frames": prepared, "manifest": manifest, "catalogs": self._build_catalogs(prepared)}

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        for dataset, df in input_data["frames"].items():
            df.to_pickle(self.work_dir / f"{dataset}.pkl")
            self.logger.info(f"[finalization] {dataset}: {len(df):,} rows saved")

        pd.to_pickle(input_data["catalogs"], self.work_dir / CATALOGS_FILENAME)
        self.logger.info(f"[finalization] {len(input_data['catalogs'])} catalog(s) saved")

        return input_data
