---
applyTo: "**/*.sql,**/schemas.py"
---

# Database Instructions

> Applies to: DB work on SQL migrations and `schemas.py`

## Rules

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
