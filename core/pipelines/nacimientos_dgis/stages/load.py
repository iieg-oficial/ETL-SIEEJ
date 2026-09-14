import io
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.db import Database
from core.pipelines.nacimientos_dgis.attributes import NacimientosDgisTables as T
from core.pipelines.nacimientos_dgis.config import settings
from core.pipelines.nacimientos_dgis.constants import (
    AGGREGATE_FILE,
    COLUMN_CATALOG,
    COPY_COLS,
    FACTS_DIR,
    PIPELINE_NAME,
)
from core.pipelines.nacimientos_dgis.queries import (
    COPY_CERTIFICADOS,
    COPY_STG,
    INSERT_NACIMIENTOS_ADOLESCENTES,
    INSERT_TASA_FECUNDIDAD,
    REFRESH_VIEWS,
    TRUNCATE_CERTIFICADOS,
    TRUNCATE_STG,
)
from core.pipelines.nacimientos_dgis.schemas import (
    CODED_MODELS,
    StgNacimientosCertificados,
    StgNacimientosEdadMadre,
)
from core.pipelines.stage import Stage
from core.utils.bulk_ops import bulk_insert_do_nothing, count_records, get_mapping, sync_id_sequence
from core.utils.files import cleanup_pipeline_data
from core.utils.logger import get_logger

CERTIFICADO_COPY_COLS = [
    column for column in StgNacimientosCertificados.columns() if column != StgNacimientosCertificados.id.key
]


class NacimientosDgisLoad(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.logger = get_logger(f"{PIPELINE_NAME}.load")
        self.mode = mode
        self.db = Database(settings.DB_NAME, settings.database_url)
        self.transform_dir = Path(f"data/transform/{PIPELINE_NAME}")

    def source(self, input_data: Optional[Any] = None) -> dict[str, Any]:
        aggregate_path = self.transform_dir / AGGREGATE_FILE
        catalogs_path = self.transform_dir / "catalogos.pkl"

        return {
            "aggregate": pd.read_pickle(aggregate_path) if aggregate_path.exists() else pd.DataFrame(),
            "catalogs": pd.read_pickle(catalogs_path) if catalogs_path.exists() else {},
            "editions": sorted(int(p.stem) for p in (self.transform_dir / FACTS_DIR).glob("*.pkl")),
        }

    # ------------------------------------------------------------------
    # Catálogos
    # ------------------------------------------------------------------
    def _load_catalogs(self, catalogs: dict[str, list[dict]]) -> None:
        with self.db.get_session() as session:
            for table, records in sorted(catalogs.items()):
                if not records:
                    self.logger.warning(f"[action] {table}: sin registros")
                    continue
                model = CODED_MODELS[table]
                bulk_insert_do_nothing(session, records, model, conflict_keys=["clave"])
                sync_id_sequence(session, model)
                self.logger.info(f"[action] {table}: {len(records)} registros")

    def _catalog_maps(self) -> dict[str, dict]:
        """clave -> id por cada catálogo, para resolver las llaves foráneas."""
        with self.db.get_session() as session:
            return {
                table: get_mapping(session, CODED_MODELS[table], "clave", "id") for table in COLUMN_CATALOG.values()
            }

    # ------------------------------------------------------------------
    # Hechos
    # ------------------------------------------------------------------
    @staticmethod
    def _copy_buffer(df: pd.DataFrame, columns: list[str]) -> io.StringIO:
        buffer = io.StringIO()
        df[columns].to_csv(buffer, index=False, header=False)
        buffer.seek(0)
        return buffer

    def _copy(self, statement: str, df: pd.DataFrame, columns: list[str]) -> None:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.copy_expert(statement, self._copy_buffer(df, columns))
            cursor.close()

    def _truncate(self, statement: str) -> None:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(statement)
            cursor.close()

    def _load_aggregate(self, df: pd.DataFrame) -> None:
        if self.mode == "bootstrap":
            self._truncate(TRUNCATE_STG)
        self._copy(COPY_STG, df, COPY_COLS)
        self.logger.info(f"[action] {len(df):,} rows loaded into {T.STG_NACIMIENTOS_EDAD_MADRE}")

    def _resolve_foreign_keys(self, df: pd.DataFrame, maps: dict[str, dict]) -> pd.DataFrame:
        """Cambia la clave SINAC por el `id` del catálogo.

        Una clave que el catálogo de esa edición no publica queda en NULL en vez
        de tumbar la carga: DGIS agrega localidades entre ediciones.
        """
        for column, table in COLUMN_CATALOG.items():
            target = f"{column}_id"
            if column not in df.columns:
                df[target] = pd.NA
                continue

            resolved = df[column].map(maps[table])
            unmatched = int((df[column].notna() & resolved.isna()).sum())
            if unmatched:
                self.logger.warning(f"[action] {column}: {unmatched:,} claves sin match en {table}")

            df[target] = resolved.astype("Int64")
            df = df.drop(columns=[column])

        return df

    def _load_certificates(self, editions: list[int], maps: dict[str, dict]) -> int:
        if self.mode == "bootstrap":
            self._truncate(TRUNCATE_CERTIFICADOS)

        total = 0
        for year in editions:
            frame = pd.read_pickle(self.transform_dir / FACTS_DIR / f"{year}.pkl")
            frame = self._resolve_foreign_keys(frame, maps)
            # `pd.NA` de las columnas nullable no lo convierte `replace`.
            frame = frame.astype(object).where(frame.notna(), None)

            self._copy(COPY_CERTIFICADOS, frame, CERTIFICADO_COPY_COLS)
            total += len(frame)
            self.logger.info(f"[action] {year}: {len(frame):,} certificados cargados")

        return total

    # ------------------------------------------------------------------
    # Derivados
    # ------------------------------------------------------------------
    def _load_calculated_tables(self) -> None:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(INSERT_TASA_FECUNDIDAD)
            self.logger.info("[action] stg_tasa_fecundidad populated")
            cursor.execute(INSERT_NACIMIENTOS_ADOLESCENTES)
            self.logger.info("[action] stg_nacimientos_adolescentes populated")
            cursor.close()

    def _refresh_views(self) -> None:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(REFRESH_VIEWS)
            cursor.close()
        self.logger.info("[action] materialized views refreshed")

    # ------------------------------------------------------------------
    # Stage
    # ------------------------------------------------------------------
    def action(self, input_data: dict[str, Any]) -> dict[str, Any] | None:
        aggregate = input_data["aggregate"]
        if aggregate.empty and not input_data["editions"]:
            self.logger.info("[action] No data to load")
            return None

        try:
            self.db.connect()
            self._load_catalogs(input_data["catalogs"])
            maps = self._catalog_maps()

            if not aggregate.empty:
                self._load_aggregate(aggregate)

            certificates = self._load_certificates(input_data["editions"], maps)

            self._load_calculated_tables()
            self._refresh_views()
        except Exception:
            self.db.disconnect()
            raise

        return {"rows_loaded": len(aggregate), "certificates_loaded": certificates}

    def finalization(self, input_data: Any) -> Any:
        cleanup_pipeline_data(PIPELINE_NAME)
        if input_data is None:
            return None
        try:
            with self.db.get_session() as session:
                for model in (StgNacimientosEdadMadre, StgNacimientosCertificados):
                    self.logger.info(f"[finalization] {count_records(session, model):,} rows in {model.__tablename__}")
        finally:
            self.db.disconnect()
        return input_data
