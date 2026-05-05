---
name: sqlalchemy-models
description: Use when generating `schemas.py` with SQLAlchemy 2.x models that match the Flyway migrations.
---

# Skill: SQLAlchemy Models

## Purpose
Use this skill after Flyway migrations are defined or applied to generate the ORM models used by the load stages.

## Steps

1. Verify that `./core/pipelines/{flujo}/attributes.py` exists with `{Flujo}Tables(StrEnum)` using one member per table name and `auto()`. Create it first if needed.
2. Read the catalog migrations and the main table migration to extract table names and column definitions.
3. Create `{Flujo}Base(DeclarativeBase)` with a `columns()` helper that returns column names.
4. Create one class per catalog table (`cat_`) with typed columns using `Mapped` and `mapped_column`.
5. Create the main staging class (`stg_`) with its columns and foreign keys.
6. Import `{Flujo}Tables as T` from `attributes.py` and use `T.TABLE_NAME` in `__tablename__`, never string literals.
7. Define relationships from the staging model to each catalog with `relationship()`.
8. Save the result to `./core/pipelines/{flujo}/schemas.py`.

## Template

See `template.py` in this folder.
