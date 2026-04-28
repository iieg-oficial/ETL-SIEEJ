---
name: estructura-pipeline
description: Genera la estructura de carpetas y archivos vacíos/plantilla para un nuevo pipeline ETL siguiendo la convención del proyecto.
---

## Cuándo usar

Al iniciar un nuevo pipeline (Fase 0 → 1 de `refactor.md`), después de que el usuario confirmó el nombre y la fuente.

## Estructura a crear

Reemplazar `{flujo}` por el nombre del pipeline (snake_case, sin acentos).

```
core/pipelines/{flujo}/
├── __init__.py
├── config.py
├── constants.py
├── attributes.py            # o attributes/{__init__,base,{flujo}}.py si hay múltiples enums
├── mappings.py              # catálogos estáticos (id → label)
├── helpers.py               # helpers locales del pipeline (opcional)
├── schemas.py               # SQLAlchemy 2.0
├── .env.example             # variables del pipeline
├── README.md                # generado por skill docs-pipeline
├── assets/
│   └── erd.png              # generado por eralchemy2
├── eda/
│   └── reporte_{nombre}.py  # scripts EDA
└── stages/
    ├── __init__.py
    ├── extract.py
    ├── transform.py
    └── load.py

migrations/{flujo}/
├── flyway.conf.example
└── sql/
    ├── V1__foreign_tables.sql
    ├── V2__catalogs_{flujo}.sql       # solo si hay catálogos
    ├── V3__tables_{flujo}.sql
    └── V4__views_{flujo}.sql

dags/etl_{flujo}.py
```

## Reglas

- `attributes.py` plano cuando hay un único enum. Carpeta `attributes/` cuando hay múltiples (base + por dominio).
- Nunca declarar constantes fuera de `constants.py`.
- `assets/`, `eda/` se crean vacíos al inicio; el ERD y los reportes EDA se generan en sus fases.
- Si el pipeline es no-iterable, `dags/etl_{flujo}.py` debe quedar con `schedule=None` por default.
- Crear todos los `__init__.py` necesarios.

## Output

Lista de archivos creados con un breve comentario de qué contendrán cada uno. **No** llenar los archivos en este paso; esa labor corresponde a los skills `esquema-db`, `sqlalchemy-models`, `dag-airflow`, etc.
