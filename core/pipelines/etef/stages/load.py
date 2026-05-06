import pandas as pd

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import update

from core.db import Database
from core.pipelines.etef.config import settings
from core.pipelines.etef.consts import CATALOG_COLUMNS, PIPELINE_NAME
from core.pipelines.etef.schemas import CATALOG_MODELS, EtefBase, EtefDatos
from core.pipelines.stage import Stage
from core.utils.bulk_ops import bulk_insert, get_mapping, insert_records, sync_id_sequence
from core.utils.files import clean_directory


class EtefLoader(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode
        self.db: Optional[Database] = None
        self._catalog_caches: dict[str, dict[str, int]] = {}

    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data:
            raise ValueError("Load no recibió datos de Transform")

        self.db = Database(PIPELINE_NAME, settings.database_url)
        self.db.connect()

        EtefBase.metadata.create_all(self.db.engine)
        self.logger.info("Tablas verificadas/creadas")

        return input_data

    def action(self, input_data: Optional[Any] = None) -> dict:
        df: pd.DataFrame = input_data["df"]
        catalog_values: dict[str, list[str]] = input_data["catalogs"]

        with self.db.get_session() as session:
            self._load_catalogs(session, catalog_values)

        df = self._resolve_catalog_ids(df)

        now = datetime.now(timezone.utc)
        records_inserted = 0
        records_closed = 0

        if self.mode == "bootstrap":
            records_inserted = self._load_bootstrap(df, now)
        else:
            records_inserted, records_closed = self._load_update(df, now)

        with self.db.get_session() as session:
            sync_id_sequence(session, EtefDatos)
            for model in CATALOG_MODELS.values():
                sync_id_sequence(session, model)

        return {
            "mode": self.mode,
            "records_inserted": records_inserted,
            "records_closed": records_closed,
            "catalogs_synced": len(catalog_values),
        }

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        clean_directory(self.work_dir, self.logger)
        if self.db:
            self.db.disconnect()
        self.logger.info(f"Etapa Load completa. Estadísticas: {input_data}")
        return input_data

    def _build_record(self, row: dict, now: datetime) -> dict:
        """Build an EtefDatos insert dict from a DataFrame row dict."""
        return {
            "anio": int(row["anio"]) if row["anio"] is not None else None,
            "trimestre": row["trimestre"],
            "mes": row["mes"],
            "prod_est": row.get("prod_est"),
            "cobertura": row.get("cobertura"),
            "cve_ent": int(row["cve_ent"]) if row["cve_ent"] is not None else None,
            "codigo_scian_id": row.get("codigo_scian_id"),
            "val_usd": float(row["val_usd"]) if row["val_usd"] is not None else None,
            "estatus_cifra": row.get("estatus_cifra"),
            "estatus": row.get("estatus"),
            "row_hash": row["row_hash"],
            "is_current": True,
            "valid_from": now,
            "valid_to": None,
        }

    def _load_bootstrap(self, df: pd.DataFrame, now: datetime) -> int:
        """Insert all records as the initial full load with is_current=True."""
        records = [self._build_record(row, now) for row in df.to_dict(orient="records")]
        with self.db.get_session() as session:
            bulk_insert(session, records, EtefDatos, chunk_size=settings.ETEF_LOAD_BATCH_SIZE)
        self.logger.info(f"Bootstrap: {len(records)} registros insertados")
        return len(records)

    def _load_update(self, df: pd.DataFrame, now: datetime) -> tuple[int, int]:
        """SCD2 update: close changed rows, insert new versions, skip unchanged."""
        # Fetch all active records in one query (id + natural key + hash)
        with self.db.get_session() as session:
            active_rows = (
                session.query(
                    EtefDatos.id,
                    EtefDatos.anio,
                    EtefDatos.trimestre,
                    EtefDatos.cve_ent,
                    EtefDatos.codigo_scian_id,
                    EtefDatos.row_hash,
                )
                .filter(EtefDatos.is_current == True)  # noqa: E712
                .all()
            )

        # Build lookup: (anio, trimestre, cve_ent, codigo_scian_id) → (id, row_hash)
        active_index: dict[tuple, tuple[int, str]] = {
            (r.anio, r.trimestre, r.cve_ent, r.codigo_scian_id): (r.id, r.row_hash) for r in active_rows
        }
        self.logger.info(f"Registros activos en BD: {len(active_index)}")

        ids_to_close: list[int] = []
        records_to_insert: list[dict] = []

        for row in df.to_dict(orient="records"):
            key = (
                int(row["anio"]) if row["anio"] is not None else None,
                row["trimestre"],
                int(row["cve_ent"]) if row["cve_ent"] is not None else None,
                row.get("codigo_scian_id"),
            )
            incoming_hash: str = row["row_hash"]

            if key not in active_index:
                records_to_insert.append(self._build_record(row, now))
            else:
                db_id, db_hash = active_index[key]
                if incoming_hash != db_hash:
                    # Close current version and insert new one
                    ids_to_close.append(db_id)
                    records_to_insert.append(self._build_record(row, now))
                # else: identical hash — skip, no change

        self.logger.info(
            f"Update: {len(ids_to_close)} registros a cerrar, {len(records_to_insert)} registros a insertar"
        )

        with self.db.get_session() as session:
            if ids_to_close:
                session.execute(
                    update(EtefDatos).where(EtefDatos.id.in_(ids_to_close)).values(valid_to=now, is_current=False)
                )
            if records_to_insert:
                bulk_insert(
                    session,
                    records_to_insert,
                    EtefDatos,
                    chunk_size=settings.ETEF_LOAD_BATCH_SIZE,
                )

        return len(records_to_insert), len(ids_to_close)

    def _load_catalogs(self, session, catalog_values: dict[str, list[str]]) -> None:
        for cat_key, values in catalog_values.items():
            model = CATALOG_MODELS[cat_key]
            records = [{"codigo": v, "descripcion": None} for v in values]
            insert_records(session, records, model, conflict_keys=["codigo"])
            self.logger.info(f"Catálogo '{cat_key}': {len(records)} valores sincronizados")

        session.flush()

        for cat_key, model in CATALOG_MODELS.items():
            self._catalog_caches[cat_key] = get_mapping(session, model, "codigo", "id")

    def _resolve_catalog_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in CATALOG_COLUMNS:
            if col in df.columns and col in self._catalog_caches:
                cache = self._catalog_caches[col]
                df[f"{col}_id"] = df[col].apply(lambda v: cache.get(str(v)) if v is not None else None)
                self.logger.info(f"Resueltos IDs para columna '{col}'")
        return df
