import pandas as pd
from datetime import date
from pathlib import Path
from typing import Any, Optional

from core.db import Database
from core.pipelines.indice_shf_vivienda.attributes import IndiceShfViviendaTables as T
from core.pipelines.indice_shf_vivienda.config import PIPELINE_NAME, settings
from core.pipelines.indice_shf_vivienda.constants import LEVEL_ESTATAL, LEVEL_GLOBAL, LEVEL_MUNICIPAL
from core.pipelines.indice_shf_vivienda.mappings import ENTITY_NAME_ALIASES, SERIE_GLOBAL_SEED
from core.pipelines.indice_shf_vivienda.schemas import LEVEL_MODELS, CatSerieGlobal
from core.pipelines.stage import Stage
from core.utils import df_to_records, normalize_text
from core.utils.bulk_ops import (
    count_records,
    get_cvegeo_mapping,
    get_mapping,
    insert_records,
    sync_id_sequence,
    upsert_records,
)
from core.utils.files import cleanup_pipeline_data


class IndiceShfViviendaLoad(Stage):
    """Seed the series catalog, resolve the geographic keys and upsert the three levels."""

    def __init__(self):
        super().__init__(PIPELINE_NAME, "load")
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> dict[str, pd.DataFrame]:
        base = Path(f"data/transform/{settings.PIPELINE_NAME}")
        pkls = {level: base / f"{level}.pkl" for level in LEVEL_MODELS}

        if all(pkl.exists() for pkl in pkls.values()):
            self.logger.info("Loading transform pkl files")
            return {level: pd.read_pickle(pkl) for level, pkl in pkls.items()}

        return input_data

    def action(self, input_data: dict[str, pd.DataFrame]) -> dict[str, Any]:
        if all(frame.empty for frame in input_data.values()):
            self.logger.warning("No data to load")
            return {"records_before": None}

        try:
            self.db.connect()
            with self.db.get_session() as session:
                series = self._load_catalog(session)

                records_before = {table: count_records(session, model) for table, (model, _) in LEVEL_MODELS.items()}

                frames = {
                    LEVEL_GLOBAL: self._resolve_serie(input_data[LEVEL_GLOBAL].copy(), series),
                    LEVEL_ESTATAL: self._resolve_entidad(session, input_data[LEVEL_ESTATAL].copy()),
                    LEVEL_MUNICIPAL: self._resolve_municipio(session, input_data[LEVEL_MUNICIPAL].copy()),
                }

                for level, frame in frames.items():
                    model, conflict_keys = LEVEL_MODELS[level]
                    self._upsert(session, frame, model, conflict_keys)
        except Exception:
            self.db.disconnect()
            raise

        return {"records_before": records_before}

    def _load_catalog(self, session) -> dict[str, int]:
        """Seed the 15 global series and return the normalized name -> id mapping.

        The ids come from PostgreSQL (SERIAL) and never from the seed list, so
        they stay put across reloads even though the seed fixes the order.
        """
        insert_records(session, SERIE_GLOBAL_SEED, CatSerieGlobal, conflict_keys=["nombre"])
        sync_id_sequence(session, CatSerieGlobal)

        return get_mapping(session, CatSerieGlobal, "nombre", CatSerieGlobal.id.key, is_normalize=True)

    def _resolve_serie(self, df: pd.DataFrame, mapping: dict[str, int]) -> pd.DataFrame:
        if df.empty:
            return df

        df["serie_global_id"] = df["serie_global"].map(normalize_text).map(mapping).astype("Int64")
        self._require_resolved(df, "serie_global_id", "serie_global", str(T.CAT_SERIE_GLOBAL))
        return df

    def _resolve_entidad(self, session, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        mapping = get_cvegeo_mapping(session, table="cvegeo_states", key="nom_ent", value="cve_ent", is_normalize=True)
        nombres = df["estado"].replace(ENTITY_NAME_ALIASES).map(normalize_text)
        df["entidad_id"] = nombres.map(mapping).astype("Int64")
        self._require_resolved(df, "entidad_id", "estado", "cvegeo_states")
        return df

    def _resolve_municipio(self, session, df: pd.DataFrame) -> pd.DataFrame:
        """Resolve each municipality inside its own state.

        Municipality names are not unique nationwide: the source publishes
        'Benito Juárez' for both Ciudad de México and Quintana Roo, and 'Juárez'
        for both Chihuahua and Nuevo León. Looking them up per state is what
        keeps those four rows from collapsing into two.

        The state aliases are deliberately not applied here: 'Veracruz' names
        both an entity and a municipality, and translating it at this level
        would send the port's rows looking for a municipality that does not exist.
        """
        if df.empty:
            return df

        df = self._resolve_entidad(session, df)
        nombres = df["municipio"].map(normalize_text)

        df["municipio_id"] = pd.Series(pd.NA, index=df.index, dtype="Int64")
        for entidad_id in sorted(df["entidad_id"].dropna().unique()):
            mapping = get_cvegeo_mapping(
                session,
                table="cvegeo_municipalities",
                key="nomgeo",
                value="cvegeo",
                cve_ent=int(entidad_id),
                is_normalize=True,
            )
            rows = df["entidad_id"] == entidad_id
            df.loc[rows, "municipio_id"] = nombres[rows].map(mapping).astype("Int64")

        self._require_resolved(df, "municipio_id", "municipio", "cvegeo_municipalities")
        return df

    def _require_resolved(self, df: pd.DataFrame, column: str, source_column: str, catalog: str) -> None:
        """Abort when a name has no key, instead of writing the row without one.

        The resolved key IS the identity of the record: inserting it as NULL
        would keep the number of rows intact while making them unattributable,
        which is worse than not loading at all.
        """
        unresolved = df[df[column].isna()]
        if unresolved.empty:
            return

        names = sorted(unresolved[source_column].dropna().astype(str).unique())
        raise ValueError(
            f"{len(unresolved):,} rows with no match in {catalog}, from {len(names)} unresolved "
            f"'{source_column}' values: {names}. Check the aliases in "
            f"core/pipelines/{settings.PIPELINE_NAME}/mappings.py."
        )

    def _upsert(self, session, df: pd.DataFrame, model, conflict_keys: list[str]) -> None:
        if df.empty:
            self.logger.warning(f"No rows to load into {model.__tablename__}")
            return

        df["fecha_actualizacion"] = date.today()

        cols = [c for c in model.columns() if c != model.id.key]
        df = df.drop_duplicates(subset=conflict_keys, keep="last")
        df_clean = df.astype(object).where(df.notna(), None)
        upsert_records(
            session,
            df_to_records(df_clean, cols),
            model,
            conflict_keys=conflict_keys,
            chunk_size=settings.CHUNK_SIZE,
        )

    def finalization(self, input_data: dict[str, Any]) -> None:
        cleanup_pipeline_data(settings.PIPELINE_NAME)
        if input_data is None or input_data.get("records_before") is None:
            return
        try:
            with self.db.get_session() as session:
                for table, (model, _) in LEVEL_MODELS.items():
                    total = count_records(session, model)
                    inserted = total - input_data["records_before"][table]
                    self.logger.info(f"{total:,} records in {model.__tablename__} ({inserted:,} new in this run)")
        finally:
            self.db.disconnect()
