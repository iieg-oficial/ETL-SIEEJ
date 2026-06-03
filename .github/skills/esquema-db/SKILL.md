---
name: esquema-db
description: Use when deriving the SQL schema and Flyway migrations from the standardized EDA report.
---

# Skill: Database Schema

## Purpose
Use this skill in the DB phase to translate EDA findings into a versioned Flyway schema.

## Steps

First determine whether the pipeline has state or municipal geography (`reporte_eda.json -> geografia.nivel`). The migration order depends on that.

### Path A — Pipeline with geography level

| Version | Filename                                 | Content                                |
|---------|------------------------------------------|----------------------------------------|
| V1      | `V1__foreign_tables.sql`                 | `cve_geo` FDW tables                   |
| V2      | `V2__catalogs_{flujo}.sql`               | One `cat_` table per catalog           |
| V3      | `V3__table_{flujo}.sql`                  | Main `stg_{flujo}` table               |
| V4      | `V4__view_{flujo}.sql`                   | Integration view `v_{flujo}`           |
| V5      | `V5__comments_{flujo}.sql`               | Table and column comments              |

1. Generate `V1__foreign_tables.sql` from `template_v1_foreign_tables.sql`. Include only the foreign tables used by the pipeline.
2. Generate `V2__catalogs_{flujo}.sql` from `template_v1_catalogos.sql`. Create one `cat_` table for each column marked as a catalog in the EDA report.
3. Generate `V3__table_{flujo}.sql` from `template_v3_tabla.sql`.
4. Generate `V4__view_{flujo}.sql` from `template_v4_vista.sql`.
5. Generate `V5__comments_{flujo}.sql` from `template_v5_comments.sql`. Add `COMMENT ON TABLE` and `COMMENT ON COLUMN` for every table and column so AI Agents can retrieve context from the database schema.

### Path B — Pipeline without geography level

| Version | Filename                                 | Content                                |
|---------|------------------------------------------|----------------------------------------|
| V1      | `V1__catalogs_{flujo}.sql`               | One `cat_` table per catalog           |
| V2      | `V2__table_{flujo}.sql`                  | Main `stg_{flujo}` table               |
| V3      | `V3__view_{flujo}.sql`                   | Integration view `v_{flujo}`           |
| V4      | `V4__comments_{flujo}.sql`               | Table and column comments              |

1. Generate `V1__catalogs_{flujo}.sql` from `template_v1_catalogos.sql`.
2. Generate `V2__table_{flujo}.sql` from `template_v3_tabla.sql`.
3. Generate `V3__view_{flujo}.sql` from `template_v4_vista.sql`.
4. Generate `V4__comments_{flujo}.sql` from `template_v5_comments.sql`. Add `COMMENT ON TABLE` and `COMMENT ON COLUMN` for every table and column so AI Agents can retrieve context from the database schema.

### Common steps

5. Apply migrations with `just flyway-migrate {flujo}` and verify that they succeed.
6. Generate the ER diagram with ERAlchemy2 and save it to `./core/pipelines/{flujo}/assets/er_{flujo}.png`.

**Naming rules:**
- `V1__foreign_tables.sql` never includes the pipeline name in the filename.
- From V2 onward, the filename follows `V{n}__{descripcion}_{flujo}.sql`.
- All scripts must be idempotent with patterns such as `IF NOT EXISTS` and `CREATE OR REPLACE`.

## Templates

See `template_v1_foreign_tables.sql`, `template_v1_catalogos.sql`, `template_v3_tabla.sql`, `template_v4_vista.sql`, and `template_v5_comments.sql` in this folder.
