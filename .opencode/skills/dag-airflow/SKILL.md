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
8. Set `max_active_runs=1` on every DAG object — no DAG may allow overlapping runs of itself.
9. Consult the heavy-pipeline criterion (`docs/airflow.md` — "Pipelines pesados") to decide pool assignment: if the pipeline trips any signal (fan-out > ~20 task instances, peak memory > ~25% of the scheduler's `mem_limit`, single extract payload > ~500 MB, or full run duration > ~30 min), assign `pool=POOL_HEAVY` and `priority_weight=PRIORITY_HEAVY` / `weight_rule="absolute"` from `core.constants.concurrency` to every task. Otherwise omit `pool=` entirely.
10. Save the result to `./dags/etl_{flujo}.py`.

## Template

See `template.py` in this folder.
