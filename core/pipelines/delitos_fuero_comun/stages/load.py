from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.db import Database
from core.pipelines.delitos_fuero_comun.config import PIPELINE_NAME, settings
from core.pipelines.delitos_fuero_comun.constants import NK_COLS, UPDATE_COLS
from core.pipelines.delitos_fuero_comun.schemas import (
    CatBienJuridicoAfectado,
    CatModalidad,
    CatMunicipio,
    CatSubtipoDelito,
    CatTipoDelito,
    DelitosFueroComunBase,
    StgDelitosFueroComun2026,
    StgDelitosFueroComunHistorico,
)
from core.pipelines.stage import Stage
from core.utils.bulk_ops import bulk_insert, get_mapping, insert_records, sync_id_sequence, upsert_records
from core.utils.files import clean_directory


def _prepare_records(df: pd.DataFrame, model, exclude_cols: tuple[str, ...]) -> list[dict]:
    cols = [c.key for c in model.__table__.columns if c.key not in exclude_cols]
    available = [c for c in cols if c in df.columns]
    # Convert to object dtype to ensure pd.NA / NaN becomes Python None
    clean = df[available].astype(object).where(pd.notna(df[available]), other=None)
    return clean.to_dict("records")


class DelitosLoad(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode
        self.db: Optional[Database] = None

    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data:
            raise ValueError("Load no recibió datos de Transform")
        self.db = Database(PIPELINE_NAME, settings.database_url)
        self.db.connect()
        DelitosFueroComunBase.metadata.create_all(self.db.engine)
        return input_data

    def action(self, input_data: Optional[Any] = None) -> dict:
        df_historico: Optional[pd.DataFrame] = input_data.get("df_historico")
        df_2026: pd.DataFrame = input_data["df_2026"]
        catalogs: dict = input_data["catalogs"]

        with self.db.get_session() as session:
            # 1. Load catalogs (always, to register new entries on update)
            insert_records(
                session,
                catalogs["bien_juridico_afectado"],
                CatBienJuridicoAfectado,
                conflict_keys=["bien_juridico_afectado"],
            )
            sync_id_sequence(session, CatBienJuridicoAfectado)

            insert_records(
                session,
                catalogs["tipo_delito"],
                CatTipoDelito,
                conflict_keys=["tipo_delito"],
            )
            sync_id_sequence(session, CatTipoDelito)

            tipo_map: dict[str, int] = get_mapping(session, CatTipoDelito, "tipo_delito", "id")
            subtipo_records = [
                {"subtipo_delito": r["subtipo_delito"], "tipo_delito_id": tipo_map[r["tipo_delito"]]}
                for r in catalogs["subtipo_delito"]
            ]
            insert_records(session, subtipo_records, CatSubtipoDelito, conflict_keys=["subtipo_delito"])
            sync_id_sequence(session, CatSubtipoDelito)

            subtipo_map: dict[str, int] = get_mapping(session, CatSubtipoDelito, "subtipo_delito", "id")
            modalidad_records = [
                {"modalidad": r["modalidad"], "subtipo_delito_id": subtipo_map.get(r["subtipo_delito"])}
                for r in catalogs["modalidad"]
            ]
            insert_records(session, modalidad_records, CatModalidad, conflict_keys=["modalidad"])
            sync_id_sequence(session, CatModalidad)

            insert_records(
                session,
                catalogs["municipio"],
                CatMunicipio,
                conflict_keys=["cve_municipio"],
            )
            sync_id_sequence(session, CatMunicipio)

            # 2. Build full ID maps
            bja_map: dict[str, int] = get_mapping(session, CatBienJuridicoAfectado, "bien_juridico_afectado", "id")
            tipo_map_full: dict[str, int] = get_mapping(session, CatTipoDelito, "tipo_delito", "id")
            subtipo_map_full: dict[str, int] = get_mapping(session, CatSubtipoDelito, "subtipo_delito", "id")
            modalidad_map_full: dict[str, int] = get_mapping(session, CatModalidad, "modalidad", "id")

            # 3. Load historical staging (bootstrap only)
            rows_hist = 0
            if df_historico is not None:
                df_hist = self._resolve_ids(df_historico, bja_map, tipo_map_full, subtipo_map_full, modalidad_map_full)
                records_hist = _prepare_records(df_hist, StgDelitosFueroComunHistorico, ("id", "created_at"))
                bulk_insert(session, records_hist, StgDelitosFueroComunHistorico, chunk_size=settings.LOAD_BATCH_SIZE)
                sync_id_sequence(session, StgDelitosFueroComunHistorico)
                rows_hist = len(records_hist)
                self.logger.info(f"Histórico cargado: {rows_hist} filas")

            # 4. Load 2026 staging
            df_26 = self._resolve_ids(df_2026, bja_map, tipo_map_full, subtipo_map_full, modalidad_map_full)
            rows_2026 = 0

            if self.mode == "bootstrap":
                records_2026 = _prepare_records(df_26, StgDelitosFueroComun2026, ("id", "created_at", "updated_at"))
                bulk_insert(session, records_2026, StgDelitosFueroComun2026, chunk_size=settings.LOAD_BATCH_SIZE)
            else:
                df_26["updated_at"] = datetime.utcnow()
                records_2026 = _prepare_records(df_26, StgDelitosFueroComun2026, ("id", "created_at"))
                upsert_records(
                    session,
                    records_2026,
                    StgDelitosFueroComun2026,
                    conflict_keys=NK_COLS,
                    update_keys=UPDATE_COLS,
                    chunk_size=settings.LOAD_BATCH_SIZE,
                )

            sync_id_sequence(session, StgDelitosFueroComun2026)
            rows_2026 = len(records_2026)
            self.logger.info(f"2026 cargado: {rows_2026} filas")

        return {"rows_hist": rows_hist, "rows_2026": rows_2026}

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        clean_directory(Path(f"data/transform/{PIPELINE_NAME}"), self.logger)
        if self.db:
            self.db.disconnect()
        return input_data

    def _resolve_ids(
        self,
        df: pd.DataFrame,
        bja_map: dict[str, int],
        tipo_map: dict[str, int],
        subtipo_map: dict[str, int],
        modalidad_map: dict[str, int],
    ) -> pd.DataFrame:
        df = df.copy()
        df["bien_juridico_afectado_id"] = df["bien_juridico_afectado"].map(bja_map)
        df["tipo_delito_id"] = df["tipo_delito"].map(tipo_map)
        df["subtipo_delito_id"] = df["subtipo_delito"].map(subtipo_map)
        df["modalidad_id"] = df["modalidad"].map(modalidad_map)
        df = df.drop(columns=["bien_juridico_afectado", "tipo_delito", "subtipo_delito", "modalidad"])
        return df
