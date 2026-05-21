"""Load stages para el pipeline asg_imss.

* `AsgImssCatalogLoader` inserta los 12 catálogos en orden topológico
  (delegacion → subdelegacion, entidad → municipio, sector_1 → sector_2 →
  sector_4, y los catálogos simples).
* `AsgImssDataLoader` resuelve FK por clave (auto-poblando catálogos con
  descripcion='SIN DESCRIPCION' cuando falta) e inserta en `stg_asg_imss`
  en lotes de BATCH_SIZE.

El `AsgImssDataLoader` mantiene una conexión DB y cachés de lookup
abiertas entre invocaciones de `execute()` (un mes por invocación). El
orquestador llama `setup()` antes del bucle y `teardown()` al final.
"""

from typing import Any, Optional

import pandas as pd
from sqlalchemy.dialects.postgresql import insert as pg_insert

from core.db import Database
from core.pipelines.asg_imss.attributes import (
    CSV_FK_TO_STG_COLUMN,
    METRIC_FLOAT_COLUMNS,
    METRIC_INT_COLUMNS,
)
from core.pipelines.asg_imss.config import PIPELINE_NAME, settings
from core.pipelines.asg_imss.schemas import (
    CatDelegacion,
    CatEntidad,
    CatMunicipio,
    CatRangoEdad,
    CatRangoSalario,
    CatRangoUma,
    CatSector1,
    CatSector2,
    CatSector4,
    CatSexo,
    CatSubdelegacion,
    CatTamanoRegistroPatronal,
    StgAsgImss,
)
from core.pipelines.stage import Stage
from core.utils.bulk_ops import bulk_insert, insert_records, sync_id_sequence


# ---------------------------------------------------------------------------
# Catalog Loader
# ---------------------------------------------------------------------------


class AsgImssCatalogLoader(Stage):
    """Carga los 12 catálogos del XLSX en orden topológico."""

    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode

    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data:
            raise ValueError("AsgImssCatalogLoader requiere catálogos parseados.")
        return input_data

    def action(self, input_data: Optional[Any] = None) -> dict:
        catalogs: dict[str, list[dict]] = input_data
        db = Database(PIPELINE_NAME, settings.database_url)
        db.connect()

        try:
            with db.get_session() as session:
                # 1. delegacion
                insert_records(session, catalogs.get("delegacion", []), CatDelegacion, ["clave"])
                session.flush()
                deleg_map = {row.clave: row.id for row in session.query(CatDelegacion).all()}

                # 2. subdelegacion (necesita delegacion_id)
                sub_records = [
                    {
                        "clave": r["clave"],
                        "descripcion": r["descripcion"],
                        "delegacion_id": deleg_map[r["delegacion_clave"]],
                    }
                    for r in catalogs.get("subdelegacion", [])
                    if r["delegacion_clave"] in deleg_map
                ]
                insert_records(
                    session,
                    sub_records,
                    CatSubdelegacion,
                    ["delegacion_id", "clave"],
                )

                # 3. entidad
                insert_records(session, catalogs.get("entidad", []), CatEntidad, ["clave"])
                session.flush()
                ent_map = {row.clave: row.id for row in session.query(CatEntidad).all()}

                # 4. municipio
                mun_records = [
                    {
                        "clave": r["clave"],
                        "descripcion": r["descripcion"],
                        "entidad_id": ent_map[r["entidad_clave"]],
                    }
                    for r in catalogs.get("municipio", [])
                    if r["entidad_clave"] in ent_map
                ]
                insert_records(session, mun_records, CatMunicipio, ["entidad_id", "clave"])

                # 5. sector_1
                insert_records(session, catalogs.get("sector_1", []), CatSector1, ["clave"])
                session.flush()
                s1_map = {row.clave: row.id for row in session.query(CatSector1).all()}

                # 6. sector_2
                s2_records = [
                    {
                        "clave": r["clave"],
                        "descripcion": r["descripcion"],
                        "sector_1_id": s1_map[r["sector_1_clave"]],
                    }
                    for r in catalogs.get("sector_2", [])
                    if r["sector_1_clave"] in s1_map
                ]
                insert_records(session, s2_records, CatSector2, ["clave"])
                session.flush()
                s2_map = {row.clave: row.id for row in session.query(CatSector2).all()}

                # 7. sector_4
                s4_records = [
                    {
                        "clave": r["clave"],
                        "descripcion": r["descripcion"],
                        "sector_2_id": s2_map[r["sector_2_clave"]],
                    }
                    for r in catalogs.get("sector_4", [])
                    if r["sector_2_clave"] in s2_map
                ]
                insert_records(session, s4_records, CatSector4, ["clave"])

                # 8-12. catálogos simples
                simple_map = {
                    "tamano_registro_patronal": CatTamanoRegistroPatronal,
                    "sexo": CatSexo,
                    "rango_edad": CatRangoEdad,
                    "rango_salario": CatRangoSalario,
                    "rango_uma": CatRangoUma,
                }
                for key, model in simple_map.items():
                    insert_records(session, catalogs.get(key, []), model, ["clave"])

                # Sync sequences
                for model in [
                    CatDelegacion,
                    CatSubdelegacion,
                    CatEntidad,
                    CatMunicipio,
                    CatSector1,
                    CatSector2,
                    CatSector4,
                    CatTamanoRegistroPatronal,
                    CatSexo,
                    CatRangoEdad,
                    CatRangoSalario,
                    CatRangoUma,
                ]:
                    sync_id_sequence(session, model)

            self.logger.info("✅ Catálogos cargados.")
            return {"status": "ok"}
        finally:
            db.disconnect()

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        return input_data


# ---------------------------------------------------------------------------
# Data Loader (stateful: connect/disconnect externo)
# ---------------------------------------------------------------------------

# Mapeos CSV col → (modelo, "simple"|"sub"|"municipio"|"sector"|"nullable_sector")
# describe la estrategia para resolver/insertar FK por clave.
_CATALOG_RESOLVER: dict[str, dict] = {
    "cve_subdelegacion": {"model": CatSubdelegacion, "kind": "subdelegacion"},
    "cve_municipio": {"model": CatMunicipio, "kind": "municipio"},
    "sector_economico_4": {"model": CatSector4, "kind": "sector_4"},
    "tamano_patron": {"model": CatTamanoRegistroPatronal, "kind": "simple"},
    "sexo": {"model": CatSexo, "kind": "simple"},
    "rango_edad": {"model": CatRangoEdad, "kind": "simple"},
    "rango_salarial": {"model": CatRangoSalario, "kind": "simple"},
    "rango_uma": {"model": CatRangoUma, "kind": "simple"},
}


class AsgImssDataLoader(Stage):
    """Carga datos mensuales en `stg_asg_imss` resolviendo FKs por clave."""

    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode
        self.db: Optional[Database] = None
        # Cachés en memoria
        self._cache_simple: dict[str, dict[str, int]] = {}
        self._cache_subdelegacion: dict[tuple[int, str], int] = {}
        self._cache_municipio: dict[tuple[int, str], int] = {}
        self._auto_inserted_counter: dict[str, int] = {}

    # ---------- Lifecycle externo ----------
    def setup(self) -> None:
        self.db = Database(PIPELINE_NAME, settings.database_url)
        self.db.connect()
        self._load_caches()

    def teardown(self) -> None:
        if self.db is not None:
            self.db.disconnect()
            self.db = None
        if self._auto_inserted_counter:
            self.logger.info(f"Catálogos auto-poblados: {self._auto_inserted_counter}")

    def _load_caches(self) -> None:
        assert self.db is not None
        with self.db.get_session() as session:
            for model in [
                CatDelegacion,
                CatEntidad,
                CatSector1,
                CatSector2,
                CatSector4,
                CatTamanoRegistroPatronal,
                CatSexo,
                CatRangoEdad,
                CatRangoSalario,
                CatRangoUma,
            ]:
                self._cache_simple[model.__tablename__] = {r.clave: r.id for r in session.query(model).all()}
            self._cache_subdelegacion = {
                (r.delegacion_id, r.clave): r.id for r in session.query(CatSubdelegacion).all()
            }
            self._cache_municipio = {(r.entidad_id, r.clave): r.id for r in session.query(CatMunicipio).all()}
        self.logger.info(
            "Cachés de catálogos cargadas: "
            + ", ".join(f"{k}={len(v)}" for k, v in self._cache_simple.items())
            + f", subdelegacion={len(self._cache_subdelegacion)}"
            + f", municipio={len(self._cache_municipio)}"
        )

    # ---------- Resolución de FKs ----------
    def _insert_simple_cat(self, session, model, clave: str) -> int:
        stmt = (
            pg_insert(model)
            .values(clave=clave, descripcion="SIN DESCRIPCION")
            .on_conflict_do_nothing(index_elements=["clave"])
            .returning(model.id)
        )
        result = session.execute(stmt).scalar()
        if result is None:
            # Conflicto: alguien lo insertó antes (o estaba ya); leer id
            result = session.query(model.id).filter(model.clave == clave).scalar()
        self.logger.warning(f"Clave nueva en {model.__tablename__}='{clave}' → SIN DESCRIPCION")
        self._auto_inserted_counter[model.__tablename__] = self._auto_inserted_counter.get(model.__tablename__, 0) + 1
        self._cache_simple[model.__tablename__][clave] = result
        return result

    def _resolve_simple(self, session, model, clave: str) -> int:
        cache = self._cache_simple[model.__tablename__]
        if clave in cache:
            return cache[clave]
        return self._insert_simple_cat(session, model, clave)

    def _resolve_subdelegacion(self, session, delegacion_id: int, clave: str) -> int:
        key = (delegacion_id, clave)
        if key in self._cache_subdelegacion:
            return self._cache_subdelegacion[key]
        stmt = (
            pg_insert(CatSubdelegacion)
            .values(
                clave=clave,
                descripcion="SIN DESCRIPCION",
                delegacion_id=delegacion_id,
            )
            .on_conflict_do_nothing(index_elements=["delegacion_id", "clave"])
            .returning(CatSubdelegacion.id)
        )
        result = session.execute(stmt).scalar()
        if result is None:
            result = (
                session.query(CatSubdelegacion.id)
                .filter(
                    CatSubdelegacion.delegacion_id == delegacion_id,
                    CatSubdelegacion.clave == clave,
                )
                .scalar()
            )
        self.logger.warning(f"Clave nueva en cat_subdelegacion=({delegacion_id},'{clave}') → SIN DESCRIPCION")
        self._auto_inserted_counter["cat_subdelegacion"] = self._auto_inserted_counter.get("cat_subdelegacion", 0) + 1
        self._cache_subdelegacion[key] = result
        return result

    def _resolve_municipio(self, session, entidad_id: int, clave: str) -> int:
        key = (entidad_id, clave)
        if key in self._cache_municipio:
            return self._cache_municipio[key]
        stmt = (
            pg_insert(CatMunicipio)
            .values(clave=clave, descripcion="SIN DESCRIPCION", entidad_id=entidad_id)
            .on_conflict_do_nothing(index_elements=["entidad_id", "clave"])
            .returning(CatMunicipio.id)
        )
        result = session.execute(stmt).scalar()
        if result is None:
            result = (
                session.query(CatMunicipio.id)
                .filter(
                    CatMunicipio.entidad_id == entidad_id,
                    CatMunicipio.clave == clave,
                )
                .scalar()
            )
        self.logger.warning(f"Clave nueva en cat_municipio=({entidad_id},'{clave}') → SIN DESCRIPCION")
        self._auto_inserted_counter["cat_municipio"] = self._auto_inserted_counter.get("cat_municipio", 0) + 1
        self._cache_municipio[key] = result
        return result

    def _resolve_sector(self, session, model, parent_id: Optional[int], clave: str) -> int:
        """Inserta sector con descripcion='SIN DESCRIPCION'. Requiere parent_id."""
        cache = self._cache_simple[model.__tablename__]
        if clave in cache:
            return cache[clave]
        values = {"clave": clave, "descripcion": "SIN DESCRIPCION"}
        if model is CatSector2:
            if parent_id is None:
                raise ValueError(f"sector_2 '{clave}' sin parent sector_1")
            values["sector_1_id"] = parent_id
        elif model is CatSector4:
            if parent_id is None:
                raise ValueError(f"sector_4 '{clave}' sin parent sector_2")
            values["sector_2_id"] = parent_id
        stmt = pg_insert(model).values(**values).on_conflict_do_nothing(index_elements=["clave"]).returning(model.id)
        result = session.execute(stmt).scalar()
        if result is None:
            result = session.query(model.id).filter(model.clave == clave).scalar()
        self.logger.warning(f"Clave nueva en {model.__tablename__}='{clave}' → SIN DESCRIPCION")
        self._auto_inserted_counter[model.__tablename__] = self._auto_inserted_counter.get(model.__tablename__, 0) + 1
        cache[clave] = result
        return result

    # ---------- Stage hooks ----------
    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data or "dataframe" not in input_data:
            raise ValueError("AsgImssDataLoader requiere 'dataframe'.")
        if self.db is None:
            raise RuntimeError("AsgImssDataLoader no inicializado. Llamar setup() antes.")
        return input_data

    def action(self, input_data: Optional[Any] = None) -> dict:
        df: pd.DataFrame = input_data["dataframe"]
        target_date = input_data["target_date"]
        if df.empty:
            self.logger.warning(f"DataFrame vacío para {target_date}; nada que cargar.")
            return {"rows_inserted": 0, "target_date": target_date}

        assert self.db is not None
        rows_inserted = 0
        with self.db.get_session() as session:
            # Resolución de FKs (vectorizada por columna)
            resolved: dict[str, list[Optional[int]]] = {}

            # Catálogos simples que van directamente a stg
            for csv_col in [
                "tamano_patron",
                "sexo",
                "rango_edad",
                "rango_salarial",
                "rango_uma",
            ]:
                model = _CATALOG_RESOLVER[csv_col]["model"]
                ids: list[Optional[int]] = []
                for v in df[csv_col].tolist():
                    ids.append(self._resolve_simple(session, model, v))
                resolved[CSV_FK_TO_STG_COLUMN[csv_col]] = ids

            # delegacion — intermedio para resolver subdelegacion (NO va a stg)
            deleg_ids: list[int] = []
            for v in df["cve_delegacion"].tolist():
                deleg_ids.append(self._resolve_simple(session, CatDelegacion, v))

            # Subdelegacion (depende de delegacion_id)
            sub_ids: list[Optional[int]] = []
            for deleg_id, clave in zip(deleg_ids, df["cve_subdelegacion"].tolist()):
                sub_ids.append(self._resolve_subdelegacion(session, deleg_id, clave))
            resolved["subdelegacion_id"] = sub_ids

            # entidad — intermedio para resolver municipio (NO va a stg)
            ent_ids: list[int] = []
            for v in df["cve_entidad"].tolist():
                ent_ids.append(self._resolve_simple(session, CatEntidad, v))

            # Municipio (depende de entidad_id)
            mun_ids: list[Optional[int]] = []
            for ent_id, clave in zip(ent_ids, df["cve_municipio"].tolist()):
                mun_ids.append(self._resolve_municipio(session, ent_id, clave))
            resolved["municipio_id"] = mun_ids

            # sector_1 y sector_2 — intermedios para resolver sector_4 (NO van a stg)
            s1_ids: list[Optional[int]] = []
            for v in df["sector_economico_1"].tolist():
                if v == "" or v is None:
                    s1_ids.append(None)
                else:
                    s1_ids.append(self._resolve_sector(session, CatSector1, None, v))

            s2_ids: list[Optional[int]] = []
            for s1_id, v in zip(s1_ids, df["sector_economico_2"].tolist()):
                if v == "" or v is None:
                    s2_ids.append(None)
                else:
                    s2_ids.append(self._resolve_sector(session, CatSector2, s1_id, v))

            s4_ids: list[Optional[int]] = []
            for s2_id, v in zip(s2_ids, df["sector_economico_4"].tolist()):
                if v == "" or v is None:
                    s4_ids.append(None)
                else:
                    s4_ids.append(self._resolve_sector(session, CatSector4, s2_id, v))
            resolved["sector_4_id"] = s4_ids

            session.flush()

            # Construcción de registros para bulk insert
            metric_cols = METRIC_INT_COLUMNS + METRIC_FLOAT_COLUMNS
            metrics = {c: df[c].tolist() for c in metric_cols}

            records: list[dict] = []
            n = len(df)
            for i in range(n):
                rec = {"fecha_corte": target_date}
                for fk_col, ids in resolved.items():
                    rec[fk_col] = ids[i]
                for c in metric_cols:
                    rec[c] = metrics[c][i]
                records.append(rec)

            # Bulk insert con batch
            bulk_insert(session, records, StgAsgImss, chunk_size=settings.BATCH_SIZE)
            rows_inserted = len(records)

        self.logger.info(f"✅ {target_date}: {rows_inserted:,} filas insertadas.")
        return {"rows_inserted": rows_inserted, "target_date": target_date}

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        return input_data
