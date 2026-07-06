import re
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.defunciones.constants import (
    ANIO_CATALOG,
    CAPITULO_GRUPO_DATASET,
    CHAPTER_TOTAL_GPO,
    CLAVE_COL,
    DESCRIPCION_COL,
    EDAD_DATASET,
    EDICION_DATASET,
    ETL_MANAGED_COLUMNS,
    FACT_DATASET,
    DEFUNCIONES_ACCENT_MAP,
    DEFUNCIONES_CANONICAL_TOKENS,
    NOMBRE_EDAD_COL,
    PIPELINE_NAME,
    PROPER_NOUN_CATALOGS,
    REGISTRO_RENAMES,
    TEXT_FACT_COLUMNS,
)
from core.pipelines.defunciones.mappings import RAZON_MATERNA
from core.utils.accents import apply_accents
from core.pipelines.defunciones.schemas import (
    CATALOG_MODELS,
    CODED_MODELS,
    OVERRIDE_MODELS,
    VERSIONED_MODELS,
    CatRazonMaterna,
    StgDefunciones,
)
from core.pipelines.stage import Stage
from core.utils.logger import get_logger

_OVERRIDE_SOURCES = {CatRazonMaterna.__tablename__: RAZON_MATERNA}


class DefuncionesTransform(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "transform")
        self.mode = mode
        self.logger = get_logger(f"{PIPELINE_NAME}.transform")

    def source(self, input_data: Optional[Any] = None) -> dict[str, pd.DataFrame]:
        extract_dir = Path("data/extract") / PIPELINE_NAME
        loaded: dict[str, pd.DataFrame] = {}
        for path in sorted(extract_dir.glob("*.pkl")):
            loaded[path.stem] = pd.read_pickle(path)
        for required in (EDAD_DATASET, FACT_DATASET):
            if required not in loaded:
                raise FileNotFoundError(f"[source] Missing extract pickle: {required}")
        self.logger.info("[source] Loaded %s extract pickles from %s", len(loaded), extract_dir)
        return loaded

    def _build_edad_catalog(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        catalog = df.copy()
        catalog[CLAVE_COL] = pd.to_numeric(catalog[CLAVE_COL], errors="coerce")
        catalog[DESCRIPCION_COL] = catalog[DESCRIPCION_COL].str.strip()

        catalog = (
            catalog.dropna(subset=[CLAVE_COL, DESCRIPCION_COL])
            .drop_duplicates(subset=[CLAVE_COL])
            .astype({CLAVE_COL: int})
            .rename(columns={CLAVE_COL: "id", DESCRIPCION_COL: NOMBRE_EDAD_COL})
        )
        return catalog[["id", NOMBRE_EDAD_COL]].to_dict("records")

    @staticmethod
    def _static_catalog(mapping: dict[int, str]) -> list[dict[str, Any]]:
        return [{"id": code, "descripcion": desc} for code, desc in mapping.items()]

    @staticmethod
    def _build_capitulo_grupo(df: pd.DataFrame) -> list[dict[str, Any]]:
        catalog = df.copy()
        catalog["cap"] = pd.to_numeric(catalog["cap"], errors="coerce")
        catalog["gpo"] = pd.to_numeric(catalog["gpo"].replace("", str(CHAPTER_TOTAL_GPO)), errors="coerce")
        catalog["descripcion"] = catalog["descripcion"].str.strip()
        catalog = (
            catalog.dropna(subset=["cap", "gpo", "descripcion"])
            .drop_duplicates(subset=["cap", "gpo"])
            .astype({"cap": int, "gpo": int})
        )
        return catalog[["cap", "gpo", "descripcion"]].to_dict("records")

    @staticmethod
    def _build_edicion(df: pd.DataFrame) -> list[dict[str, Any]]:
        return [{"anio": int(a), "descripcion": f"Edición {int(a)}"} for a in df["anio"]]

    @staticmethod
    def _build_coded(df: pd.DataFrame) -> list[dict[str, Any]]:
        cat = df.copy()
        cat["codigo"] = cat[CLAVE_COL].str.strip()
        cat["descripcion"] = cat[DESCRIPCION_COL].str.strip()
        cat = cat[cat["codigo"] != ""].drop_duplicates(subset=["codigo"])
        return cat[["codigo", "descripcion"]].to_dict("records")

    @staticmethod
    def _build_versioned(df: pd.DataFrame) -> list[dict[str, Any]]:
        cat = df.copy()
        cat["codigo"] = pd.to_numeric(cat[CLAVE_COL], errors="coerce")
        cat["descripcion"] = cat[DESCRIPCION_COL].str.strip()
        cat = (
            cat.dropna(subset=["codigo", "descripcion"])
            .drop_duplicates(subset=["codigo", "edicion"])
            .astype({"codigo": int, "edicion": int})
            .rename(columns={"edicion": "anio"})
        )
        return cat[["codigo", "anio", "descripcion"]].to_dict("records")

    @staticmethod
    def _build_catalog(df: pd.DataFrame, text_key: bool) -> list[dict[str, Any]]:
        catalog = df.copy()
        catalog[DESCRIPCION_COL] = catalog[DESCRIPCION_COL].str.strip()
        if text_key:
            catalog[CLAVE_COL] = catalog[CLAVE_COL].str.strip()
            catalog = catalog[catalog[CLAVE_COL] != ""]
        else:
            catalog[CLAVE_COL] = pd.to_numeric(catalog[CLAVE_COL], errors="coerce")

        catalog = (
            catalog.dropna(subset=[CLAVE_COL, DESCRIPCION_COL])
            .drop_duplicates(subset=[CLAVE_COL])
            .rename(columns={CLAVE_COL: "id"})
        )
        if not text_key:
            catalog["id"] = catalog["id"].astype(int)
        return catalog[["id", DESCRIPCION_COL]].to_dict("records")

    def _reconcile(self, source_columns: set[str], target_columns: set[str]) -> None:
        mapped_source = {REGISTRO_RENAMES.get(col, col) for col in source_columns}
        unknown = mapped_source - target_columns
        missing = target_columns - mapped_source
        if unknown:
            self.logger.warning("[reconcile] registro columns NOT modeled (ignored): %s", sorted(unknown))
        if missing:
            self.logger.info("[reconcile] modeled columns absent in this edition (-> NULL): %s", sorted(missing))

    def _build_facts(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        target_columns = set(StgDefunciones.columns()) - ETL_MANAGED_COLUMNS
        self._reconcile(set(df.columns), target_columns)

        facts = df.rename(columns=REGISTRO_RENAMES)
        keep = [col for col in facts.columns if col in target_columns]
        facts = facts[keep].copy()

        for col in keep:
            stripped = facts[col].str.strip()
            if col in TEXT_FACT_COLUMNS:
                facts[col] = stripped.replace("", None)
            else:
                facts[col] = pd.to_numeric(stripped, errors="coerce").astype("Int64")

        clean = facts.astype(object).where(facts.notna(), None)
        return clean.to_dict("records")

    @staticmethod
    def _restore_acronyms(text: str) -> str:
        for token in DEFUNCIONES_CANONICAL_TOKENS:
            text = re.sub(rf"\b{token}\b", token, text, flags=re.IGNORECASE)
        return text

    def _normalize_descriptions(self, catalogs: dict[str, list[dict[str, Any]]]) -> None:
        for name, records in catalogs.items():
            if name in PROPER_NOUN_CATALOGS:
                continue
            field = NOMBRE_EDAD_COL if name == EDAD_DATASET else "descripcion"
            for record in records:
                value = record.get(field)
                if isinstance(value, str):
                    value = self._restore_acronyms(apply_accents(value, DEFUNCIONES_ACCENT_MAP))
                    if name == ANIO_CATALOG:
                        value = re.sub(r"^Año\s+", "", value)
                    record[field] = value

    def action(self, input_data: dict[str, pd.DataFrame]) -> dict[str, Any]:
        edad_records = self._build_edad_catalog(input_data[EDAD_DATASET])
        if not edad_records:
            raise ValueError("[action] edad catalog produced 0 records")

        catalogs = {EDAD_DATASET: edad_records}
        for model in CATALOG_MODELS:
            name = model.__tablename__
            if name in input_data:
                catalogs[name] = self._build_catalog(input_data[name], model.text_key)
        for model in OVERRIDE_MODELS:
            catalogs[model.__tablename__] = self._static_catalog(_OVERRIDE_SOURCES[model.__tablename__])
        if CAPITULO_GRUPO_DATASET in input_data:
            catalogs[CAPITULO_GRUPO_DATASET] = self._build_capitulo_grupo(input_data[CAPITULO_GRUPO_DATASET])
        if EDICION_DATASET in input_data:
            catalogs[EDICION_DATASET] = self._build_edicion(input_data[EDICION_DATASET])
        for model in VERSIONED_MODELS:
            if model.__tablename__ in input_data:
                catalogs[model.__tablename__] = self._build_versioned(input_data[model.__tablename__])
        for model in CODED_MODELS:
            if model.__tablename__ in input_data:
                catalogs[model.__tablename__] = self._build_coded(input_data[model.__tablename__])

        self._normalize_descriptions(catalogs)
        facts = self._build_facts(input_data[FACT_DATASET])

        self.logger.info(
            "[action] catalogs: %s | facts: %s=%s",
            ", ".join(f"{name}={len(recs)}" for name, recs in catalogs.items()),
            FACT_DATASET,
            f"{len(facts):,}",
        )
        return {"catalogs": catalogs, "facts": {FACT_DATASET: facts}}

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        pd.to_pickle(input_data, self.work_dir / "transform.pkl")
        self.logger.info("[finalization] Saved transform.pkl")
        return input_data
