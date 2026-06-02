from pathlib import Path
from typing import Any, Optional

import pandas as pd
from sqlalchemy import delete

from core.db import Database
from core.pipelines.escuelas.config import settings
from core.pipelines.escuelas.constants import DIRECTORIO_DATASET, ESTADISTICA_DATASET, PIPELINE_NAME
from core.pipelines.escuelas.schemas import (
    CatCodigosSostenimiento,
    CatMedios,
    CatNiveles,
    CatNivelesPrograma,
    CatProgramas,
    CatRegiones,
    CatSostenimientos,
    CatTurnos,
    StgDirectorioEscuelas,
    StgEstadisticaEscuelas,
)
from core.pipelines.stage import Stage
from core.utils import df_to_records
from core.utils.bulk_ops import bulk_insert, count_records, get_mapping, insert_records, sync_id_sequence
from core.utils.files import cleanup_pipeline_data
from core.utils.logger import get_logger


class EscuelasLoad(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode
        self.logger = get_logger(f"{PIPELINE_NAME}.load")
        self.db = Database(PIPELINE_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> dict[str, Any]:
        transform_dir = Path("data/transform") / PIPELINE_NAME
        directorio_path = transform_dir / f"{DIRECTORIO_DATASET}.pkl"
        estadistica_path = transform_dir / f"{ESTADISTICA_DATASET}.pkl"

        if directorio_path.exists() and estadistica_path.exists() and input_data:
            self.logger.info("[source] Loading transformed pickle files")
            input_data[DIRECTORIO_DATASET] = pd.read_pickle(directorio_path)
            input_data[ESTADISTICA_DATASET] = pd.read_pickle(estadistica_path)

        return input_data

    def _load_catalogs(self, session, catalogs: dict[str, list[dict[str, Any]]]) -> None:
        for model in [CatSostenimientos, CatNiveles, CatProgramas, CatMedios, CatNivelesPrograma]:
            sync_id_sequence(session, model)

        insert_records(session, catalogs["turnos"], CatTurnos, conflict_keys=["id"])
        insert_records(session, catalogs["sostenimientos"], CatSostenimientos, conflict_keys=["sostenimiento"])

        sostenimientos_map = get_mapping(session, CatSostenimientos, "sostenimiento", "id")
        codigos_sostenimiento = [
            {"id": item["id"], "sostenimiento_id": sostenimientos_map[item["sostenimiento"]]}
            for item in catalogs["codigos_sostenimiento"]
        ]

        insert_records(session, codigos_sostenimiento, CatCodigosSostenimiento, conflict_keys=["id"])
        insert_records(session, catalogs["niveles"], CatNiveles, conflict_keys=["nivel"])
        insert_records(session, catalogs["programas"], CatProgramas, conflict_keys=["programa"])
        insert_records(session, catalogs["regiones"], CatRegiones, conflict_keys=["id"])
        insert_records(session, catalogs["medios"], CatMedios, conflict_keys=["medio"])
        insert_records(session, catalogs["niveles_programa"], CatNivelesPrograma, conflict_keys=["nivel_programa"])

    def _map_directorio(self, session, df: pd.DataFrame) -> pd.DataFrame:
        mapped = df.copy()

        niveles_map = get_mapping(session, CatNiveles, "nivel", "id")
        programas_map = get_mapping(session, CatProgramas, "programa", "id")
        medios_map = get_mapping(session, CatMedios, "medio", "id")

        mapped["nivel_id"] = mapped["nivel"].map(niveles_map)
        mapped["programa_id"] = mapped["programa"].map(programas_map)
        mapped["medio_id"] = mapped["medio"].map(medios_map)

        return mapped

    def _map_estadistica(self, session, df: pd.DataFrame) -> pd.DataFrame:
        mapped = df.copy()

        niveles_programa_map = get_mapping(session, CatNivelesPrograma, "nivel_programa", "id")
        sostenimientos_map = get_mapping(session, CatSostenimientos, "sostenimiento", "id")

        mapped["nivel_programa_id"] = mapped["nivel_programa"].map(niveles_programa_map)
        mapped["sostenimiento_id"] = mapped["sostenimiento"].map(sostenimientos_map)

        return mapped

    def _records_from_df(self, df: pd.DataFrame, model) -> list[dict[str, Any]]:
        columns = [column for column in model.columns() if column != model.id.key]
        clean_df = df.astype(object).where(pd.notna(df), None)
        return df_to_records(clean_df, columns)

    def _reload_staging(self, session, input_data: dict[str, Any]) -> dict[str, int]:
        directorio = self._map_directorio(session, input_data[DIRECTORIO_DATASET])
        estadistica = self._map_estadistica(session, input_data[ESTADISTICA_DATASET])

        records_before = {
            DIRECTORIO_DATASET: count_records(session, StgDirectorioEscuelas),
            ESTADISTICA_DATASET: count_records(session, StgEstadisticaEscuelas),
        }

        session.execute(delete(StgDirectorioEscuelas).where(StgDirectorioEscuelas.anio == settings.SOURCE_YEAR))
        session.execute(delete(StgEstadisticaEscuelas).where(StgEstadisticaEscuelas.anio == settings.SOURCE_YEAR))
        session.flush()

        sync_id_sequence(session, StgDirectorioEscuelas)
        sync_id_sequence(session, StgEstadisticaEscuelas)

        bulk_insert(session, self._records_from_df(directorio, StgDirectorioEscuelas), StgDirectorioEscuelas)
        bulk_insert(session, self._records_from_df(estadistica, StgEstadisticaEscuelas), StgEstadisticaEscuelas)

        return records_before

    def action(self, input_data: dict[str, Any]) -> dict[str, int]:
        if self.mode != "bootstrap":
            raise ValueError("Escuelas v1 only supports bootstrap mode")

        self.db.connect()
        try:
            with self.db.get_session() as session:
                self._load_catalogs(session, input_data["catalogs"])
                records_before = self._reload_staging(session, input_data)
        except Exception:
            self.db.disconnect()
            raise

        return records_before

    def finalization(self, input_data: dict[str, int]) -> dict[str, int]:
        try:
            with self.db.get_session() as session:
                directorio_total = count_records(
                    session, StgDirectorioEscuelas, filter_column="anio", filter_value=settings.SOURCE_YEAR
                )
                estadistica_total = count_records(
                    session, StgEstadisticaEscuelas, filter_column="anio", filter_value=settings.SOURCE_YEAR
                )
        finally:
            self.db.disconnect()
            cleanup_pipeline_data(PIPELINE_NAME)

        self.logger.info(
            "[finalization] directorio=%s rows estadistica=%s rows for year %s",
            f"{directorio_total:,}",
            f"{estadistica_total:,}",
            settings.SOURCE_YEAR,
        )
        return input_data
