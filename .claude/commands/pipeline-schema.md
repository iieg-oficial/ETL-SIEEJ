---
description: Diseña o ajusta el esquema de base de datos (migraciones V1-V4 + schemas.py)
  a partir del reporte EDA.
argument-hint: '[nombre del pipeline]'
---

> Use el agente `db-agent`.

Diseña el esquema de BD para el pipeline:

- **Pipeline:** {{flujo}}
- **Filtrar Jalisco (cve_ent = 14):** {{jalisco}}
- **Variante de update (append / scd2):** {{variante}}

Inputs disponibles: `core/pipelines/{{flujo}}/eda/reporte_*.json`.

Entregables:
- Migraciones V1-V4 en `migrations/{{flujo}}/sql/`.
- `core/pipelines/{{flujo}}/attributes.py` y `schemas.py`.
- ERD en `core/pipelines/{{flujo}}/assets/erd.png`.
- Salida de `just flyway-info {{flujo}}` confirmando aplicación.

Aplica los skills `esquema-db` y `sqlalchemy-models`. Reglas heredadas de [.github/instructions/database-rules.instructions.md](../instructions/database-rules.instructions.md).
