---
name: pipeline-schema
description: Diseña o ajusta el esquema de base de datos (migraciones V1-V4 + schemas.py) a partir del reporte EDA.
agent: db-agent
argument-hint: "[nombre del pipeline]"
---

Diseña el esquema de BD para el pipeline:

- **Pipeline:** ${input:flujo}
- **Filtrar Jalisco (cve_ent = 14):** ${input:jalisco}
- **Variante de update (append / scd2):** ${input:variante}

Inputs disponibles: `core/pipelines/${input:flujo}/eda/reporte_*.json`.

Entregables:
- Migraciones V1-V4 en `migrations/${input:flujo}/sql/`.
- `core/pipelines/${input:flujo}/attributes.py` y `schemas.py`.
- ERD en `core/pipelines/${input:flujo}/assets/erd.png`.
- Salida de `just flyway-info ${input:flujo}` confirmando aplicación.

Aplica los skills `esquema-db` y `sqlalchemy-models`. Reglas heredadas de [.github/instructions/database-rules.instructions.md](../instructions/database-rules.instructions.md).
