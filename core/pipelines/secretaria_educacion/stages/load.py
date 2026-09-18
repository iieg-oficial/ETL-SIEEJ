from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from sqlalchemy import delete, text

from core.constants.geo import JALISCO_CVE_ENTIDAD
from core.db import Database
from core.pipelines.secretaria_educacion.config import settings
from core.pipelines.secretaria_educacion.constants import (
    AULAS_GOOGLE_DATASET,
    DIRECTORIO_DATASET,
    MANIFEST_FILENAME,
    PIPELINE_NAME,
    PROGRAMAS_DATASET,
)
from core.pipelines.secretaria_educacion.schemas import (
    CargasAcervo,
    CatColonias,
    CatLocalidades,
    CatMedios,
    CatNiveles,
    CatProgramas,
    CatProgramasEstrategicos,
    CatRegiones,
    CatRegionesOperativas,
    CatSostenimientos,
    CatTurnos,
    StgAulasGoogle,
    StgDirectorioCentrosTrabajo,
    StgEscuelasProgramasEstrategicos,
)
from core.pipelines.stage import Stage
from core.utils import df_to_records
from core.utils.bulk_ops import (
    bulk_insert,
    count_records,
    get_mapping,
    insert_records,
    sync_id_sequence,
    upsert_records,
)
from core.utils.files import cleanup_pipeline_data, read_json
from core.utils.logger import get_logger
from core.utils.normalize import strip_accents

# Catálogos con id propio del origen, que se insertan tal cual.
SOURCE_ID_CATALOGS = [
    ("turnos", CatTurnos),
    ("regiones", CatRegiones),
]

# Catálogos con id autoincremental, deduplicados por su valor.
GENERATED_ID_CATALOGS = [
    ("medios", CatMedios, "medio"),
    ("sostenimientos", CatSostenimientos, "sostenimiento"),
    ("niveles", CatNiveles, "nivel"),
    ("programas", CatProgramas, "programa"),
    ("programas_estrategicos", CatProgramasEstrategicos, "programa_estrategico"),
    ("regiones_operativas", CatRegionesOperativas, "region_operativa"),
]

DATASET_MODELS = {
    DIRECTORIO_DATASET: StgDirectorioCentrosTrabajo,
    PROGRAMAS_DATASET: StgEscuelasProgramasEstrategicos,
    AULAS_GOOGLE_DATASET: StgAulasGoogle,
}


class SecretariaEducacionLoad(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode
        self.logger = get_logger(f"{PIPELINE_NAME}.load")
        self.db = Database(PIPELINE_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> dict[str, Any]:
        transform_dir = Path("data/transform") / PIPELINE_NAME
        manifest = read_json(Path("data/extract") / PIPELINE_NAME / MANIFEST_FILENAME) or {}

        frames = {}
        for dataset in manifest:
            pickle_path = transform_dir / f"{dataset}.pkl"
            if pickle_path.exists():
                frames[dataset] = pd.read_pickle(pickle_path)

        if frames:
            self.logger.info(f"[source] Loaded {len(frames)} dataset(s) from transform")
            return {"frames": frames, "manifest": manifest, "catalogs": input_data["catalogs"]}

        return input_data

    def _load_catalogs(self, session, catalogs: dict[str, list[dict[str, Any]]]) -> None:
        # Estos llevan el id del origen, así que se actualizan: si la dependencia
        # corrige una etiqueta, un DO NOTHING dejaría el valor viejo para siempre.
        for name, model in SOURCE_ID_CATALOGS:
            if catalogs.get(name):
                upsert_records(session, catalogs[name], model, conflict_keys=["id"])

        for name, model, value_column in GENERATED_ID_CATALOGS:
            if not catalogs.get(name):
                continue
            sync_id_sequence(session, model)
            insert_records(session, catalogs[name], model, conflict_keys=[value_column])

        if catalogs.get("localidades"):
            sync_id_sequence(session, CatLocalidades)
            insert_records(session, catalogs["localidades"], CatLocalidades, conflict_keys=["cve_geo_id"])

        if catalogs.get("colonias"):
            self._load_colonias(session, catalogs["colonias"])

    def _load_colonias(self, session, colonias: list[dict[str, Any]]) -> None:
        """Colonias reference their locality, so the cve_geo_id resolves to its id first."""
        localidades = get_mapping(session, CatLocalidades, "cve_geo_id", "id")

        registros = []
        for colonia in colonias:
            localidad_id = localidades.get(colonia["cve_geo_id"])
            if localidad_id is None:
                continue
            registros.append(
                {
                    "localidad_id": localidad_id,
                    "clave_colonia": colonia["clave_colonia"],
                    "colonia": colonia["colonia"],
                }
            )

        sync_id_sequence(session, CatColonias)
        insert_records(session, registros, CatColonias, conflict_keys=["localidad_id", "clave_colonia"])

    def _municipios_por_nombre(self, session) -> dict[str, int]:
        """Map normalized municipality names to their cvegeo key."""
        rows = session.execute(
            text("SELECT cve_mun, nomgeo FROM cvegeo_municipalities WHERE cve_ent = :ent"),
            {"ent": JALISCO_CVE_ENTIDAD},
        ).all()
        return {strip_accents(str(nombre)).lower(): int(cve) for cve, nombre in rows}

    def _map_directorio(self, session, df: pd.DataFrame) -> pd.DataFrame:
        mapped = df.copy()

        for column, model, key in [
            ("medio", CatMedios, "medio"),
            ("sostenimiento", CatSostenimientos, "sostenimiento"),
            ("nivel", CatNiveles, "nivel"),
            ("programa", CatProgramas, "programa"),
        ]:
            mapping = get_mapping(session, model, key, "id")
            mapped[f"{column}_id"] = mapped[column].map(mapping)

        localidades = get_mapping(session, CatLocalidades, "cve_geo_id", "id")
        cve_geo = (
            mapped["entidad_id"].astype("Int64").astype(str).str.zfill(2)
            + mapped["municipio_id"].astype("Int64").astype(str).str.zfill(3)
            + mapped["clave_localidad"].astype("Int64").astype(str).str.zfill(4)
        )
        mapped["localidad_id"] = pd.to_numeric(cve_geo, errors="coerce").map(localidades)

        colonias = {
            (localidad_id, clave): colonia_id
            for colonia_id, localidad_id, clave in session.query(
                CatColonias.id, CatColonias.localidad_id, CatColonias.clave_colonia
            ).all()
        }
        mapped["colonia_id"] = [
            colonias.get((localidad_id, clave))
            for localidad_id, clave in zip(mapped["localidad_id"], mapped["clave_colonia"])
        ]

        return mapped

    def _map_aulas(self, session, df: pd.DataFrame) -> pd.DataFrame:
        """The source only ships the municipality name, so it resolves against cvegeo."""
        mapped = df.copy()

        mapping = get_mapping(session, CatRegionesOperativas, "region_operativa", "id")
        mapped["region_operativa_id"] = mapped["region_operativa"].map(mapping)

        municipios = self._municipios_por_nombre(session)
        claves = mapped["municipio"].map(
            lambda v: municipios.get(strip_accents(str(v)).lower()) if pd.notna(v) else None
        )
        mapped["municipio_id"] = pd.array(claves, dtype="Int64")

        sin_match = mapped.loc[mapped["municipio_id"].isna(), "municipio"].dropna().unique()
        if len(sin_match):
            self.logger.warning(f"[action] municipios sin equivalencia en cvegeo: {sorted(sin_match)}")

        return mapped

    def _map_foreign_keys(self, session, dataset: str, df: pd.DataFrame) -> pd.DataFrame:
        if dataset == DIRECTORIO_DATASET:
            return self._map_directorio(session, df)

        if dataset == AULAS_GOOGLE_DATASET:
            return self._map_aulas(session, df)

        mapped = df.copy()
        mapping = get_mapping(session, CatProgramasEstrategicos, "programa_estrategico", "id")
        mapped["programa_estrategico_id"] = mapped["programa_estrategico"].map(mapping)
        return mapped

    def _records_from_df(self, df: pd.DataFrame, model) -> list[dict[str, Any]]:
        columns = [column for column in model.columns() if column != model.id.key]
        clean_df = df.astype(object).where(pd.notna(df), None)
        return df_to_records(clean_df, columns)

    def _reload_dataset(self, session, dataset: str, df: pd.DataFrame) -> None:
        """Replace the rows of this cut, so a re-run does not duplicate."""
        model = DATASET_MODELS[dataset]
        fecha_corte = df["fecha_corte"].iloc[0]

        mapped = self._map_foreign_keys(session, dataset, df)

        session.execute(delete(model).where(model.fecha_corte == fecha_corte))
        session.flush()
        sync_id_sequence(session, model)

        bulk_insert(session, self._records_from_df(mapped, model), model)
        self.logger.info(f"[action] {dataset}: {len(mapped):,} rows loaded for cut {fecha_corte}")

    def _register_load(self, session, manifest: dict[str, Any]) -> None:
        now = datetime.now(timezone.utc)
        records = [
            {
                "envio_id": meta["envio_id"],
                "conjunto": meta["conjunto"],
                "object_key": meta["object_key"],
                "etag": meta.get("etag"),
                "fecha_corte": pd.to_datetime(meta["fecha_corte"]).date(),
                "fecha_actualizacion_fuente": (
                    pd.to_datetime(meta["fecha_actualizacion"]).date() if meta.get("fecha_actualizacion") else None
                ),
                "actualizado_en": pd.to_datetime(meta["actualizado_en"]).to_pydatetime(),
                "procesado_en": now,
            }
            for meta in manifest.values()
        ]

        sync_id_sequence(session, CargasAcervo)
        upsert_records(session, records, CargasAcervo, conflict_keys=["envio_id", "object_key"])

    def action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        if self.mode != "bootstrap":
            raise ValueError("secretaria_educacion v1 only supports bootstrap mode")

        self.db.connect()
        try:
            with self.db.get_session() as session:
                self._load_catalogs(session, input_data["catalogs"])
                for dataset, df in input_data["frames"].items():
                    self._reload_dataset(session, dataset, df)
                self._register_load(session, input_data["manifest"])
        except Exception:
            self.db.disconnect()
            raise

        return input_data

    def finalization(self, input_data: dict[str, Any]) -> dict[str, int]:
        totals = {}
        try:
            with self.db.get_session() as session:
                for dataset, model in DATASET_MODELS.items():
                    if dataset in input_data["frames"]:
                        totals[dataset] = count_records(session, model)
        finally:
            self.db.disconnect()
            cleanup_pipeline_data(PIPELINE_NAME)

        for dataset, total in totals.items():
            self.logger.info(f"[finalization] {dataset}: {total:,} rows in database")

        return totals
