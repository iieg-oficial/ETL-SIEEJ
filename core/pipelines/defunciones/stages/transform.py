from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.defunciones.constants import (
    CAPITULO_GRUPO_DATASET,
    EDAD_DATASET,
    EDICION_DATASET,
    ETL_MANAGED_COLUMNS,
    FACT_DATASET,
    PIPELINE_NAME,
    REGISTRO_RENAMES,
    TEXT_FACT_COLUMNS,
)
from core.pipelines.defunciones.helpers import catalogs
from core.pipelines.defunciones.mappings import RAZON_MATERNA
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

    def action(self, input_data: dict[str, pd.DataFrame]) -> dict[str, Any]:
        edad_records = catalogs.build_edad_catalog(input_data[EDAD_DATASET])
        if not edad_records:
            raise ValueError("[action] edad catalog produced 0 records")

        built = {EDAD_DATASET: edad_records}
        for model in CATALOG_MODELS:
            name = model.__tablename__
            if name in input_data:
                built[name] = catalogs.build_catalog(input_data[name], model.text_key)
        for model in OVERRIDE_MODELS:
            built[model.__tablename__] = catalogs.static_catalog(_OVERRIDE_SOURCES[model.__tablename__])
        if CAPITULO_GRUPO_DATASET in input_data:
            built[CAPITULO_GRUPO_DATASET] = catalogs.build_capitulo_grupo(input_data[CAPITULO_GRUPO_DATASET])
        if EDICION_DATASET in input_data:
            built[EDICION_DATASET] = catalogs.build_edicion(input_data[EDICION_DATASET])
        for model in VERSIONED_MODELS:
            if model.__tablename__ in input_data:
                built[model.__tablename__] = catalogs.build_versioned(input_data[model.__tablename__])
        for model in CODED_MODELS:
            if model.__tablename__ in input_data:
                built[model.__tablename__] = catalogs.build_coded(input_data[model.__tablename__])

        catalogs.normalize_descriptions(built)
        facts = self._build_facts(input_data[FACT_DATASET])

        self.logger.info(
            "[action] catalogs: %s | facts: %s=%s",
            ", ".join(f"{name}={len(recs)}" for name, recs in built.items()),
            FACT_DATASET,
            f"{len(facts):,}",
        )
        return {"catalogs": built, "facts": {FACT_DATASET: facts}}

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        pd.to_pickle(input_data, self.work_dir / "transform.pkl")
        self.logger.info("[finalization] Saved transform.pkl")
        return input_data
