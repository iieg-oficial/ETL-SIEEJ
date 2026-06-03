import io
import pandas as pd
from csv import QUOTE_NONE
from pathlib import Path
from typing import Any, Optional

from core.db import Database
from core.pipelines.stage import Stage
from core.pipelines.denue.attributes import DenueTables as T
from core.pipelines.denue.config import settings
from core.pipelines.denue.constants import ENTIDAD_JALISCO, INT_COLS, RAW_COLS
from core.pipelines.denue.mappings import RANGOS_PERSONAL, TIPOS_ESTABLECIMIENTOS, get_sector_codigo
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
    StgEstEntResumen,
    StgEstJal,
)
from core.utils.bulk_ops import count_records, get_mapping, insert_records, sync_id_sequence, upsert_records
from core.utils.logger import get_logger

PIPELINE_NAME = settings.PIPELINE_NAME


class DenueLoad(Stage):
    def __init__(self, mode: str = "bootstrap", entidad: int = None):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode
        self.entidad = entidad
        self.is_jalisco = entidad == ENTIDAD_JALISCO
        self.logger = get_logger(f"{PIPELINE_NAME}.load")
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> list[dict]:
        transform_dir = Path(f"data/transform/{PIPELINE_NAME}")
        prefix = "denue_df" if self.is_jalisco else "denue_resumen"

        per_period = sorted(transform_dir.glob(f"{prefix}_{self.entidad}_*.pkl"))
        if per_period:
            periods = []
            for df_pkl in per_period:
                date_str = df_pkl.stem.rsplit("_", 1)[-1]
                cat_pkl = transform_dir / f"denue_catalogs_{self.entidad}_{date_str}.pkl"
                if cat_pkl.exists():
                    periods.append({"df_path": df_pkl, "catalogs_path": cat_pkl})
            self.logger.info(f"[source] Found {len(periods)} per-period transform pkls")
            return periods

        self.logger.info("[source] No transform pkls found")
        return []

    def _load_catalogs(self, session, catalogs: dict) -> None:
        if self.is_jalisco:
            insert_records(session, RANGOS_PERSONAL, CatRangosPersonal, conflict_keys=[CatRangosPersonal.id.key])
            insert_records(
                session,
                TIPOS_ESTABLECIMIENTOS,
                CatTiposEstablecimientos,
                conflict_keys=[CatTiposEstablecimientos.id.key],
            )

        insert_records(
            session,
            catalogs[T.CAT_ACTUALIZACIONES],
            CatActualizaciones,
            conflict_keys=[CatActualizaciones.fecha_actualizacion.key],
        )

        if T.CAT_LOCALIDADES in catalogs:
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
            if records:
                insert_records(session, records, model, conflict_keys=[conflict_key])

        models_to_sync = [CatActualizaciones, CatSectores, CatSubsectores, CatRamas, CatSubramas, CatClasesActividad]
        if self.is_jalisco:
            models_to_sync.append(CatLocalidades)
        for model in models_to_sync:
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
            subset[col] = (
                subset[col]
                .astype(str)
                .replace({"nan": "\\N", "NaT": "\\N", "None": "\\N"})
                .str.replace("\\", "\\\\", regex=False)
            )

        buffer = io.StringIO()
        subset.to_csv(buffer, sep="\t", header=False, index=False, quoting=QUOTE_NONE, na_rep="\\N")
        buffer.seek(0)
        return buffer

    def _load_jalisco(self, period: dict, catalogs: dict, df: pd.DataFrame) -> None:
        with self.db.get_session() as session:
            self._load_catalogs(session, catalogs)

        dupes = df.duplicated(subset=["id", "fecha_actualizacion"], keep="last")
        if dupes.any():
            self.logger.info(f"[action] Dropping {dupes.sum()} duplicate (id, fecha_actualizacion) rows")
            df = df[~dupes]

        buffer = self._prepare_copy_buffer(df)
        cols_str = ", ".join(RAW_COLS)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(TMP_TABLE_DDL)
            self.logger.info(f"[action] COPY {len(df):,} rows to tmp_raw")
            cursor.copy_expert(f"COPY tmp_raw ({cols_str}) FROM STDIN WITH (FORMAT text, NULL '\\N')", buffer)
            self.logger.info(f"[action] INSERT INTO {T.STG_EST_JAL} from tmp_raw")
            cursor.execute(INSERT_FROM_RAW)
            cursor.close()

    def _map_resumen_fks(self, session, df: pd.DataFrame) -> pd.DataFrame:
        actualizaciones_map = get_mapping(
            session, CatActualizaciones, CatActualizaciones.fecha_actualizacion.key, CatActualizaciones.id.key
        )
        sectores_map = get_mapping(session, CatSectores, CatSectores.codigo.key, CatSectores.id.key)
        subsectores_map = get_mapping(session, CatSubsectores, CatSubsectores.codigo.key, CatSubsectores.id.key)
        ramas_map = get_mapping(session, CatRamas, CatRamas.codigo.key, CatRamas.id.key)
        subramas_map = get_mapping(session, CatSubramas, CatSubramas.codigo.key, CatSubramas.id.key)
        clases_map = get_mapping(session, CatClasesActividad, CatClasesActividad.codigo.key, CatClasesActividad.id.key)

        df = df.copy()
        df["actualizacion_id"] = df["fecha_actualizacion"].map(actualizaciones_map)

        codigo_str = df["codigo_actividad"].apply(lambda x: str(int(x)) if pd.notna(x) else None)
        df["sector_id"] = codigo_str.apply(lambda x: sectores_map.get(get_sector_codigo(x)) if x else None)
        df["subsector_id"] = codigo_str.apply(lambda x: subsectores_map.get(x[:3]) if x and len(x) >= 3 else None)
        df["rama_id"] = codigo_str.apply(lambda x: ramas_map.get(x[:4]) if x and len(x) >= 4 else None)
        df["subrama_id"] = codigo_str.apply(lambda x: subramas_map.get(x[:5]) if x and len(x) >= 5 else None)
        df["clase_actividad_id"] = codigo_str.apply(lambda x: clases_map.get(x) if x else None)

        return df.astype(object).where(df.notna(), None)

    def _load_resumen(self, period: dict, catalogs: dict, df: pd.DataFrame) -> None:
        with self.db.get_session() as session:
            self._load_catalogs(session, catalogs)
            df = self._map_resumen_fks(session, df)

            cols = [c for c in StgEstEntResumen.columns() if c != StgEstEntResumen.id.key]
            records = df[cols].to_dict("records")
            upsert_records(
                session,
                records,
                StgEstEntResumen,
                conflict_keys=[
                    StgEstEntResumen.entidad_id.key,
                    StgEstEntResumen.actualizacion_id.key,
                    StgEstEntResumen.clase_actividad_id.key,
                ],
            )

    def action(self, input_data: list[dict]) -> Any:
        if not input_data:
            self.logger.info("[action] No transform data to load")
            return None

        self.logger.info(f"[action] Loading {len(input_data)} periodos for entidad {self.entidad}")
        target_model = StgEstJal if self.is_jalisco else StgEstEntResumen

        try:
            self.db.connect()
            with self.db.get_session() as session:
                records_before = count_records(session, target_model)

            for period in input_data:
                df = pd.read_pickle(period["df_path"])
                catalogs = pd.read_pickle(period["catalogs_path"]).to_dict()

                if df.empty:
                    continue

                self.logger.info(f"[action] Loading {len(df):,} rows from {period['df_path'].name}")

                if self.is_jalisco:
                    self._load_jalisco(period, catalogs, df)
                else:
                    self._load_resumen(period, catalogs, df)

        except Exception:
            self.db.disconnect()
            raise

        return {"records_before": records_before, "target_model": target_model}

    def finalization(self, input_data: Any) -> Any:
        if input_data is None:
            return None
        try:
            target_model = input_data["target_model"]
            with self.db.get_session() as session:
                total = count_records(session, target_model)
                inserted = total - input_data["records_before"]
            self.logger.info(f"[finalization] {format(total, ',')} rows in {target_model.__tablename__}")
            self.logger.info(f"[finalization] {format(inserted, ',')} rows inserted/updated")
        finally:
            self.db.disconnect()
        return input_data
