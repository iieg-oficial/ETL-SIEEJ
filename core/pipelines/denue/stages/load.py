import io
import pandas as pd
from csv import QUOTE_NONE
from pathlib import Path
from typing import Any, Optional

from core.db import Database
from core.pipelines.stage import Stage
from core.pipelines.denue.attributes import DenueTables as T
from core.pipelines.denue.config import settings
from core.pipelines.denue.mappings import RANGOS_PERSONAL, TIPOS_ESTABLECIMIENTOS
from core.pipelines.denue.constants import INT_COLS, RAW_COLS
from core.pipelines.denue.queries import INSERT_FROM_RAW, TMP_TABLE_DDL
from core.pipelines.denue.schemas import (
    CatActualizaciones,
    CatClasesActividad,
    CatLocalidades,
    CatRamas,
    CatRangosPersonal,
    CatSectores,
    CatSubramas,
    CatSubsectores,
    CatTiposEstablecimientos,
    StgEstablecimientos,
)
from core.utils.bulk_ops import count_records, insert_records, sync_id_sequence
from core.utils.logger import get_logger

PIPELINE_NAME = settings.PIPELINE_NAME


class DenueLoad(Stage):
    def __init__(self, mode: str = "bootstrap", entidad: int = None):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode
        self.entidad = entidad
        self.logger = get_logger(f"{PIPELINE_NAME}.load")
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> Any:
        pkl_df = Path(f"data/transform/{PIPELINE_NAME}/denue_df_{self.entidad}.pkl")
        pkl_catalogs = Path(f"data/transform/{PIPELINE_NAME}/denue_catalogs_{self.entidad}.pkl")
        self.logger.info("[source] Checking for pkl files")
        if pkl_df.exists() and pkl_catalogs.exists():
            self.logger.info("[source] Loading from pkl files")
            df = pd.read_pickle(pkl_df)
            catalogs = pd.read_pickle(pkl_catalogs).to_dict()
            return {"df": df, "catalogs": catalogs}
        self.logger.info("[source] pkl not found, using transform output")
        return input_data

    def _load_catalogs(self, session, catalogs: dict) -> None:
        insert_records(session, RANGOS_PERSONAL, CatRangosPersonal, conflict_keys=[CatRangosPersonal.id.key])
        insert_records(
            session, TIPOS_ESTABLECIMIENTOS, CatTiposEstablecimientos, conflict_keys=[CatTiposEstablecimientos.id.key]
        )

        self.logger.info(f"[_load_catalogs] Loading {len(catalogs[T.CAT_ACTUALIZACIONES])} actualizaciones")
        insert_records(
            session,
            catalogs[T.CAT_ACTUALIZACIONES],
            CatActualizaciones,
            conflict_keys=[CatActualizaciones.fecha_actualizacion.key],
        )

        self.logger.info(f"[_load_catalogs] Loading {len(catalogs[T.CAT_LOCALIDADES])} localidades")
        insert_records(
            session, catalogs[T.CAT_LOCALIDADES], CatLocalidades, conflict_keys=[CatLocalidades.cve_geo_id.key]
        )

        scian_catalogs = [
            (T.CAT_SECTORES, CatSectores, CatSectores.codigo.key),
            (T.CAT_SUBSECTORES, CatSubsectores, CatSubsectores.codigo.key),
            (T.CAT_RAMAS, CatRamas, CatRamas.codigo.key),
            (T.CAT_SUBRAMAS, CatSubramas, CatSubramas.codigo.key),
            (T.CAT_CLASES_ACTIVIDAD, CatClasesActividad, CatClasesActividad.codigo.key),
        ]
        for table_key, model, conflict_key in scian_catalogs:
            records = catalogs.get(table_key, [])
            self.logger.info(f"[_load_catalogs] Loading {len(records)} {table_key}")
            insert_records(session, records, model, conflict_keys=[conflict_key])

        for model in [
            CatActualizaciones,
            CatLocalidades,
            CatSectores,
            CatSubsectores,
            CatRamas,
            CatSubramas,
            CatClasesActividad,
        ]:
            sync_id_sequence(session, model)

    def _prepare_copy_buffer(self, df: pd.DataFrame) -> io.StringIO:
        subset = df[RAW_COLS].copy()

        for col in INT_COLS:
            subset[col] = pd.to_numeric(subset[col], errors="coerce").astype("Int64").astype(str).replace("<NA>", "\\N")

        subset["codigo_actividad"] = (
            pd.to_numeric(subset["codigo_actividad"], errors="coerce")
            .astype("Int64")
            .astype(str)
            .replace("<NA>", "\\N")
        )

        text_cols = [c for c in RAW_COLS if c not in INT_COLS and c != "codigo_actividad"]
        for col in text_cols:
            subset[col] = subset[col].astype(str).replace("nan", "\\N").str.replace("\\", "\\\\", regex=False)

        buffer = io.StringIO()
        subset.to_csv(buffer, sep="\t", header=False, index=False, quoting=QUOTE_NONE, na_rep="\\N")
        buffer.seek(0)
        return buffer

    def action(self, input_data: Any) -> Any:
        df = input_data["df"]
        if df.empty:
            self.logger.info("[action] Empty DataFrame, skipping load")
            return None

        catalogs = input_data["catalogs"]
        self.logger.info(f"[action] Loading {len(df):,} rows")

        try:
            self.db.connect()
            with self.db.get_session() as session:
                records_before = count_records(session, StgEstablecimientos)
                self._load_catalogs(session, catalogs)

            buffer = self._prepare_copy_buffer(df)
            cols_str = ", ".join(RAW_COLS)

            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(TMP_TABLE_DDL)

                self.logger.info(f"[action] COPY {len(df):,} rows to tmp_raw")
                cursor.copy_expert(f"COPY tmp_raw ({cols_str}) FROM STDIN WITH (FORMAT text, NULL '\\N')", buffer)

                self.logger.info(f"[action] INSERT INTO {T.STG_ESTABLECIMIENTOS} from tmp_raw")
                cursor.execute(INSERT_FROM_RAW)
                cursor.close()
        except Exception:
            self.db.disconnect()
            raise

        return {"data": input_data, "records_before": records_before}

    def finalization(self, input_data: Any) -> Any:
        if input_data is None:
            return None
        try:
            with self.db.get_session() as session:
                total = count_records(session, StgEstablecimientos)
                inserted = total - input_data["records_before"]
            self.logger.info(f"[finalization] {format(total, ',')} establecimientos in database")
            self.logger.info(f"[finalization] {format(inserted, ',')} establecimientos inserted/updated")
        finally:
            self.db.disconnect()
        return input_data["data"]
