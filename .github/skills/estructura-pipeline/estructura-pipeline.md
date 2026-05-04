---
name: estructura-pipeline
description: Use when creating the base folder structure and scaffold files for a new ETL pipeline.
---

# Skill: Pipeline Structure

## Purpose
Use this skill at the start of the workflow to scaffold the pipeline before implementation begins.

## Steps

1. Create the pipeline root folder: `./core/pipelines/{flujo}/`.
2. Create the `eda/`, `stages/`, `helpers/`, and `assets/` subfolders.
3. Create the base files: `__init__.py`, `attributes.py`, `schemas.py`, `constants.py`, `config.py`, and `.env.example`.
4. Create an empty `__init__.py` in each subfolder.
5. Create the migrations folder `./migrations/{flujo}/sql/` and copy a `flyway.conf.example` from another pipeline as reference.
6. Confirm the generated structure before continuing.

## Template

Expected tree once the pipeline is fully implemented:

```
core/pipelines/{flujo}/
├── __init__.py
├── attributes.py       # StrEnum de nombres de tabla: {Flujo}Tables(StrEnum) — OBLIGATORIO
├── config.py           # Pydantic-settings: variables de entorno del pipeline
├── constants.py        # Constantes UPPER_CASE del pipeline
├── mappings.py         # Dicts de lookup para catálogos (opcional, si hay valores fijos)
├── schemas.py          # Modelos SQLAlchemy (generado por DB Agent)
├── .env.example        # Variables de entorno requeridas (sin valores)
├── README.md           # Documentación interna (generado por DOCS Agent)
├── eda/
│   ├── __init__.py
│   ├── eda_{flujo}.py  # Script de análisis exploratorio
│   └── reporte_eda.json
├── stages/
│   ├── __init__.py
│   ├── extract.py
│   ├── transform.py
│   └── load.py
├── helpers/            # Funciones auxiliares específicas del pipeline
│   └── __init__.py
└── assets/
    └── er_{flujo}.png  # Diagrama ER (generado por DB Agent)

dags/
└── etl_{flujo}.py      # DAG de Airflow (bootstrap + update)

migrations/{flujo}/
├── flyway.conf
└── sql/
    # Con nivel geográfico (municipal/estatal):
    ├── V1__foreign_tables.sql       # FDW cvegeo — sin nombre de flujo en el archivo
    ├── V2__catalogs_{flujo}.sql     # Tablas cat_
    ├── V3__table_{flujo}.sql        # Tabla stg_
    └── V4__view_{flujo}.sql         # Vista v_
    # Sin nivel geográfico:
    ├── V1__catalogs_{flujo}.sql
    ├── V2__table_{flujo}.sql
    └── V3__view_{flujo}.sql
```

> **Note:** Some legacy pipelines use `consts.py` instead of `constants.py`. New pipelines must use `constants.py`.
