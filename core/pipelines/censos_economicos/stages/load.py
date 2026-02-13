import hashlib
import os
from datetime import datetime
from typing import Any, Optional

import pandas as pd
from sqlalchemy import text

from core.db import Database
from core.pipelines.censos_economicos.config import settings
from core.pipelines.censos_economicos.consts import (
    CE_ECONOMIC_COLUMNS,
    CLASSIFICATION_COLUMNS,
    KEY_COLUMNS,
    PIPELINE_NAME,
    classify_file_type,
)
from core.pipelines.censos_economicos.schemas import (
    CatCeCatalogoActividad,
    CatCeCatalogoEntidadMunicipio,
    CatCeCatalogoEstrato,
    CeBase,
    StgCeData,
    StgCeDiccionarioDatos,
    StgCeSourceFiles,
)
from core.pipelines.stage import Stage
from core.utils.bulk_ops import insert_records, sync_id_sequence
from core.utils.clean import list_values_to_null
from core.utils.normalize import lowercase_headers


class CELoader(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode
        self.db: Database | None = None

    def source(self, input_data: Optional[Any] = None) -> dict:
        """Conecta a la base de datos y crea las tablas."""
        if not input_data:
            raise ValueError("La etapa Load no recibio datos de Transform.")

        self.db = Database(PIPELINE_NAME, settings.database_url)
        self.db.connect()

        CeBase.metadata.create_all(self.db.engine)
        self.logger.info("Tablas de base de datos creadas/verificadas.")

        return input_data

    def action(self, input_data: Optional[Any] = None) -> dict:
        """Carga catalogos y CSVs de datos en PostgreSQL."""
        catalogs_by_year = input_data["catalogs"]
        data_entries = input_data["data_entries"]
        stats: dict[str, Any] = {"catalogs": {}, "data": {}, "source_files": 0}

        # 1. Cargar catalogos
        for year, year_catalogs in catalogs_by_year.items():
            year_stats = {}

            if "actividad" in year_catalogs:
                with self.db.get_session() as session:
                    insert_records(session, year_catalogs["actividad"], CatCeCatalogoActividad, ["codigo"])
                year_stats["actividad"] = len(year_catalogs["actividad"])
                self.logger.info(f"Cargados {len(year_catalogs['actividad'])} codigos de actividad para el anio {year}.")

            if "entidad_municipio" in year_catalogs:
                with self.db.get_session() as session:
                    insert_records(
                        session, year_catalogs["entidad_municipio"], CatCeCatalogoEntidadMunicipio, ["cvegeo"]
                    )
                year_stats["entidad_municipio"] = len(year_catalogs["entidad_municipio"])
                self.logger.info(
                    f"Cargadas {len(year_catalogs['entidad_municipio'])} entradas geograficas para el anio {year}."
                )

            if "estrato" in year_catalogs:
                with self.db.get_session() as session:
                    insert_records(session, year_catalogs["estrato"], CatCeCatalogoEstrato, ["id_estrato"])
                year_stats["estrato"] = len(year_catalogs["estrato"])
                self.logger.info(f"Cargadas {len(year_catalogs['estrato'])} entradas de estrato para el anio {year}.")

            if "diccionario" in year_catalogs:
                with self.db.get_session() as session:
                    insert_records(
                        session, year_catalogs["diccionario"], StgCeDiccionarioDatos, ["year", "column_name"]
                    )
                year_stats["diccionario"] = len(year_catalogs["diccionario"])
                self.logger.info(f"Cargadas {len(year_catalogs['diccionario'])} entradas de diccionario para el anio {year}.")

            stats["catalogs"][year] = year_stats

        # 2. Cargar CSVs de datos
        for entry in data_entries:
            year = entry["year"]
            slug = entry["slug"]
            data_csv = entry["data_csv"]
            slug_dir = entry["slug_dir"]
            url = entry["url"]

            self.logger.info(f"Cargando datos de {year}/{slug} desde {data_csv}")

            try:
                row_count = self._load_data_csv(data_csv, year)
                self._record_source_files(entry, "loaded", row_count=row_count)
                stats["data"][f"{year}/{slug}"] = row_count
                self.logger.info(f"Cargadas {row_count} filas para {year}/{slug}.")

            except Exception as e:
                self.logger.error(f"Error al cargar {year}/{slug}: {e}")
                self._record_source_files(entry, "error", error_message=str(e))
                raise

        return stats

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        """Sincroniza secuencias de ID y desconecta."""
        stats = input_data

        all_models = [
            CatCeCatalogoActividad,
            CatCeCatalogoEntidadMunicipio,
            CatCeCatalogoEstrato,
            StgCeDiccionarioDatos,
            StgCeSourceFiles,
            StgCeData,
        ]

        with self.db.get_session() as session:
            for model in all_models:
                try:
                    sync_id_sequence(session, model)
                except Exception as e:
                    self.logger.warning(f"Error al sincronizar secuencia para {model.__tablename__}: {e}")

        self.db.disconnect()
        self.logger.info("Base de datos desconectada. Etapa Load completa.")
        return stats

    def _load_data_csv(self, csv_path: str, year: int) -> int:
        """Lee, limpia e inserta por lotes un CSV de datos individual."""
        df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
        lowercase_headers(df)
        df.columns = df.columns.str.strip()
        df = list_values_to_null(df)

        # Agregar columna de anio
        df["year"] = year

        # Columnas clave: cadena vacia para valores faltantes/None
        for col in KEY_COLUMNS:
            if col in df.columns:
                df[col] = df[col].fillna("").astype(str).str.strip()
            else:
                df[col] = ""

        # Columnas de clasificacion: None para valores faltantes/vacios
        for col in CLASSIFICATION_COLUMNS:
            if col in df.columns:
                df[col] = df[col].where(df[col].notna() & (df[col] != ""), None)
            else:
                df[col] = None

        # Columnas economicas: convertir a float, no numerico -> None (NULL = dato confidencial)
        for col in CE_ECONOMIC_COLUMNS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            else:
                df[col] = None

        # Desfragmentar despues de operaciones columna por columna
        df = df.copy()

        # Derivar cvegeo de e03 + e04
        df["cvegeo"] = df.apply(lambda row: (row["e03"] + row["e04"]) if row["e03"] and row["e04"] else None, axis=1)

        # Seleccionar columnas de salida
        output_cols = ["year"] + KEY_COLUMNS + CLASSIFICATION_COLUMNS + ["cvegeo"] + CE_ECONOMIC_COLUMNS
        available_cols = [c for c in output_cols if c in df.columns]
        df = df[available_cols]

        # Insercion por lotes con SQL crudo para rendimiento
        col_list = ", ".join(available_cols)
        placeholders = ", ".join([f":{c}" for c in available_cols])
        upsert_sql = text(
            f"INSERT INTO stg_ce_data ({col_list}) VALUES ({placeholders}) "
            f"ON CONFLICT ON CONSTRAINT uq_stg_ce_data_natural_key DO NOTHING"
        )

        batch_size = settings.CE_LOAD_BATCH_SIZE
        total_inserted = 0

        for start in range(0, len(df), batch_size):
            batch = df.iloc[start : start + batch_size]
            records = batch.astype(object).where(batch.notna(), None).to_dict("records")

            with self.db.get_session() as session:
                result = session.execute(upsert_sql, records)
                total_inserted += result.rowcount

        return total_inserted

    def _record_source_files(
        self,
        entry: dict,
        status: str,
        row_count: int | None = None,
        error_message: str | None = None,
    ) -> None:
        """Registra metadatos del archivo fuente en stg_ce_source_files."""
        year = entry["year"]
        slug = entry["slug"]
        slug_dir = entry["slug_dir"]
        url = entry["url"]
        data_csv = entry["data_csv"]

        # Calcular metadatos del archivo
        file_size = os.path.getsize(data_csv) if os.path.exists(data_csv) else None
        sha256 = None
        if os.path.exists(data_csv):
            h = hashlib.sha256()
            with open(data_csv, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            sha256 = h.hexdigest()

        rel_path = os.path.relpath(data_csv, slug_dir)

        record = {
            "year": year,
            "slug": slug,
            "filename": rel_path,
            "file_type": classify_file_type(rel_path),
            "file_path": os.path.abspath(data_csv),
            "file_size": file_size,
            "sha256": sha256,
            "source_url": url,
            "downloaded_at": datetime.utcnow(),
            "row_count": row_count,
            "status": status,
            "error_message": error_message,
            "loaded_at": datetime.utcnow() if status == "loaded" else None,
        }

        with self.db.get_session() as session:
            insert_records(session, [record], StgCeSourceFiles, ["year", "slug", "file_type"])
