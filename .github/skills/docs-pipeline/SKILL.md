---
name: docs-pipeline
description: Genera el README interno de un pipeline con esquema, fuentes, metodología, variables y diagrama ER.
---

## Cuándo usar

Fase 7. Después del testing exitoso. Ejecutado por `docs-agent`.

## Pre-requisitos

- `schemas.py` final.
- Migraciones V1-V4 aplicadas y validadas.
- Stages implementados.
- DAG corrido en bootstrap.

## Salidas

- `core/pipelines/{flujo}/README.md`
- `core/pipelines/{flujo}/assets/erd.png` (regenerar siempre que `schemas.py` haya cambiado).

## Generar ERD

```python
from eralchemy2 import render_er

from core.pipelines.{flujo}.schemas import {Flujo}Base

render_er({Flujo}Base, "core/pipelines/{flujo}/assets/erd.png")
```

## Estructura del README

Todo en español. En este orden:

```markdown
# {DB_NAME}

Breve descripción del dominio del pipeline (1-2 oraciones).

## Fuente

- **Publicador**: {INEGI / Secretaría / etc.}
- **URL**: {url_principal}
- **Formato**: {csv / xlsx / api}
- **Encoding**: {utf-8 / iso-8859-1}
- **Cobertura geográfica**: {nacional / estatal / municipal}
- **Frecuencia de actualización**: {anual / mensual / on-demand}

## Esquema

<img src="assets/erd.png" width="600">

### Diccionario de variables

#### `stg_{principal}`

| Columna | Descripción |
|---|---|
| {col_no_obvia} | {descripción breve} |

(Solo columnas cuyo significado no es obvio. Omitir `id`, `nombre`, `fecha_actualizacion`.)

## Bootstrap y Update

- **Bootstrap**: {sí / no} — {breve cómo}.
- **Update**: {append / SCD2 / no aplica} — {periodicidad y disparador}.

## Diagrama de archivos

```
core/pipelines/{flujo}/
├── stages/{extract,transform,load}.py
├── schemas.py
├── attributes.py
├── constants.py
├── mappings.py
└── eda/
```

## Metodología

### Extract

{Breve: cómo descarga, qué filtros, dónde guarda el pickle.}

### Transform

{Breve: pasos de limpieza, normalización, build de catálogos, FKs resueltas.}

### Load

{Breve: orden de carga, estrategia (`bulk_insert` / `upsert_records`), conflict_keys.}

## Variables del .env

| Variable | Descripción | Ejemplo |
|---|---|---|
| `DB_NAME` | Nombre de la BD | `etl_{flujo}` |
| `URL_{NIVEL}` | URL fuente | `https://...` |

## Pasos manuales

1. Copiar `.env.example` a `.env` y completar.
2. `just up-database`
3. `just flyway-migrate {flujo}`
4. `python dags/etl_{flujo}.py` (bootstrap)
```

## Reglas

- Nombres de columna y tabla **idénticos** a `schemas.py`. Validarlo antes de escribir.
- No documentar lo que no esté verificado en código.
- Omitir secciones que no aplican (no dejar vacías).
- Sin emojis.
- Si la cobertura es Jalisco-only, mencionarlo en "Cobertura geográfica" y referenciar el filtro `cve_ent = 14` en la vista.
