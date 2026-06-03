# ETL SIEEJ Instructions

This repository builds ETL pipelines for SIEEJ. Keep pipeline contracts, Flyway migrations, SQLAlchemy models, and Airflow DAGs aligned.

## Repository Defaults

- Use `conda run -n etl` for Python commands and local pipeline execution.
- Use `just --list` before inventing custom workflow commands.
- Prefer existing helpers in `core/` and `utils/` before adding new helpers.
- Keep internal customization guidance in English. User-facing GitHub templates may stay in Spanish.

## Context Hygiene

- Treat `data/`, `logs/`, `.ruff_cache/`, `config/airflow.cfg`, and `plugins/` as low-value context unless the task explicitly targets them.
- Prefer narrow local reads and searches over broad repository exploration.

## Responsibility Split

- **Data Engineer Agent (DEA)**: Owns orchestration, approvals, issue creation, branch creation, commits, and pull requests.
- **EDA Agent**: Owns source inspection and `reporte_eda.json`.
- **DB Agent**: Owns migrations, `attributes.py`, `schemas.py`, and ER output.
- **ETL Agent**: Owns stage implementation, DAG updates, `.env.example`, and bootstrap validation until the flow passes.
- **DOCS Agent**: Owns `README.md` generation.

## Python Instructions (applies to all Python files)

- Follow PEP8. Write atomic, reusable functions with English docstrings.
- Use strict typing for function arguments and return values.
- Handle exceptions explicitly with `try/except`. Use `logging`, never `print`.
- Keep imports at the top of the file in this order: standard library, third-party, local. Never import inside functions.
- Do not hardcode fixed values. Use `UPPER_CASE` constants defined in the pipeline `constants.py` or `consts.py`.
- Use `snake_case` for variables and functions, `PascalCase` for classes, and `UPPER_CASE` for constants.
- Before creating a new helper, check whether it already exists in `core/utils/`. If not, create it in the pipeline `helpers/` package.
- Keep files in UTF-8. Use `normalize_text` from `core/utils/normalize.py` for variable and column names. Do not use accents, `ñ`, or special characters in identifiers.
- Do not add decorative comments such as `#=== Title ===`. Keep comments short, precise, and in English.
- **Environment:** always use the `etl` conda environment (Python 3.12) for Python scripts. Activate `etl` or use `conda run -n etl`. Never use system `python` or `python3` unless you have verified it points to the `etl` environment.
- Add new dependencies to `requirements.txt` with pinned versions.
- Respect `line-length = 120` from `pyproject.toml` and run `ruff check` before each commit.
- Stage files must inherit from `core.pipeline.Stage` (ABC) and implement `source()`, `action()`, and `finalization()`.

## Database Instructions (applies to **/*.sql and **/schemas.py)

- Standardize column types: text to `VARCHAR(n)`, integer numeric values to `INT`, decimals to `FLOAT` or `NUMERIC(p,s)`, dates to `DATE`, and date-time values to `TIMESTAMP`.
- Standardize column names to Spanish `snake_case` without spaces, accents, or special characters. Use `normalize_text` as the reference transformation.
- Catalog tables use the `cat_` prefix. The main staging table uses the `stg_` prefix. Do not introduce other prefixes.
- Create tables only through versioned Flyway migrations. Validate them with `just migrate {flujo}` against the local Docker database.
- Use `just psql` or the commands defined in the `justfile` to inspect the database. Do not connect directly outside the Docker workflow.
- If a logic error exists in a versioned migration that has not reached production, fix the existing script instead of creating a patch migration.
- For municipality and state references, use the `cve_geo` database through the configured FDW. Do not duplicate those tables in the pipeline schema.
- Migration names must follow `V{n}__{flujo}__{descripcion}.sql` with double underscores.
- The pipeline `schemas.py` file must remain synchronized with the Flyway migrations. Every SQL table needs a corresponding SQLAlchemy model.
- Generate the ER diagram with ERAlchemy2 after applying migrations and save it to `./core/pipelines/{flujo}/assets/er_{flujo}.png`.

## EDA Instructions (applies to **/eda/*.py)

- Write EDA work as `.py` scripts, not notebooks. Notebooks make Git review harder.
- Save all EDA scripts under `./core/pipelines/{flujo}/eda/`. The filename must be `eda_{flujo}.py`.
- The script must cover these steps in order:
  1. Download or load the source files using the same logic planned for the `extract` stage.
  2. Show the first rows and column data types (`dtypes`).
  3. Report the total row count and total column count.
  4. Identify key columns such as IDs, dates, and periods.
  5. Count unique values per column to detect possible catalogs (`< 100` unique values means catalog candidate).
  6. Analyze geographic level: national, state, or municipal (`cve_ent`, `cve_mun`, and related fields).
  7. Analyze null and empty values: `NaN`, `NA`, `N/A`, empty strings, and whitespace.
  8. Analyze periodicity when multiple source files exist.
- The final script output must be the JSON report generated with the `eda-reporte` skill. Do not rely on prints alone; serialize the results.
- Do not save intermediate files inside `eda/`. Only the script and `reporte_eda.json` belong there.
- Import project utilities from `core.utils` when possible, such as `normalize_text` and `get_logger`.

## Bootstrap & Update Instructions (applies to **/dags/*.py and **/stages/*.py)

- **Bootstrap**: the first pipeline execution. It processes the full historical dataset available from the source. The corresponding DAG uses the `_bootstrap` suffix and runs on demand.
- **Update**: subsequent executions. It processes only new or changed records since the last successful run. The corresponding DAG uses the `_update` suffix and has a defined `schedule_interval`.
- Every `Stage` must accept `mode: str` with `"bootstrap"` or `"update"` and branch its logic accordingly.
- **Append-only update**: when the source only adds new rows, implement it with `INSERT ... ON CONFLICT DO NOTHING` through `bulk_ops.insert_records` or `bulk_ops.bulk_insert`.
- **SCD update**: when the source can contain both new rows and updates to existing rows:
  - Generate a hash for the monitored columns, excluding `id` and timestamps.
  - Compare the incoming hash with the stored database hash to detect changes.
  - When a change is detected, close the current row with `valid_to = current_date` and `is_current = False`, then insert the new row with `valid_from = current_date`, `valid_to = NULL`, and `is_current = True`.
  - The integration view (`V4`) must always filter on `is_current = True`.
- Define two DAGs in the same file: one for bootstrap and one for update. Each DAG must have its own `default_args`.
- The `main()` function at the end of the file must execute the full bootstrap flow for local testing without Airflow.
