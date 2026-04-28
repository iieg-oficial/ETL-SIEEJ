---
name: pipeline-implement
description: Implementa stages Extract/Transform/Load y el DAG Airflow del pipeline.
agent: etl-agent
argument-hint: "[nombre del pipeline]"
---

Implementa los stages y DAG del pipeline:

- **Pipeline:** ${input:flujo}
- **Iterable (sí/no) + parámetro:** ${input:iterable}
- **Schedule del DAG:** ${input:schedule}

Inputs disponibles: reporte EDA aprobado, `schemas.py`, migraciones aplicadas.

Entregables:
- `core/pipelines/${input:flujo}/{config,constants,mappings,helpers}.py`.
- `core/pipelines/${input:flujo}/stages/{extract,transform,load}.py`.
- `core/pipelines/${input:flujo}/.env.example` con todas las variables nuevas.
- `dags/etl_${input:flujo}.py` con función `main()` para pruebas locales.
- Smoke local: `python dags/etl_${input:flujo}.py` corre en bootstrap sin errores.

Aplica skills `dag-airflow` y `estructura-pipeline`. Reglas heredadas de [.github/instructions/python-rules.instructions.md](../instructions/python-rules.instructions.md) y [.github/instructions/bootstrap-update-rules.instructions.md](../instructions/bootstrap-update-rules.instructions.md).
