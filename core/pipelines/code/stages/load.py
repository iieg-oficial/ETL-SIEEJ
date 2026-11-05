from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from sqlalchemy import delete

from core.db import Database
from core.pipelines.code.config import settings
from core.pipelines.code.constants import (
    ACADEMIAS_FRAME,
    CATALOGS_FILENAME,
    MANIFEST_FILENAME,
    MATERIALIZED_VIEWS,
    PIPELINE_NAME,
    POLIDEPORTIVO_DEPORTES_FRAME,
    POLIDEPORTIVOS_FRAME,
    POLIDEPORTIVOS_UNIQUE_KEY,
    PUNTOS_FRAME,
)
from core.pipelines.code.datasets import ACADEMIAS, POLIDEPORTIVOS, RETO
from core.pipelines.code.helpers.common import catalog_conflicts
from core.pipelines.code.schemas import (
    CargasAcervo,
    CatActividades,
    CatDeportes,
    CatRegiones,
    CatTiposAcademia,
    PolideportivoDeportes,
    StgAcademiasDeportivas,
    StgPolideportivos,
    StgPuntosActivacionReto,
)
from core.pipelines.stage import Stage
from core.utils import df_to_records, map_multiindex
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
from core.utils.views import refresh_materialized_views

# Main table of each dataset: what finalization counts and register reads.
MAIN_FRAMES = {RETO: PUNTOS_FRAME, ACADEMIAS: ACADEMIAS_FRAME, POLIDEPORTIVOS: POLIDEPORTIVOS_FRAME}
MAIN_MODELS = {
    PUNTOS_FRAME: StgPuntosActivacionReto,
    ACADEMIAS_FRAME: StgAcademiasDeportivas,
    POLIDEPORTIVOS_FRAME: StgPolideportivos,
}


class CodeLoad(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode
        self.logger = get_logger(f"{PIPELINE_NAME}.load")
        self.db = Database(PIPELINE_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> dict[str, dict[str, Any]]:
        """Read what transform left on disk, so this stage can rerun on its own."""
        transform_dir = Path("data/transform") / PIPELINE_NAME
        manifest = read_json(Path("data/extract") / PIPELINE_NAME / MANIFEST_FILENAME) or {}

        loaded = {}
        for key, entry in manifest.items():
            folder = transform_dir / key
            frames = {
                path.stem: pd.read_pickle(path)
                for path in sorted(folder.glob("*.pkl"))
                if path.name != CATALOGS_FILENAME
            }
            if not frames:
                continue
            catalogs_path = folder / CATALOGS_FILENAME
            if not catalogs_path.exists():
                raise FileNotFoundError(f"No catalogs in {catalogs_path}. Run transform first.")
            loaded[key] = {"frames": frames, "manifest": entry, "catalogs": pd.read_pickle(catalogs_path)}

        if loaded:
            self.logger.info(f"[source] Loaded {sorted(loaded)} from disk")
            return loaded

        if input_data:
            return input_data

        if manifest:
            raise FileNotFoundError(f"No transformed data in {transform_dir}. Run transform first.")

        self.logger.info("[source] No data to load")
        return {}

    def _load_catalogs(self, session, catalogs: dict[str, list[dict[str, Any]]]) -> None:
        # Activities carry the source id, so they update: DO NOTHING would keep
        # a label that the dependency later corrected.
        if catalogs.get("actividades"):
            upsert_records(session, catalogs["actividades"], CatActividades, conflict_keys=["id"])

        if catalogs.get("regiones"):
            sync_id_sequence(session, CatRegiones)
            insert_records(session, catalogs["regiones"], CatRegiones, conflict_keys=["region"])

    def _load_deportes(self, session, catalogs: dict[str, list[dict[str, Any]]]) -> None:
        """Shared by Academias and Polideportivos; the id is the dependency's.

        A pair that would relabel a stored sport is rejected: the dependency
        renumbering its catalog must not silently rewrite published data.
        """
        deportes = catalogs.get("deportes")
        if not deportes:
            return

        stored = get_mapping(session, CatDeportes, "id", "deporte")
        conflicts = catalog_conflicts(deportes, stored)
        if conflicts:
            raise ValueError(f"cat_deportes would be relabeled, not loaded: {conflicts}")

        upsert_records(session, deportes, CatDeportes, conflict_keys=["id"])

    def _map_foreign_keys(self, session, df: pd.DataFrame) -> pd.DataFrame:
        mapped = df.copy()
        regiones = get_mapping(session, CatRegiones, "region", "id")
        mapped["region_id"] = mapped["region"].map(regiones)
        return mapped

    def _records_from_df(self, df: pd.DataFrame, model) -> list[dict[str, Any]]:
        columns = [column for column in model.columns() if column != "id"]
        clean_df = df.astype(object).where(pd.notna(df), None)
        return df_to_records(clean_df, columns)

    def _replace_table(self, session, df: pd.DataFrame, model) -> None:
        """Replace every row: each submission is the full dataset, so no old cut survives.

        Runs in the caller's session, so a failed insert rolls the delete back.
        """
        session.execute(delete(model))
        session.flush()
        sync_id_sequence(session, model)

        bulk_insert(session, self._records_from_df(df, model), model)
        cuts = sorted(df["fecha_corte"].unique())
        self.logger.info(f"[action] {model.__tablename__} replaced with {len(df):,} rows for cut(s) {cuts}")

    def _reload_academias(self, session, df: pd.DataFrame) -> None:
        tipos = get_mapping(session, CatTiposAcademia, "tipo", "id")
        mapped = df.assign(tipo_id=df["tipo"].map(tipos))

        unmapped = sorted(mapped.loc[mapped["tipo_id"].isna(), "tipo"].unique())
        if unmapped:
            raise ValueError(f"tipo values missing from cat_tipos_academia: {unmapped}")

        self._replace_table(session, mapped, StgAcademiasDeportivas)

    def _polideportivo_ids(self, session, cuts: list) -> dict[tuple, int]:
        """Natural key to id of the rows just inserted for these cuts."""
        model = StgPolideportivos
        rows = session.query(model.id, *(getattr(model, column) for column in POLIDEPORTIVOS_UNIQUE_KEY)).filter(
            model.fecha_corte.in_(cuts)
        )
        return {tuple(row[1:]): row[0] for row in rows}

    def _reload_polideportivos(self, session, df: pd.DataFrame, bridge: pd.DataFrame) -> None:
        """The bridge goes with its polideportivo: deleting the rows cascades to it."""
        self._replace_table(session, df, StgPolideportivos)
        if bridge.empty:
            return

        cuts = sorted(df["fecha_corte"].unique())
        ids = self._polideportivo_ids(session, cuts)
        keyed = bridge.assign(
            polideportivo_id=map_multiindex(ids, [bridge[column] for column in POLIDEPORTIVOS_UNIQUE_KEY])
        )
        bulk_insert(session, self._records_from_df(keyed, PolideportivoDeportes), PolideportivoDeportes)

    def _register_load(self, session, manifest: dict[str, Any], df: pd.DataFrame) -> None:
        record = {
            "envio_id": manifest["envio_id"],
            "conjunto": manifest["conjunto"],
            "object_key": manifest["object_key"],
            "etag": manifest.get("etag"),
            "fecha_corte": df["fecha_corte"].max(),
            "fecha_actualizacion_fuente": df["fecha_actualizacion_fuente"].iloc[0],
            "actualizado_en": pd.to_datetime(manifest["actualizado_en"]).to_pydatetime(),
            "procesado_en": datetime.now(timezone.utc),
        }

        sync_id_sequence(session, CargasAcervo)
        upsert_records(session, [record], CargasAcervo, conflict_keys=["envio_id", "object_key"])

    def _load_dataset(self, session, key: str, entry: dict[str, Any]) -> None:
        frames, catalogs = entry["frames"], entry["catalogs"]
        main = frames[MAIN_FRAMES[key]]

        if key == RETO:
            self._load_catalogs(session, catalogs)
            self._replace_table(session, self._map_foreign_keys(session, main), StgPuntosActivacionReto)
        elif key == ACADEMIAS:
            self._load_deportes(session, catalogs)
            sync_id_sequence(session, CatTiposAcademia)
            insert_records(session, catalogs["tipos"], CatTiposAcademia, conflict_keys=["tipo"])
            self._reload_academias(session, main)
        else:
            self._load_deportes(session, catalogs)
            self._reload_polideportivos(session, main, frames[POLIDEPORTIVO_DEPORTES_FRAME])

        self._register_load(session, entry["manifest"], main)

    def _deporte_conflicts(self, input_data: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
        """Datasets whose sport catalog contradicts another dataset's in this run."""
        pairs = {
            key: {item["id"]: item["deporte"] for item in entry["catalogs"].get("deportes", [])}
            for key, entry in input_data.items()
        }
        found = {}
        for key, entry in input_data.items():
            others = {id_: name for other, items in pairs.items() if other != key for id_, name in items.items()}
            conflicts = catalog_conflicts(entry["catalogs"].get("deportes", []), others)
            if conflicts:
                found[key] = conflicts
        return found

    def action(self, input_data: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        if not input_data:
            self.logger.info("[action] Nothing to load")
            return input_data

        conflicts = self._deporte_conflicts(input_data)
        errors: list[Exception] = [
            ValueError(f"{key}: sport catalog conflicts with another dataset in this run: {found}")
            for key, found in conflicts.items()
        ]
        failed = list(conflicts)
        loaded = []

        self.db.connect()
        try:
            for key, entry in input_data.items():
                if key in conflicts:
                    continue
                # One session per dataset: a bad file must not roll back the others.
                try:
                    with self.db.get_session() as session:
                        self._load_dataset(session, key, entry)
                    loaded.append(key)
                except Exception as error:
                    self.logger.error(f"[action] {key} failed: {error}")
                    errors.append(error)
                    failed.append(key)

            if RETO in loaded:
                try:
                    refresh_materialized_views(self.db, MATERIALIZED_VIEWS)
                    self.logger.info("[action] materialized views refreshed")
                except Exception as error:
                    self.logger.error(f"[action] refresh failed: {error}")
                    errors.append(error)
        except BaseException:
            self.db.disconnect()
            raise

        if errors:
            self.db.disconnect()
            raise ExceptionGroup(f"load failed for {failed}; loaded: {loaded}", errors)

        return input_data

    def finalization(self, input_data: dict[str, dict[str, Any]]) -> dict[str, int]:
        if not input_data:
            cleanup_pipeline_data(PIPELINE_NAME)
            return {}

        totals = {}
        try:
            with self.db.get_session() as session:
                for key in input_data:
                    frame = MAIN_FRAMES[key]
                    totals[frame] = count_records(session, MAIN_MODELS[frame])
        finally:
            self.db.disconnect()
            cleanup_pipeline_data(PIPELINE_NAME)

        for frame, total in totals.items():
            self.logger.info(f"[finalization] {total:,} rows in {frame}")
        return totals
