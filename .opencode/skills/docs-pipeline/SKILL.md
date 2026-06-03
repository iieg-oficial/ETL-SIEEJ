---
name: docs-pipeline
description: Use when generating the internal pipeline README from implemented artifacts.
---

# Skill: Pipeline Documentation

## Purpose
Use this skill during the documentation phase to build the pipeline `README.md`.

## Steps

1. Read `./core/pipelines/{flujo}/eda/reporte_eda.json` for source details.
2. Read the `V1` to `V4` migrations in `./migrations/{flujo}/sql/` to document the schema and tables.
3. Read `./dags/etl_{flujo}.py` to document the DAG name, schedule, and stage order.
4. Read `./core/pipelines/{flujo}/.env.example` to list required environment variables.
5. Include the ER diagram from `./core/pipelines/{flujo}/assets/er_{flujo}.png` when it exists.
6. Build the README using `template.md` in this folder.
7. Save it to `./core/pipelines/{flujo}/README.md`.

## Template

See `template.md` in this folder.
