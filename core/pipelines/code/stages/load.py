from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from sqlalchemy import delete

from core.db import Database
from core.pipelines.code.config import settings
from core.pipelines.code.constants import CATALOGS_FILENAME, MANIFEST_FILENAME, PIPELINE_NAME, PUNTOS_FRAME
from core.pipelines.code.schemas import CargasAcervo, CatActividades, CatRegiones, StgPuntosActivacionReto
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


class CodeLoad(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode
        self.logger = get_logger(f"{PIPELINE_NAME}.load")
        self.db = Database(PIPELINE_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> dict[str, Any]:
        """Read what transform left on disk, so this stage can rerun on its own."""
        transform_dir = Path("data/transform") / PIPELINE_NAME
        manifest = read_json(Path("data/extract") / PIPELINE_NAME / MANIFEST_FILENAME) or {}

        pickle_path = transform_dir / f"{PUNTOS_FRAME}.pkl"
        if manifest and pickle_path.exists():
            catalogs_path = transform_dir / CATALOGS_FILENAME
            if not catalogs_path.exists():
                raise FileNotFoundError(f"No catalogs in {catalogs_path}. Run transform first.")

            self.logger.info("[source] Loaded the transformed data from disk")
            return {
                "frames": {PUNTOS_FRAME: pd.read_pickle(pickle_path)},
                "manifest": manifest,
                "catalogs": pd.read_pickle(catalogs_path),
            }

        if input_data:
            return input_data

        if manifest:
            raise FileNotFoundError(f"No transformed data in {transform_dir}. Run transform first.")

        self.logger.info("[source] No data to load")
        return {"frames": {}, "manifest": {}, "catalogs": {}}

    def _load_catalogs(self, session, catalogs: dict[str, list[dict[str, Any]]]) -> None:
        # Activities carry the source id, so they update: DO NOTHING would keep
        # a label that the dependency later corrected.
        if catalogs.get("actividades"):
            upsert_records(session, catalogs["actividades"], CatActividades, conflict_keys=["id"])

        if catalogs.get("regiones"):
            sync_id_sequence(session, CatRegiones)
            insert_records(session, catalogs["regiones"], CatRegiones, conflict_keys=["region"])

    def _map_foreign_keys(self, session, df: pd.DataFrame) -> pd.DataFrame:
        mapped = df.copy()
        regiones = get_mapping(session, CatRegiones, "region", "id")
        mapped["region_id"] = mapped["region"].map(regiones)
        return mapped

    def _records_from_df(self, df: pd.DataFrame, model) -> list[dict[str, Any]]:
        columns = [column for column in model.columns() if column != model.id.key]
        clean_df = df.astype(object).where(pd.notna(df), None)
        return df_to_records(clean_df, columns)

    def _reload_puntos(self, session, df: pd.DataFrame) -> None:
        """Replace the rows of the cuts in the file, so a re-run does not duplicate."""
        model = StgPuntosActivacionReto
        cuts = sorted(df["fecha_corte"].unique())

        mapped = self._map_foreign_keys(session, df)

        session.execute(delete(model).where(model.fecha_corte.in_(cuts)))
        session.flush()
        sync_id_sequence(session, model)

        bulk_insert(session, self._records_from_df(mapped, model), model)
        self.logger.info(f"[action] {len(mapped):,} rows loaded for cut(s) {cuts}")

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

    def action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        if not input_data["frames"]:
            self.logger.info("[action] Nothing to load")
            return input_data

        puntos = input_data["frames"][PUNTOS_FRAME]

        self.db.connect()
        try:
            with self.db.get_session() as session:
                self._load_catalogs(session, input_data["catalogs"])
                self._reload_puntos(session, puntos)
                self._register_load(session, input_data["manifest"], puntos)
        except Exception:
            self.db.disconnect()
            raise

        return input_data

    def finalization(self, input_data: dict[str, Any]) -> dict[str, int]:
        if not input_data["frames"]:
            cleanup_pipeline_data(PIPELINE_NAME)
            return {}

        try:
            with self.db.get_session() as session:
                total = count_records(session, StgPuntosActivacionReto)
        finally:
            self.db.disconnect()
            cleanup_pipeline_data(PIPELINE_NAME)

        self.logger.info(f"[finalization] {total:,} rows in database")
        return {PUNTOS_FRAME: total}
