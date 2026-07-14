import pandas as pd

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import text

from core.db import Database
from core.pipelines.repd.config import settings
from core.pipelines.repd.consts import (
    CATALOG_COLUMNS,
    HASH_FIELDS,
    MUNICIPALITY_COLUMNS,
    PIPELINE_NAME,
    SKIP_MUNICIPALITY_VALUES,
)
from core.pipelines.repd.queries import MATERIALIZED_VIEWS
from core.pipelines.repd.schemas import (
    CATALOG_MODELS,
    Casos,
    CasosHistorial,
    RepdBase,
)
from core.pipelines.stage import Stage
from core.utils.bulk_ops import (
    bulk_insert,
    get_mapping,
    insert_records,
    sync_id_sequence,
)
from core.utils.files import clean_directory
from core.utils.normalize import normalize_text
from core.utils.records import compute_record_hash
from core.utils.views import refresh_materialized_views


class REPDLoader(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode
        self.db: Database | None = None
        self._catalog_caches: dict[str, dict[str, int]] = {}
        self._municipality_cache: dict[tuple[str, str], int] = {}

    # Conecta a la BD y verifica tablas
    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data:
            raise ValueError("Load no recibio datos de Transform.")

        self.db = Database(PIPELINE_NAME, settings.database_url)
        self.db.connect()

        RepdBase.metadata.create_all(self.db.engine)
        self.logger.info("Tablas verificadas/creadas.")

        return input_data

    # Carga catalogos, resuelve FKs y persiste registros
    def action(self, input_data: Optional[Any] = None) -> dict:
        df: pd.DataFrame = input_data["df"]
        catalog_values: dict[str, list[str]] = input_data["catalogs"]

        with self.db.get_session() as session:
            self._load_catalogs(session, catalog_values)
            self._load_municipality_cache(session)

        df = self._resolve_catalog_ids(df)
        df = self._resolve_municipality_ids(df)

        # Calcular record_hash
        df["record_hash"] = df.apply(lambda row: compute_record_hash(row.to_dict(), HASH_FIELDS), axis=1)

        if self.mode == "bootstrap":
            stats = self._load_bootstrap(df)
        else:
            stats = self._load_update(df)

        refresh_materialized_views(self.db, MATERIALIZED_VIEWS)

        return stats

    # Sincroniza secuencias, limpia carpeta de datos y desconecta
    def finalization(self, input_data: Optional[Any] = None) -> dict:
        with self.db.get_session() as session:
            for model in CATALOG_MODELS.values():
                sync_id_sequence(session, model)
            sync_id_sequence(session, Casos)
            sync_id_sequence(session, CasosHistorial)

        clean_directory(self.work_dir, self.logger)

        self.db.disconnect()
        self.logger.info(f"Etapa Load completa. Estadisticas: {input_data}")
        return input_data

    # Inserta valores en tablas catalogo y construye caches name->id
    def _load_catalogs(self, session, catalog_values: dict[str, list[str]]) -> None:
        for cat_key, values in catalog_values.items():
            model = CATALOG_MODELS[cat_key]
            records = [{"nombre": v} for v in values]
            insert_records(session, records, model, conflict_keys=["nombre"])
            self.logger.info(f"Catalogo '{cat_key}': {len(records)} valores sincronizados.")

        session.flush()

        for cat_key, model in CATALOG_MODELS.items():
            self._catalog_caches[cat_key] = get_mapping(session, model, "nombre", "id", is_normalize=True)

    # Inserta nuevos valores en un catalogo y refresca su cache
    def _refresh_catalog(self, session, cat_key: str, new_values: list[str]) -> None:
        model = CATALOG_MODELS[cat_key]
        records = [{"nombre": v} for v in new_values]
        insert_records(session, records, model, conflict_keys=["nombre"])
        session.flush()
        self._catalog_caches[cat_key] = get_mapping(session, model, "nombre", "id", is_normalize=True)

    # Carga el mapping (estado, municipio)->id desde cvegeo via FDW
    def _load_municipality_cache(self, session) -> None:
        results = session.execute(text("SELECT nom_ent, nomgeo, id FROM cvegeo_municipalities")).all()
        self._municipality_cache = {(normalize_text(row[0]), normalize_text(row[1])): row[2] for row in results}
        self.logger.info(f"Cache de municipios cvegeo: {len(self._municipality_cache)} entradas")

    # Resuelve (estado, municipio) a ID de cvegeo
    def _resolve_municipality_id(self, state: str | None, name: str | None) -> int | None:
        if name is None or name in SKIP_MUNICIPALITY_VALUES:
            return None
        if state is None:
            return None
        normalized_name = normalize_text(name)
        key = (normalize_text(state), normalized_name)
        return self._municipality_cache.get(key)

    # Agrega columnas *_id mapeando nombre->id de catalogo
    def _resolve_catalog_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in CATALOG_COLUMNS:
            cache = self._catalog_caches[col]
            series = df[col].apply(lambda v: cache.get(normalize_text(v)) if v is not None else None).astype(object)
            df[f"{col}_id"] = series.where(pd.notna(series), other=None)
        return df

    # Resuelve columnas de municipio a IDs de cvegeo
    def _resolve_municipality_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        for mun_col, state_col, id_col in MUNICIPALITY_COLUMNS:
            series = df.apply(
                lambda row: self._resolve_municipality_id(row.get(state_col), row.get(mun_col)),
                axis=1,
            ).astype(object)
            df[id_col] = series.where(pd.notna(series), other=None)
        return df

    # Carga inicial: inserta todos los registros en current e history
    def _load_bootstrap(self, df: pd.DataFrame) -> dict:
        now = datetime.utcnow()

        current_records = []
        history_records = []

        for _, row in df.iterrows():
            rec = self._build_case_record(row)
            current_records.append(
                {
                    **rec,
                    "version_actual": 1,
                    "fecha_creacion": now,
                    "fecha_actualizacion": now,
                }
            )
            history_records.append(
                {
                    **rec,
                    "numero_version": 1,
                    "es_vigente": True,
                    "vigente_desde": now,
                    "vigente_hasta": None,
                    "fecha_creacion": now,
                }
            )

        batch_size = settings.REPD_LOAD_BATCH_SIZE

        with self.db.get_session() as session:
            bulk_insert(session, current_records, Casos, chunk_size=batch_size)
            self.logger.info(f"Insertados {len(current_records)} registros en casos.")

        # Asociar caso_id a historial
        with self.db.get_session() as session:
            feb_to_id = get_mapping(session, Casos, "feb", "id")

        for rec in history_records:
            rec["caso_id"] = feb_to_id.get(rec["feb"])

        with self.db.get_session() as session:
            bulk_insert(session, history_records, CasosHistorial, chunk_size=batch_size)
            self.logger.info(f"Insertados {len(history_records)} registros en casos_historial.")

        return {
            "mode": "bootstrap",
            "current_inserted": len(current_records),
            "history_inserted": len(history_records),
        }

    # Carga incremental: detecta cambios por hash y versiona (SCD2)
    def _load_update(self, df: pd.DataFrame) -> dict:
        now = datetime.utcnow()

        # Prefetch: feb -> {id, record_hash, version_actual}
        with self.db.get_session() as session:
            existing_rows = session.query(
                Casos.id,
                Casos.feb,
                Casos.record_hash,
                Casos.version_actual,
            ).all()
        existing_by_feb = {
            row.feb: {
                "id": row.id,
                "hash": row.record_hash,
                "version": row.version_actual,
            }
            for row in existing_rows
        }
        self.logger.info(f"Registros existentes en current: {len(existing_by_feb)}")

        new_current = []
        new_history = []
        updated_current = []
        closed_history = []
        updated_history = []

        for _, row in df.iterrows():
            rec = self._build_case_record(row)
            feb = rec["feb"]
            existing = existing_by_feb.get(feb)

            if existing is None:
                # Registro nuevo
                new_current.append(
                    {
                        **rec,
                        "version_actual": 1,
                        "fecha_creacion": now,
                        "fecha_actualizacion": now,
                    }
                )
                new_history.append(
                    {
                        **rec,
                        "numero_version": 1,
                        "es_vigente": True,
                        "vigente_desde": now,
                        "vigente_hasta": None,
                        "fecha_creacion": now,
                    }
                )

            elif existing["hash"] != rec["record_hash"]:
                # Registro cambio: crear nueva version
                new_version = existing["version"] + 1
                updated_current.append(
                    {
                        "feb": feb,
                        "case_id": existing["id"],
                        "record": {
                            **rec,
                            "version_actual": new_version,
                            "fecha_actualizacion": now,
                        },
                    }
                )
                closed_history.append(
                    {
                        "feb": feb,
                        "old_version": existing["version"],
                        "vigente_hasta": now,
                    }
                )
                updated_history.append(
                    {
                        **rec,
                        "caso_id": existing["id"],
                        "numero_version": new_version,
                        "es_vigente": True,
                        "vigente_desde": now,
                        "vigente_hasta": None,
                        "fecha_creacion": now,
                    }
                )

        batch_size = settings.REPD_LOAD_BATCH_SIZE

        # Insertar registros nuevos
        if new_current:
            with self.db.get_session() as session:
                bulk_insert(session, new_current, Casos, chunk_size=batch_size)

            with self.db.get_session() as session:
                feb_to_id = get_mapping(session, Casos, "feb", "id")
            for rec in new_history:
                rec["caso_id"] = feb_to_id.get(rec["feb"])

            with self.db.get_session() as session:
                bulk_insert(session, new_history, CasosHistorial, chunk_size=batch_size)

        # Actualizar registros que cambiaron
        if updated_current:
            with self.db.get_session() as session:
                for item in updated_current:
                    session.query(Casos).filter(Casos.id == item["case_id"]).update(item["record"])

                for item in closed_history:
                    session.query(CasosHistorial).filter(
                        CasosHistorial.feb == item["feb"],
                        CasosHistorial.numero_version == item["old_version"],
                    ).update(
                        {
                            "es_vigente": False,
                            "vigente_hasta": item["vigente_hasta"],
                        }
                    )

            with self.db.get_session() as session:
                bulk_insert(session, updated_history, CasosHistorial, chunk_size=batch_size)

        unchanged = len(df) - len(new_current) - len(updated_current)
        self.logger.info(
            f"Update: {len(new_current)} nuevos, {len(updated_current)} actualizados, {unchanged} sin cambios"
        )

        return {
            "mode": "update",
            "new": len(new_current),
            "updated": len(updated_current),
            "unchanged": unchanged,
        }

    # Construye dict con campos de negocio a partir de una fila del DataFrame
    @staticmethod
    def _build_case_record(row: pd.Series) -> dict:
        return {
            "feb": row["feb"],
            "sexo_id": row.get("sexo_id"),
            "nacionalidad_id": row.get("nacionalidad_id"),
            "rango_edad_id": row.get("rango_edad_id"),
            "fecha_reporte": row.get("fecha_reporte"),
            "fecha_desaparicion": row.get("fecha_desaparicion"),
            "estado_desaparicion": row.get("estado_desaparicion"),
            "municipio_desaparicion_id": row.get("municipio_desaparicion_id"),
            "estatus_id": row.get("estatus_id"),
            "fecha_localizacion": row.get("fecha_localizacion"),
            "condicion_localizacion_id": row.get("condicion_localizacion_id"),
            "clasificacion_localizacion_id": row.get("clasificacion_localizacion_id"),
            "estado_localizacion": row.get("estado_localizacion"),
            "municipio_localizacion_id": row.get("municipio_localizacion_id"),
            "fecha_cierre": row.get("fecha_cierre"),
            "tipo_cierre_id": row.get("tipo_cierre_id"),
            "feb_vinculado": row.get("feb_vinculado"),
            "tiene_carpeta_investigacion": row.get("tiene_carpeta_investigacion"),
            "record_hash": row.get("record_hash"),
        }
