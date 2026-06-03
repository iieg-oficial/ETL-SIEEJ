---
name: dag-airflow
description: Use when generating the Airflow DAG file for a pipeline with bootstrap and update flows.
---

# Skill: DAG Airflow

## Purpose
Use this skill during ETL implementation to generate the DAG file for Airflow 3.x.

## Steps

1. Define `dag_id` values as `etl_{flujo}_bootstrap` and `etl_{flujo}_update`.
2. Configure `schedule_interval` from the approved frequency (`None` for bootstrap, cron for update).
3. Define separate `default_args` for bootstrap and update.
4. Create `run_bootstrap()` and `run_update()` to instantiate `Pipeline` with the correct stages.
5. Chain the stages as `extract >> transform >> load`.
6. Add `main()` for local bootstrap execution without Airflow.
7. Use the established import-resolution pattern at the top of the file.
8. Save the result to `./dags/etl_{flujo}.py`.

## Template

See `template.py` in this folder.
