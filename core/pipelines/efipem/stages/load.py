import pandas as pd

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import update

from core.db import Database
from core.pipelines.efipem.config import settings
from core.pipelines.efipem.consts import (
    CATALOG_COLUMNS,
    PIPELINE_NAME,
)
from core.pipelines.efipem.schemas import (
    CATALOG_MODELS,
    CatConcepto,
    EfipemBase,
    FinanzasTrimestral,
)
from core.pipelines.stage import Stage
from core.utils.bulk_ops import (
    bulk_insert,
    get_mapping,
    insert_records,
    sync_id_sequence,
)
from core.utils.files import clean_directory


class EfipemLoader(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode
        self.db: Database | None = None
        self._catalog_caches: dict[str, dict[str, int]] = {}
        self._concepto_cache: dict[tuple[int, str], int] = {}

    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data:
            raise ValueError("Load no recibio datos de Transform.")

        self.db = Database(PIPELINE_NAME, settings.database_url)
        self.db.connect()

        EfipemBase.metadata.create_all(self.db.engine)
        self.logger.info("Tablas verificadas/creadas.")

        return input_data

    def action(self, input_data: Optional[Any] = None) -> dict:
        df: pd.DataFrame = input_data["df"]
        catalog_values: dict[str, list[str]] = input_data["catalogs"]
        concepto_pairs: list[tuple[str, str]] = input_data["concepto_pairs"]

        with self.db.get_session() as session:
            self._load_catalogs(session, catalog_values)
            self._load_conceptos(session, concepto_pairs)

        df = self._resolve_ids(df)

        now = datetime.now(timezone.utc)
        records_inserted = 0
        records_closed = 0

        if self.mode == "bootstrap":
            records_inserted = self._load_bootstrap(df, now)
        else:
            records_inserted, records_closed = self._load_update(df, now)

        with self.db.get_session() as session:
            sync_id_sequence(session, FinanzasTrimestral)
            for model in CATALOG_MODELS.values():
                sync_id_sequence(session, model)
            sync_id_sequence(session, CatConcepto)

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
        self.logger.info(f"Etapa Load completa. Estadisticas: {input_data}")
        return input_data

    def _build_record(self, row: dict, now: datetime) -> dict:
        return {
            "anio": int(row["anio"]),
            "trimestre_id": int(row["trimestre_id"]),
            "cve_ent": int(row["cve_ent"]),
            "tema_id": int(row["tema_id"]),
            "clasificador_id": int(row["clasificador_id"]),
            "concepto_id": int(row["concepto_id"]),
            "valor": int(row["valor"]),
            "estatus_id": int(row["estatus_id"]),
            "row_hash": row["row_hash"],
            "is_current": True,
            "valid_from": now,
            "valid_to": None,
        }

    def _load_bootstrap(self, df: pd.DataFrame, now: datetime) -> int:
        records = [self._build_record(row, now) for row in df.to_dict(orient="records")]
        with self.db.get_session() as session:
            bulk_insert(session, records, FinanzasTrimestral, chunk_size=settings.EFIPEM_LOAD_BATCH_SIZE)
        self.logger.info(f"Bootstrap: {len(records)} registros insertados")
        return len(records)

    def _load_update(self, df: pd.DataFrame, now: datetime) -> tuple[int, int]:
        with self.db.get_session() as session:
            active_rows = (
                session.query(
                    FinanzasTrimestral.id,
                    FinanzasTrimestral.anio,
                    FinanzasTrimestral.trimestre_id,
                    FinanzasTrimestral.cve_ent,
                    FinanzasTrimestral.tema_id,
                    FinanzasTrimestral.clasificador_id,
                    FinanzasTrimestral.concepto_id,
                    FinanzasTrimestral.row_hash,
                )
                .filter(FinanzasTrimestral.is_current == True)  # noqa: E712
                .all()
            )

        active_index: dict[tuple, tuple[int, str]] = {
            (r.anio, r.trimestre_id, r.cve_ent, r.tema_id, r.clasificador_id, r.concepto_id): (r.id, r.row_hash)
            for r in active_rows
        }
        self.logger.info(f"Registros activos en BD: {len(active_index)}")

        ids_to_close: list[int] = []
        records_to_insert: list[dict] = []

        for row in df.to_dict(orient="records"):
            key = (
                int(row["anio"]),
                int(row["trimestre_id"]),
                int(row["cve_ent"]),
                int(row["tema_id"]),
                int(row["clasificador_id"]),
                int(row["concepto_id"]),
            )
            incoming_hash: str = row["row_hash"]

            if key not in active_index:
                records_to_insert.append(self._build_record(row, now))
            else:
                db_id, db_hash = active_index[key]
                if incoming_hash != db_hash:
                    ids_to_close.append(db_id)
                    records_to_insert.append(self._build_record(row, now))

        self.logger.info(
            f"Update: {len(ids_to_close)} registros a cerrar, {len(records_to_insert)} registros a insertar"
        )

        with self.db.get_session() as session:
            if ids_to_close:
                session.execute(
                    update(FinanzasTrimestral)
                    .where(FinanzasTrimestral.id.in_(ids_to_close))
                    .values(valid_to=now, is_current=False)
                )
            if records_to_insert:
                bulk_insert(
                    session,
                    records_to_insert,
                    FinanzasTrimestral,
                    chunk_size=settings.EFIPEM_LOAD_BATCH_SIZE,
                )

        return len(records_to_insert), len(ids_to_close)

    def _load_catalogs(self, session, catalog_values: dict[str, list[str]]) -> None:
        for cat_key, values in catalog_values.items():
            model = CATALOG_MODELS[cat_key]
            records = [{"name": v} for v in values]
            insert_records(session, records, model, conflict_keys=["name"])
            self.logger.info(f"Catalogo '{cat_key}': {len(records)} valores sincronizados.")

        session.flush()

        for cat_key, model in CATALOG_MODELS.items():
            self._catalog_caches[cat_key] = get_mapping(session, model, "name", "id")

    def _load_conceptos(self, session, concepto_pairs: list[tuple[str, str]]) -> None:
        clasificador_map = self._catalog_caches["clasificador"]
        records = []
        for clasificador_name, concepto_name in concepto_pairs:
            clasif_id = clasificador_map.get(clasificador_name)
            if clasif_id is None:
                self.logger.warning(f"Clasificador no encontrado en cache: {clasificador_name!r}")
                continue
            records.append({"clasificador_id": clasif_id, "name": concepto_name})

        insert_records(session, records, CatConcepto, conflict_keys=["clasificador_id", "name"])
        session.flush()

        rows = session.query(CatConcepto.clasificador_id, CatConcepto.name, CatConcepto.id).all()
        self._concepto_cache = {(r[0], r[1]): r[2] for r in rows}
        self.logger.info(f"Catalogo 'concepto': {len(self._concepto_cache)} entradas en cache")

    def _resolve_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in CATALOG_COLUMNS:
            cache = self._catalog_caches[col]
            df[f"{col}_id"] = df[col].map(cache)

        df["concepto_id"] = df.apply(
            lambda row: self._concepto_cache.get((row["clasificador_id"], row["concepto"])),
            axis=1,
        )

        required_fk = ["trimestre_id", "tema_id", "clasificador_id", "concepto_id", "estatus_id"]
        for col in required_fk:
            null_count = df[col].isna().sum()
            if null_count:
                sample = df[df[col].isna()].head(3).to_dict(orient="records")
                raise ValueError(f"FK '{col}' tiene {null_count} valores nulos. Muestra: {sample}")

        return df
