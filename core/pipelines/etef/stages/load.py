import pandas as pd

from typing import Any, Optional

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

        # Construir registros para inserción
        records = []
        for _, row in df.iterrows():
            record = {
                "anio": int(row["anio"]) if pd.notna(row["anio"]) else None,
                "trimestre": row["trimestre"],
                "mes": row["mes"],
                "cve_ent": int(row["cve_ent"]) if pd.notna(row["cve_ent"]) else None,
                "codigo_scian_id": row.get("codigo_scian_id"),
                "val_usd": float(row["val_usd"]) if pd.notna(row["val_usd"]) else None,
                "estatus_cifra": row.get("estatus_cifra"),
                "estatus": row.get("estatus"),
            }
            records.append(record)

        self.logger.info(f"Insertando {len(records)} registros en stg_etef_datos")

        with self.db.get_session() as session:
            batch_size = settings.ETEF_LOAD_BATCH_SIZE
            bulk_insert(session, records, EtefDatos, batch_size=batch_size)
            self.logger.info(f"Insertados {len(records)} registros")

            # Sincronizar secuencias SERIAL
            sync_id_sequence(session, EtefDatos)
            for model in CATALOG_MODELS.values():
                sync_id_sequence(session, model)

        return {
            "mode": self.mode,
            "records_inserted": len(records),
            "catalogs_synced": len(catalog_values),
        }

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        clean_directory(self.work_dir, self.logger)
        if self.db:
            self.db.disconnect()
        self.logger.info(f"Etapa Load completa. Estadísticas: {input_data}")
        return input_data

    def _load_catalogs(self, session, catalog_values: dict[str, list[str]]) -> None:
        for cat_key, values in catalog_values.items():
            model = CATALOG_MODELS[cat_key]
            records = [
                {"codigo": v, "descripcion": None, "version": None}
                for v in values
            ]
            insert_records(session, records, model, conflict_keys=["codigo"])
            self.logger.info(f"Catálogo '{cat_key}': {len(records)} valores sincronizados")

        session.flush()

        # Cargar mapas código->id para resolución de FKs
        for cat_key, model in CATALOG_MODELS.items():
            self._catalog_caches[cat_key] = get_mapping(session, model, "codigo", "id")

    def _resolve_catalog_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in CATALOG_COLUMNS:
            if col in df.columns and col in self._catalog_caches:
                cache = self._catalog_caches[col]
                series = df[col].apply(lambda v: cache.get(str(v)) if v is not None else None).astype(object)
                df[f"{col}_id"] = series.where(pd.notna(series), other=None)
                self.logger.info(f"Resueltos IDs para columna '{col}'")
        return df
