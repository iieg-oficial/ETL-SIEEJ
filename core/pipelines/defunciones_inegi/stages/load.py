from datetime import date
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from sqlalchemy import func, select

from core.db import Database
from core.pipelines.defunciones_inegi.attributes import DefuncionesInegiTables as T
from core.pipelines.defunciones_inegi.config import settings
from core.pipelines.defunciones_inegi.constants import (
    CATALOGS_FILE,
    COLUMN_CATALOG,
    EDITION_COLUMN,
    FACTS_DIR,
    EXTENDED_SCHEMA_YEAR,
    GEO_ROLES,
    PIPELINE_NAME,
    TEXT_KEY_TABLES,
    VERSIONED_COLUMN_CATALOG,
)
from core.pipelines.defunciones_inegi.helpers.catalogs import canonical_text_key
from core.pipelines.defunciones_inegi.queries import MATERIALIZED_VIEWS
from core.pipelines.defunciones_inegi.schemas import (
    CATALOG_MODELS,
    STABLE_MODELS,
    VERSIONED_MODELS,
    CatCapituloGrupo,
    CatCie10,
    CatEdicion,
    CatLocalidad,
    CatPais,
    StgDefunciones,
    StgDefuncionesAmpliacion,
)
from core.pipelines.stage import Stage
from core.utils.bulk_ops import bulk_insert, bulk_insert_do_nothing, sync_id_sequence
from core.utils.geo import localidad_code
from core.utils.mappings import map_multiindex
from core.utils.views import refresh_materialized_views
from core.utils.logger import get_logger


class DefuncionesInegiLoad(Stage):
    """Inserta catálogos, resuelve las FK de los hechos y carga por edición."""

    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode
        self.transform_dir = Path("data/transform") / PIPELINE_NAME
        self.db = Database(settings.DB_NAME, settings.database_url)
        self.logger = get_logger(f"{PIPELINE_NAME}.load")

    def source(self, input_data: Optional[Any] = None) -> dict[str, Any]:
        catalogs = pd.read_pickle(self.transform_dir / CATALOGS_FILE)
        editions = sorted(int(path.stem) for path in (self.transform_dir / FACTS_DIR).glob("*.pkl"))
        return {"catalogs": catalogs, "editions": editions}

    def action(self, input_data: dict[str, Any]) -> dict[str, int]:
        self.db.connect()
        loaded = 0
        with self.db.get_session() as session:
            years = self._edition_years(input_data["editions"], input_data["catalogs"])
            edition_ids = self._load_editions(session, years)
            self._load_catalogs(session, input_data["catalogs"], edition_ids)
            session.commit()

            mappings = self._build_mappings(session)
            for year in input_data["editions"]:
                loaded += self._load_edition_facts(session, year, edition_ids[year], mappings)
                session.commit()
        self._refresh_views()
        return {"defunciones": loaded}

    def _refresh_views(self) -> None:
        refresh_materialized_views(self.db, MATERIALIZED_VIEWS)

    @staticmethod
    def _edition_years(editions: list[int], catalogs: dict[str, list[dict]]) -> list[int]:
        """Años que debe cubrir cat_edicion.

        No basta con los de los hechos: los catálogos versionados traen la
        edición en cada registro, y cargar menos ediciones de hechos que de
        catálogos dejaba esas filas sin FK que resolver.
        """
        from_catalogs = {
            record[EDITION_COLUMN] for records in catalogs.values() for record in records if EDITION_COLUMN in record
        }
        return sorted(set(editions) | from_catalogs)

    def _load_editions(self, session, years: list[int]) -> dict[int, int]:
        today = date.today()
        records = [{"anio": year, "fecha_actualizacion": today} for year in years]
        bulk_insert_do_nothing(session, records, CatEdicion, conflict_keys=["anio"])
        session.flush()
        rows = session.execute(select(CatEdicion.anio, CatEdicion.id)).all()
        return {anio: edicion_id for anio, edicion_id in rows}

    def _load_catalogs(self, session, catalogs: dict[str, list[dict]], edition_ids: dict[int, int]) -> None:
        for table, records in catalogs.items():
            if not records:
                self.logger.warning(f"[action] {table}: sin registros")
                continue

            if table in STABLE_MODELS:
                bulk_insert_do_nothing(session, records, STABLE_MODELS[table], conflict_keys=["clave"])
            elif table == T.CAT_PAIS:
                bulk_insert_do_nothing(session, records, CatPais, conflict_keys=["clave"])
            elif table == T.CAT_CAPITULO_GRUPO:
                bulk_insert_do_nothing(session, records, CatCapituloGrupo, conflict_keys=["capitulo", "grupo"])
            elif table == T.CAT_LOCALIDAD:
                bulk_insert_do_nothing(
                    session,
                    self._with_edition(records, edition_ids),
                    CatLocalidad,
                    conflict_keys=["cvegeo", "edicion_id"],
                )
            elif table == T.CAT_CIE10:
                bulk_insert_do_nothing(
                    session, self._with_edition(records, edition_ids), CatCie10, conflict_keys=["clave", "edicion_id"]
                )
            else:
                bulk_insert_do_nothing(
                    session,
                    self._with_edition(records, edition_ids),
                    CATALOG_MODELS[table],
                    conflict_keys=["clave", "edicion_id"],
                )
            session.flush()

    @staticmethod
    def _with_edition(records: list[dict], edition_ids: dict[int, int]) -> list[dict]:
        """Cambia el año de edición por su FK y descarta la columna auxiliar."""
        stamped = []
        for record in records:
            year = record.pop(EDITION_COLUMN, None)
            stamped.append(record | {"edicion_id": edition_ids[year]})
        return stamped

    def _build_mappings(self, session) -> dict[str, dict]:
        """Clave INEGI -> id. Los versionados llevan la edición en la llave."""
        mappings: dict[str, dict] = {}
        for table, model in STABLE_MODELS.items():
            mappings[table] = {clave: row_id for clave, row_id in session.execute(select(model.clave, model.id)).all()}

        mappings[T.CAT_PAIS] = {clave: row_id for clave, row_id in session.execute(select(CatPais.clave, CatPais.id))}
        mappings[T.CAT_CAPITULO_GRUPO] = {
            (capitulo, grupo): row_id
            for capitulo, grupo, row_id in session.execute(
                select(CatCapituloGrupo.capitulo, CatCapituloGrupo.grupo, CatCapituloGrupo.id)
            ).all()
        }
        mappings[T.CAT_LOCALIDAD] = {
            (cvegeo, edicion_id): row_id
            for cvegeo, edicion_id, row_id in session.execute(
                select(CatLocalidad.cvegeo, CatLocalidad.edicion_id, CatLocalidad.id)
            ).all()
        }
        for model in (*VERSIONED_MODELS, CatCie10):
            mappings[model.__tablename__] = {
                (clave, edicion_id): row_id
                for clave, edicion_id, row_id in session.execute(select(model.clave, model.edicion_id, model.id)).all()
            }
        return mappings

    @staticmethod
    def _column(df: pd.DataFrame, name: str) -> pd.Series:
        """Las ediciones viejas no traen todas las columnas; la ausencia es nula, no un error."""
        return df[name] if name in df.columns else pd.Series(pd.NA, index=df.index)

    def _catalog_key(self, df: pd.DataFrame, column: str, table: str) -> pd.Series:
        """Castea la clave como la guarda su catálogo destino.

        El tipo de clave y el versionado son ejes independientes: hay catálogos
        versionados con clave entera (ocupacion) y no versionados con clave
        alfanumérica (grupo_lista_mexicana).
        """
        source = self._column(df, column)
        if table in TEXT_KEY_TABLES:
            return canonical_text_key(source.fillna(""))
        return pd.to_numeric(source, errors="coerce")

    def _resolve_ids(self, df: pd.DataFrame, edicion_id: int, mappings: dict[str, dict]) -> pd.DataFrame:
        for column, table in COLUMN_CATALOG.items():
            key = self._catalog_key(df, column, table)
            df[f"{column}_id"] = key.map(mappings[table]).astype("Int64")

        for column, table in VERSIONED_COLUMN_CATALOG.items():
            key = self._catalog_key(df, column, table)
            df[f"{column}_id"] = key.map(lambda clave: mappings[table].get((clave, edicion_id))).astype("Int64")

        for column in ("pais_nacimiento", "pais_nacionalidad"):
            source = pd.to_numeric(self._column(df, column), errors="coerce")
            df[f"{column}_id"] = source.map(mappings[T.CAT_PAIS]).astype("Int64")

        capitulo = pd.to_numeric(self._column(df, "capitulo"), errors="coerce")
        grupo = pd.to_numeric(self._column(df, "grupo"), errors="coerce")
        df["capitulo_grupo_id"] = map_multiindex(mappings[T.CAT_CAPITULO_GRUPO], [capitulo, grupo]).astype("Int64")

        localidades = mappings[T.CAT_LOCALIDAD]
        for entidad, municipio, localidad in GEO_ROLES:
            if localidad not in df.columns:
                df[f"{localidad}_id"] = pd.NA
                continue
            codes = [
                localidad_code(ent, mun, loc)
                for ent, mun, loc in zip(df[entidad], df[municipio], df[localidad], strict=True)
            ]
            df[f"{localidad}_id"] = pd.Series(
                [localidades.get((code, edicion_id)) if code is not None else None for code in codes], index=df.index
            ).astype("Int64")

        return df

    def _load_edition_facts(self, session, year: int, edicion_id: int, mappings: dict[str, dict]) -> int:
        df = pd.read_pickle(self.transform_dir / FACTS_DIR / f"{year}.pkl")
        df = self._resolve_ids(df, edicion_id, mappings)

        first_id = (session.execute(select(func.max(StgDefunciones.id))).scalar() or 0) + 1
        df["id"] = range(first_id, first_id + len(df))
        df["edicion_id"] = edicion_id
        df["fecha_actualizacion"] = date.today()

        facts = self._to_records(df, StgDefunciones.columns())
        bulk_insert(session, facts, StgDefunciones, chunk_size=settings.CHUNK_SIZE)

        if year >= EXTENDED_SCHEMA_YEAR:
            df["defuncion_id"] = df["id"]
            extras = self._to_records(df, StgDefuncionesAmpliacion.columns())
            bulk_insert(session, extras, StgDefuncionesAmpliacion, chunk_size=settings.CHUNK_SIZE)
            self.logger.info(f"[action] {year}: {len(extras):,} filas de ampliación")

        self.logger.info(f"[action] {year}: {len(facts):,} defunciones cargadas")
        return len(facts)

    @staticmethod
    def _to_records(df: pd.DataFrame, columns: list[str]) -> list[dict]:
        """`pd.NA` de los tipos nullable no lo convierte `replace`; hay que enmascarar."""
        frame = df.reindex(columns=columns)
        return frame.astype(object).where(frame.notna(), None).to_dict("records")

    def finalization(self, input_data: dict[str, int]) -> dict[str, int]:
        with self.db.get_session() as session:
            sync_id_sequence(session, StgDefunciones)
            session.commit()
        self.db.disconnect()
        self.logger.info(f"[finalization] {input_data['defunciones']:,} defunciones en total")
        return input_data
