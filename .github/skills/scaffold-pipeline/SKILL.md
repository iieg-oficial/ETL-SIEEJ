---
name: scaffold-pipeline
description: Templates completos de código para un pipeline ETL SIEEJ nuevo. Incluye boilerplate de config.py, consts.py, schemas.py, los tres stages (extract/transform/load), DAG dual, .env.example y estructura de carpetas. Úsalo cuando necesites crear un pipeline desde cero o agregar un stage nuevo.
argument-hint: <nombre_pipeline> [fuente=http|drive]
---

# Skill: Scaffold Pipeline ETL

Fuente única de templates para un pipeline nuevo. Las instrucciones de cómo/cuándo aplicar estos templates están en los agentes (`etl`, `db`) y en las instructions (`airflow`, `db`). Este skill **solo provee los moldes**.

## Placeholders

- `{nombre}` → snake_case (ej: `empleo_formal`)
- `{Nombre}` → PascalCase (ej: `EmpleoFormal`)
- `{NOMBRE}` → UPPER_SNAKE_CASE (ej: `EMPLEO_FORMAL`)
- `{pipeline}` == `{nombre}` (alias usado en SQL/tablas)

## Estructura de carpetas

```
core/pipelines/{nombre}/
├── __init__.py                    (vacío)
├── config.py
├── consts.py
├── schemas.py
├── .env.example
└── stages/
    ├── __init__.py                (vacío)
    ├── extract.py
    ├── transform.py
    └── load.py

migrations/{nombre}/
├── flyway.conf.example
└── sql/
    ├── V1__catalogos.sql          (ver skill generate-migration)
    ├── V2__cvegeo.sql             (si aplica, ver skill cvegeo-integration)
    ├── V3__tabla_principal.sql
    └── V4__vista.sql

dags/etl_{nombre}.py
core/pipelines/{nombre}/README.md  (ver skill pipeline-readme)
```

---

## Template: `core/pipelines/{nombre}/config.py`

```python
from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("{nombre}"))

    # Base de datos del pipeline
    {NOMBRE}_DB_HOST: str = Field(default="localhost")
    {NOMBRE}_DB_PORT: int = Field(default=5432)
    {NOMBRE}_DB_USER: str = Field(default="test")
    {NOMBRE}_DB_PASS: str = Field(default="test")
    {NOMBRE}_DB_NAME: str = Field(default="{nombre}")

    # Fuente de datos
    {NOMBRE}_SOURCE_URL: str = Field(default="")

    # Carga
    {NOMBRE}_LOAD_BATCH_SIZE: int = Field(default=5000)


settings = Settings()
```

---

## Template: `core/pipelines/{nombre}/consts.py`

```python
PIPELINE_NAME = "{nombre}"

# Strings que representan nulos en la fuente
NULL_VALUES: list[str] = ["NO APLICA", "NA", "N/A", "null", "nan", ""]

# Mapa de columnas originales → nombres internos (snake_case)
COLUMN_RENAME_MAP: dict[str, str] = {
    # "Nombre Original": "nombre_interno",
}

# Columnas de fecha (se parsean en transform)
DATE_COLUMNS: list[str] = []

# Columnas de catálogo dinámico (se sincronizan en load)
CATALOG_COLUMNS: list[str] = []

# Municipios que NO deben resolverse contra cvegeo (solo si requiere_cvegeo)
# SKIP_MUNICIPALITY_VALUES = frozenset({"SE IGNORA", "EXTRANJERO"})

# Columnas (municipio, estado, id_destino) para resolución cvegeo (solo si aplica)
# MUNICIPALITY_COLUMNS = [("municipio", "estado", "municipio_id")]

# Campos determinísticos para record_hash (solo SCD2 — ver skill scd2-pattern)
# HASH_FIELDS: list[str] = []
```

---

## Template: `core/pipelines/{nombre}/schemas.py`

```python
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Index, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class {Nombre}Base(DeclarativeBase):
    pass


# ----- Catálogos -----

class Cat{Ejemplo}({Nombre}Base):
    __tablename__ = "stg_{nombre}_cat_{ejemplo}"
    __table_args__ = (UniqueConstraint("name", name="uq_{nombre}_cat_{ejemplo}_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)


# ----- Tabla principal -----

class {Nombre}Data({Nombre}Base):
    __tablename__ = "stg_{nombre}_datos"
    __table_args__ = (
        UniqueConstraint("llave_natural", name="uq_{nombre}_datos_llave"),
        Index("ix_{nombre}_datos_llave", "llave_natural", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    llave_natural: Mapped[str] = mapped_column(String(64), unique=True)
    cat_{ejemplo}_id: Mapped[int]
    # municipio_id: Mapped[Optional[int]]       # solo si cvegeo
    # record_hash: Mapped[str] = mapped_column(String(64))  # solo SCD2
    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now(), onupdate=func.now())


# Registro de catálogos para iteración dinámica en load.py
CATALOG_MODELS: dict[str, type] = {
    "{ejemplo}": Cat{Ejemplo},
}
```

Ejemplos de referencia: `core/pipelines/repd/schemas.py` (SCD2 + catálogos), `core/pipelines/fiscalia/schemas.py` (catálogos mixtos).

---

## Template: `core/pipelines/{nombre}/stages/extract.py` — Fuente HTTP

```python
from datetime import datetime
from typing import Any, Optional

import requests

from core.pipelines.{nombre}.config import settings
from core.pipelines.{nombre}.consts import PIPELINE_NAME
from core.pipelines.stage import Stage


class {Nombre}Extractor(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "extract")
        self.mode = mode

    def source(self, input_data: Optional[Any] = None) -> dict:
        url = settings.{NOMBRE}_SOURCE_URL
        if not url:
            raise ValueError("{NOMBRE}_SOURCE_URL no configurada")
        self.logger.info(f"Fuente: {url}")
        return {"url": url}

    def action(self, input_data: Optional[Any] = None) -> dict:
        url = input_data["url"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.work_dir / f"{PIPELINE_NAME}_{timestamp}.xlsx"

        response = requests.get(url, timeout=180)
        response.raise_for_status()
        if not response.content:
            raise ValueError("Respuesta vacía")

        output_path.write_bytes(response.content)
        self.logger.info(f"Descargado: {output_path}")
        return {"file_path": str(output_path)}

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        self.logger.info(f"Extracción completa: {input_data['file_path']}")
        return input_data
```

### Variante: Fuente Google Drive

Ver `core/pipelines/fiscalia/stages/extract.py` — usa `core.utils.gdrive` con credenciales en `GDRIVE_CREDENTIALS_PATH` y `GDRIVE_FOLDER_ID`.

---

## Template: `core/pipelines/{nombre}/stages/transform.py`

```python
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.{nombre}.consts import (
    CATALOG_COLUMNS,
    COLUMN_RENAME_MAP,
    DATE_COLUMNS,
    NULL_VALUES,
    PIPELINE_NAME,
)
from core.pipelines.stage import Stage
from core.utils.clean import list_values_to_null
from core.utils.files import clean_directory
from core.utils.normalize import normalize_col, uppercase_col
from core.utils.parse_datetime import parse_month_year


class {Nombre}Transformer(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "transform")
        self.mode = mode

    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data or not input_data.get("file_path"):
            raise ValueError("Transform no recibió archivo de Extract")
        return input_data

    def action(self, input_data: Optional[Any] = None) -> dict:
        file_path = input_data["file_path"]

        # Ajustar según EDA: sheet_name, header, encoding, etc.
        df = pd.read_excel(file_path, sheet_name=0, header=0, dtype=str)
        self.logger.info(f"Leídos {len(df)} registros, {len(df.columns)} columnas")

        # Normalizar headers a snake_case
        tmp = pd.DataFrame({"c": df.columns.str.strip()})
        df.columns = normalize_col(tmp, "c").values
        df = df.rename(columns=COLUMN_RENAME_MAP)

        # Limpieza de nulos
        df = list_values_to_null(df, rm_list=NULL_VALUES)

        # Parseo de fechas
        for col in DATE_COLUMNS:
            if col in df.columns:
                df[col] = df[col].apply(parse_month_year)

        # Normalización geográfica (si aplica)
        for col in ("estado", "municipio"):
            if col in df.columns:
                uppercase_col(df, col)

        # Extracción de catálogos
        catalogs: dict[str, list[str]] = {}
        for col in CATALOG_COLUMNS:
            if col in df.columns:
                catalogs[col] = sorted(df[col].dropna().unique().tolist())

        # Sanitizar NaN/NaT residuales → None
        df = df.where(pd.notna(df), other=None)

        return {"df": df, "catalogs": catalogs, "row_count": len(df)}

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        clean_directory(Path(f"data/extract/{PIPELINE_NAME}"), self.logger)
        clean_directory(self.work_dir, self.logger)
        return input_data
```

---

## Template: `core/pipelines/{nombre}/stages/load.py` — Insert/Upsert simple

Para pipelines **sin SCD2**. Si requieres SCD2 consulta el skill `scd2-pattern`.

```python
from typing import Any, Optional

import pandas as pd

from core.db import Database
from core.pipelines.{nombre}.config import settings
from core.pipelines.{nombre}.consts import PIPELINE_NAME
from core.pipelines.{nombre}.schemas import CATALOG_MODELS, {Nombre}Base, {Nombre}Data
from core.pipelines.stage import Stage
from core.utils.bulk_ops import bulk_insert, get_mapping, insert_records, sync_id_sequence
from core.utils.files import clean_directory


class {Nombre}Loader(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode
        self.db: Optional[Database] = None

    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data:
            raise ValueError("Load no recibió datos de Transform")
        self.db = Database(PIPELINE_NAME, settings.database_url)
        self.db.connect()
        {Nombre}Base.metadata.create_all(self.db.engine)
        return input_data

    def action(self, input_data: Optional[Any] = None) -> dict:
        df: pd.DataFrame = input_data["df"]
        catalogs: dict[str, list[str]] = input_data["catalogs"]

        with self.db.get_session() as session:
            # 1) Sincronizar catálogos y construir mapas name → id
            cat_maps: dict[str, dict[str, int]] = {}
            for col, model in CATALOG_MODELS.items():
                if col in catalogs:
                    insert_records(session, model, [{"name": v} for v in catalogs[col]])
                    cat_maps[col] = get_mapping(session, model, "name", "id")

            # 2) Resolver IDs de catálogos en el DataFrame
            for col, mapping in cat_maps.items():
                df[f"{col}_id"] = df[col].map(mapping)

            # 3) Insertar datos principales
            records = df.to_dict("records")
            bulk_insert(
                session,
                {Nombre}Data,
                records,
                batch_size=settings.{NOMBRE}_LOAD_BATCH_SIZE,
            )

            # 4) Sincronizar secuencias SERIAL
            sync_id_sequence(session, {Nombre}Data)

        return {"row_count": len(df)}

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        clean_directory(self.work_dir, self.logger)
        if self.db:
            self.db.close()
        return input_data
```

Para integración cvegeo, agregar resolución de municipios antes del `bulk_insert` — ver skill `cvegeo-integration`.

---

## Template: `dags/etl_{nombre}.py`

```python
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from core.pipeline import Pipeline
from core.pipelines.{nombre}.stages.extract import {Nombre}Extractor
from core.pipelines.{nombre}.stages.transform import {Nombre}Transformer
from core.pipelines.{nombre}.stages.load import {Nombre}Loader


def run_bootstrap():
    Pipeline(
        name="{nombre}",
        stages=[
            {Nombre}Extractor(mode="bootstrap"),
            {Nombre}Transformer(mode="bootstrap"),
            {Nombre}Loader(mode="bootstrap"),
        ],
    ).run(mode="bootstrap")


def run_update():
    Pipeline(
        name="{nombre}",
        stages=[
            {Nombre}Extractor(mode="update"),
            {Nombre}Transformer(mode="update"),
            {Nombre}Loader(mode="update"),
        ],
    ).run(mode="update")


with DAG(
    "etl_{nombre}_bootstrap",
    default_args={"owner": "iieg", "retries": 1, "retry_delay": timedelta(minutes=10)},
    description="{Nombre} Bootstrap — Carga inicial completa (on demand)",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    schedule=None,
    tags=["etl", "{nombre}", "bootstrap", "on-demand"],
) as dag_bootstrap:
    PythonOperator(task_id="run_bootstrap", python_callable=run_bootstrap)


with DAG(
    "etl_{nombre}_update",
    default_args={"owner": "iieg", "retries": 2, "retry_delay": timedelta(minutes=5)},
    description="{Nombre} Update — Carga incremental",
    schedule="0 3 1 * *",   # ajustar según periodicidad del EDA
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["etl", "{nombre}", "update"],
) as dag_update:
    PythonOperator(task_id="run_update", python_callable=run_update)


if __name__ == "__main__":
    run_bootstrap()
```

**Si la periodicidad > 3 meses o es única**: omitir el bloque `dag_update` y dejar solo el bootstrap.

---

## Template: `core/pipelines/{nombre}/.env.example`

```env
# ====================================================================
# {NOMBRE} — Variables de entorno (copiar a .env y completar)
# ====================================================================

# Base de datos
{NOMBRE}_DB_HOST=localhost           # Docker: host.docker.internal
{NOMBRE}_DB_PORT=5432
{NOMBRE}_DB_USER=tu_usuario
{NOMBRE}_DB_PASS=tu_password
{NOMBRE}_DB_NAME={nombre}

# Fuente de datos
{NOMBRE}_SOURCE_URL=https://ejemplo.com/datos.xlsx

# Carga
{NOMBRE}_LOAD_BATCH_SIZE=5000

# Google Drive (solo si aplica)
# GDRIVE_CREDENTIALS_PATH=/ruta/credentials.json
# GDRIVE_FOLDER_ID=tu_folder_id
```

---

## Template: `migrations/{nombre}/flyway.conf.example`

```properties
flyway.url=jdbc:postgresql://localhost:5432/{nombre}
flyway.user=
flyway.password=
flyway.schemas=public
flyway.locations=filesystem:migrations/{nombre}/sql
flyway.outOfOrder=false
flyway.validateOnMigrate=true
flyway.cleanDisabled=false
```

---

## Checklist de scaffold

- [ ] Reemplazar todos los `{nombre}`, `{Nombre}`, `{NOMBRE}` por los valores reales
- [ ] Ajustar `read_excel`/`read_csv` según lo detectado en el EDA (sheet, header, encoding)
- [ ] Completar `COLUMN_RENAME_MAP`, `DATE_COLUMNS`, `CATALOG_COLUMNS` desde el EDA
- [ ] Si requiere cvegeo → aplicar skill `cvegeo-integration`
- [ ] Si requiere SCD2 → aplicar skill `scd2-pattern`
- [ ] Generar migraciones con skill `generate-migration`
- [ ] Generar README con skill `pipeline-readme`

## Referencias del proyecto

- `core/pipelines/repd/` — SCD2 + cvegeo + catálogos dinámicos (template canónico)
- `core/pipelines/fiscalia/` — Google Drive + catálogos mixtos
- `core/pipelines/censos_economicos/` — múltiples años con config dinámica
- `core/utils/bulk_ops.py` — operaciones de inserción
- `core/utils/{clean,normalize,parse_datetime}.py` — utilidades de transformación
