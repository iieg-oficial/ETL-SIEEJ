import pandas as pd

from datetime import datetime, timezone
from typing import Any, Optional

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
    FinanzasMunicipal,
)
from more_itertools import chunked
from sqlalchemy.dialects.postgresql import insert as pg_insert

from core.pipelines.stage import Stage
from core.utils.bulk_ops import (
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
        records_inserted = self._load_bootstrap(df, now)

        with self.db.get_session() as session:
            sync_id_sequence(session, FinanzasMunicipal)
            for model in CATALOG_MODELS.values():
                sync_id_sequence(session, model)
            sync_id_sequence(session, CatConcepto)

        return {
            "mode": self.mode,
            "records_inserted": records_inserted,
        }

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        clean_directory(self.work_dir, self.logger)
        if self.db:
            self.db.disconnect()
        self.logger.info(f"Etapa Load completa. Estadisticas: {input_data}")
        return input_data

    def _build_record(self, row: dict) -> dict:
        return {
            "anio": int(row["anio"]),
            "cvegeo": str(row["cvegeo"]),
            "cve_ent": int(row["cve_ent"]),
            "cve_mun": int(row["cve_mun"]),
            "tema_id": int(row["tema_id"]),
            "clasificador_id": int(row["clasificador_id"]),
            "concepto_id": int(row["concepto_id"]),
            "valor": int(row["valor"]),
            "estatus_id": int(row["estatus_id"]),
        }

    def _load_bootstrap(self, df: pd.DataFrame, now: datetime) -> int:
        records = [self._build_record(row) for row in df.to_dict(orient="records")]
        inserted = 0
        with self.db.get_session() as session:
            for i, chunk in enumerate(chunked(records, settings.EFIPEM_LOAD_BATCH_SIZE), start=1):
                chunk = list(chunk)
                stmt = pg_insert(FinanzasMunicipal).values(chunk)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=["anio", "cvegeo", "tema_id", "clasificador_id", "concepto_id"]
                )
                result = session.execute(stmt)
                inserted += result.rowcount
                self.logger.info(
                    f"  chunk {i}: {min(i * settings.EFIPEM_LOAD_BATCH_SIZE, len(records))}/{len(records)}"
                )
        self.logger.info(
            f"Bootstrap: {inserted} registros insertados ({len(records) - inserted} omitidos por conflicto)"
        )
        return inserted

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

        required_fk = ["tema_id", "clasificador_id", "concepto_id", "estatus_id"]
        for col in required_fk:
            null_count = df[col].isna().sum()
            if null_count:
                sample = df[df[col].isna()].head(3).to_dict(orient="records")
                raise ValueError(f"FK '{col}' tiene {null_count} valores nulos. Muestra: {sample}")

        return df
