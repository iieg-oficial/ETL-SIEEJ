import pandas as pd

from typing import Any, Optional

from sqlalchemy import text

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
        self._entidad_id_by_cve_ent: dict[str, int] = {}

    # Conecta a la BD y verifica tablas
    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data:
            raise ValueError("Load no recibio datos de Transform.")

        self.db = Database(PIPELINE_NAME, settings.database_url)
        self.db.connect()

        EfipemBase.metadata.create_all(self.db.engine)
        self.logger.info("Tablas verificadas/creadas.")

        return input_data

    # Carga catalogos, resuelve FKs y persiste registros
    def action(self, input_data: Optional[Any] = None) -> dict:
        df: pd.DataFrame = input_data["df"]
        catalog_values: dict[str, list[str]] = input_data["catalogs"]
        concepto_pairs: list[tuple[str, str]] = input_data["concepto_pairs"]

        with self.db.get_session() as session:
            self._load_catalogs(session, catalog_values)
            self._load_conceptos(session, concepto_pairs)
            self._load_entidad_cache(session)

        df = self._resolve_ids(df)

        stats = self._load_records(df)
        return stats

    # Sincroniza secuencias, limpia carpeta y desconecta
    def finalization(self, input_data: Optional[Any] = None) -> dict:
        with self.db.get_session() as session:
            for model in CATALOG_MODELS.values():
                sync_id_sequence(session, model)
            sync_id_sequence(session, CatConcepto)
            sync_id_sequence(session, FinanzasTrimestral)

        clean_directory(self.work_dir, self.logger)

        self.db.disconnect()
        self.logger.info(f"Etapa Load completa. Estadisticas: {input_data}")
        return input_data

    # Inserta valores en catalogos simples y construye caches name->id
    def _load_catalogs(self, session, catalog_values: dict[str, list[str]]) -> None:
        for cat_key, values in catalog_values.items():
            model = CATALOG_MODELS[cat_key]
            records = [{"name": v} for v in values]
            insert_records(session, records, model, conflict_keys=["name"])
            self.logger.info(f"Catalogo '{cat_key}': {len(records)} valores sincronizados.")

        session.flush()

        for cat_key, model in CATALOG_MODELS.items():
            self._catalog_caches[cat_key] = get_mapping(session, model, "name", "id")

    # Inserta conceptos (clasificador_id, name) y construye cache
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

    # Carga mapping cve_ent -> cvegeo_states.id (FDW)
    def _load_entidad_cache(self, session) -> None:
        rows = session.execute(text("SELECT cve_ent, id FROM cvegeo_states")).all()
        # cve_ent en cvegeo_states es INTEGER; lo normalizamos a str zfill(2) para match
        self._entidad_id_by_cve_ent = {str(r[0]).zfill(2): r[1] for r in rows}
        self.logger.info(f"Cache entidades cvegeo: {len(self._entidad_id_by_cve_ent)} entradas")

    # Agrega columnas *_id resolviendo catalogos y entidad
    def _resolve_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in CATALOG_COLUMNS:
            cache = self._catalog_caches[col]
            df[f"{col}_id"] = df[col].map(cache)

        # concepto_id depende de (clasificador_id, concepto)
        df["concepto_id"] = df.apply(
            lambda row: self._concepto_cache.get((row["clasificador_id"], row["concepto"])),
            axis=1,
        )

        # entidad_id via cvegeo FDW
        df["entidad_id"] = df["cve_ent"].map(self._entidad_id_by_cve_ent)

        # Validar que no haya FKs nulos en campos obligatorios
        required_fk = ["trimestre_id", "tema_id", "clasificador_id", "concepto_id", "estatus_id"]
        for col in required_fk:
            null_count = df[col].isna().sum()
            if null_count:
                sample = df[df[col].isna()].head(3).to_dict(orient="records")
                raise ValueError(f"FK '{col}' tiene {null_count} valores nulos. Muestra: {sample}")

        return df

    # Bootstrap/update: para EFIPEM la fuente sobreescribe => TRUNCATE + bulk_insert
    def _load_records(self, df: pd.DataFrame) -> dict:
        records = [
            {
                "anio": int(row["anio"]),
                "trimestre_id": int(row["trimestre_id"]),
                "cve_ent": row["cve_ent"],
                "entidad_id": int(row["entidad_id"]) if pd.notna(row["entidad_id"]) else None,
                "tema_id": int(row["tema_id"]),
                "clasificador_id": int(row["clasificador_id"]),
                "concepto_id": int(row["concepto_id"]),
                "valor": int(row["valor"]),
                "estatus_id": int(row["estatus_id"]),
            }
            for _, row in df.iterrows()
        ]

        batch_size = settings.EFIPEM_LOAD_BATCH_SIZE

        with self.db.get_session() as session:
            if self.mode == "update":
                self.logger.info("Modo update: TRUNCATE de stg_efipem_finanzas_trimestral")
                session.execute(text(f"TRUNCATE TABLE {FinanzasTrimestral.__tablename__} RESTART IDENTITY"))

            bulk_insert(session, records, FinanzasTrimestral, chunk_size=batch_size)
            self.logger.info(f"Insertados {len(records)} registros en {FinanzasTrimestral.__tablename__}.")

        return {
            "mode": self.mode,
            "inserted": len(records),
        }
