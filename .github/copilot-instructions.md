---
name: copilot-instructions
description: Always-on instructions for the ETL SIEEJ project.
---

# ETL SIEEJ — Copilot Instructions

## Project Overview

**ETL SIEEJ** is the data pipeline system for the _Sistema de Información Estratégica del Estado de Jalisco_, developed by IIEG (Instituto de Información Estadística y Geográfica de Jalisco). It ingests data from public sources, transforms them using pipeline-specific business rules, and loads them into a PostgreSQL/PostGIS database for analysis and consumption.

Each pipeline runs in two modes:
- **`bootstrap`** — full historical load (first load or full rebuild).
- **`update`** — incremental load on a cron schedule.

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Orchestration | Apache Airflow (CeleryExecutor) | 3.x |
| Language | Python | 3.12 |
| Database | PostgreSQL + PostGIS | 17 |
| ORM | SQLAlchemy | 2.x |
| Migrations | Flyway | latest |
| Data processing | Pandas | 2.x |
| Config/validation | pydantic-settings | 2.x |
| Linter | Ruff | `line-length = 120` |
| Task runner | just | latest |
| Containers | Docker + Docker Compose | ≥ 20.10 |

---

## Global Rules

### Python Environment
**Always use the conda `etl` environment (Python 3.12) to run any Python script.** Activate it before running:

```bash
conda activate etl
python dags/etl_{flujo}.py
```

Or invoke the interpreter directly:

```bash
conda run -n etl python dags/etl_{flujo}.py
```

Never use system `python` or `python3` without verifying it belongs to the `etl` environment.

---

## Justfile Automations

The `justfile` centralizes all repetitive tasks for development, Docker, and Flyway. **Always check `just --list` first** — it shows every available recipe with its description and parameters before writing custom shell commands.

```bash
just --list   # show all available recipes
```

Key recipe groups:

| Group | Recipe | Description |
|-------|--------|-------------|
| **development** | `just build-dev` | Spin up a local PostGIS container for testing (default: user/pass/db = `test`, port `5432`) |
| | `just create-cvegeo-db` | Create and seed the `cvegeo` database (required before pipelines that use geographic codes) |
| | `just setup` | Install pre-commit hooks after cloning the repo |
| | `just stop-dev` | Stop and remove the local dev container |
| **docker** | `just up` | Start all Docker Compose services (Airflow stack) |
| | `just down` | Stop all services |
| | `just down-volumes` | Stop all services and remove volumes (destructive) |
| | `just ps` | Show status of running services |
| | `just logs [service]` | Tail logs for a service |
| | `just restart <service>` | Restart a specific service |
| | `just rebuild <service>` | Rebuild and restart a specific service |
| **flyway** | `just flyway-config <pipeline>` | Copy `flyway.conf.example` → `flyway.conf` for a pipeline |
| | `just flyway-migrate <pipeline>` | Apply pending migrations for a pipeline |
| | `just flyway-info <pipeline>` | Show migration status |
| | `just flyway-validate <pipeline>` | Validate applied migrations against scripts |
| | `just flyway-clean <pipeline>` | Drop all objects managed by Flyway (destructive) |
| | `just flyway-reset <pipeline>` | Clean + migrate (full rebuild of schema) |
