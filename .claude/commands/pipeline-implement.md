---
description: Implementa stages Extract/Transform/Load y el DAG Airflow del pipeline.
argument-hint: '[nombre del pipeline]'
---

> Use el agente `etl-agent`.

Implementa los stages y DAG del pipeline:

- **Pipeline:** {{flujo}}
- **Iterable (sí/no) + parámetro:** {{iterable}}
- **Schedule del DAG:** {{schedule}}

Inputs disponibles: reporte EDA aprobado, `schemas.py`, migraciones aplicadas.

Entregables:
- `core/pipelines/{{flujo}}/{config,constants,mappings,helpers}.py`.
- `core/pipelines/{{flujo}}/stages/{extract,transform,load}.py`.
- `core/pipelines/{{flujo}}/.env.example` con todas las variables nuevas.
- `dags/etl_{{flujo}}.py` con función `main()` para pruebas locales.
- Smoke local: `python dags/etl_{{flujo}}.py` corre en bootstrap sin errores.

Aplica skills `dag-airflow` y `estructura-pipeline`. Reglas heredadas de [.github/instructions/python-rules.instructions.md](../instructions/python-rules.instructions.md) y [.github/instructions/bootstrap-update-rules.instructions.md](../instructions/bootstrap-update-rules.instructions.md).
