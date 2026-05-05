# ETL SIEEJ Copilot Instructions

This repository builds ETL pipelines for SIEEJ. Keep pipeline contracts, Flyway migrations, SQLAlchemy models, and Airflow DAGs aligned.

## Repository Defaults

- `.github` is the only active Copilot customization source in this repository. Ignore `.claude/` unless the task explicitly targets it.
- Use `conda run -n etl` for Python commands and local pipeline execution.
- Use `just --list` before inventing custom workflow commands.
- Prefer existing helpers in `core/` and `utils/` before adding new helpers.
- Keep internal customization guidance in English. User-facing GitHub templates may stay in Spanish.

## Responsibility Split

- DEA owns orchestration, approvals, issue creation, branch creation, commits, and pull requests.
- EDA owns source inspection and `reporte_eda.json`.
- DB owns migrations, `attributes.py`, `schemas.py`, and ER output.
- ETL owns stage implementation, DAG updates, `.env.example`, and bootstrap validation until the flow passes.
- DOCS owns `README.md` generation.

## Context Hygiene

- Treat `.claude/`, `data/`, `logs/`, `.ruff_cache/`, `config/airflow.cfg`, and `plugins/` as low-value context unless the task explicitly targets them.
- Prefer narrow local reads and searches over broad repository exploration.
