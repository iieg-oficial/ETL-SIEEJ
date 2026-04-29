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
3. Crear los archivos base vacíos: `__init__.py`, `schemas.py`, `constants.py`, `config.py`, `.env.example`
4. Crear `__init__.py` vacío en cada subcarpeta.
5. Crear la carpeta de migraciones: `./migrations/{flujo}/sql/` y copiar un `flyway.conf.example` desde otro pipeline como referencia.
6. Confirmar la estructura generada listando el árbol de archivos antes de continuar.

## Template

Árbol esperado al finalizar el pipeline completo:

```
core/pipelines/{flujo}/
├── __init__.py
├── config.py           # Pydantic-settings: variables de entorno del pipeline
├── constants.py        # Constantes UPPER_CASE del pipeline
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
    ├── V1__{flujo}__catalogos.sql
    ├── V2__{flujo}__geo.sql        # Solo si hay nivel municipal/estatal
    ├── V3__{flujo}__tabla_principal.sql
    └── V4__{flujo}__vista.sql
```
