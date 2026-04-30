---
name: estructura-pipeline
description: Crea la estructura de carpetas y archivos base para un nuevo pipeline ETL en el proyecto.
---

# Skill: Estructura de Pipeline

## Purpose
Invocar al inicio del desarrollo (Fase 0 y Fase 5) para generar el esqueleto completo del pipeline antes de escribir cualquier lógica.

## Steps

1. Crear la carpeta raíz del pipeline: `./core/pipelines/{flujo}/`
2. Crear las subcarpetas: `eda/`, `stages/`, `helpers/`, `assets/`
3. Crear los archivos base vacíos: `__init__.py`, `attributes.py`, `schemas.py`, `constants.py`, `config.py`, `.env.example`
4. Crear `__init__.py` vacío en cada subcarpeta.
5. Crear la carpeta de migraciones: `./migrations/{flujo}/sql/` y copiar un `flyway.conf.example` desde otro pipeline como referencia.
6. Confirmar la estructura generada listando el árbol de archivos antes de continuar.

## Template

Árbol esperado al finalizar el pipeline completo:

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

> **Nota:** Algunos pipelines legacy usan `consts.py` en lugar de `constants.py`. Los nuevos pipelines deben usar `constants.py`.
