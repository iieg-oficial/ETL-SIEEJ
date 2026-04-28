---
name: database-rules
description: Reglas para esquemas SQLAlchemy y migraciones Flyway de los pipelines ETL SIEEJ.
applyTo: "migrations/**/*.sql,core/pipelines/**/schemas.py,core/pipelines/**/mappings.py"
---

## SQLAlchemy

- Usar SQLAlchemy 2.0: `Mapped`, `mapped_column`, `DeclarativeBase`. Nunca el estilo 1.x (`Column`, `declarative_base`).
- Toda tabla tiene PK `id: Mapped[int]`.
- FKs se nombran `{singular_table_name}_id` y referencian `{tabla}.id`.
- Toda tabla principal tiene `fecha_actualizacion: Date NOT NULL`, salvo que la periodicidad ya esté capturada por un catálogo `periodos`.

## Naming de tablas

- Minúsculas, sin acentos (ñ → ni), separadas por guiones bajos, en plural.
- En español, sin prefijos en el `__tablename__`.
- Prefijos solo a nivel BD/migración:
  - `cat_` para tablas catálogo.
  - `stg_` para tablas principales (staging).
- Las claves de columnas siguen `snake_case` en español, sin caracteres especiales.

## Tipos

Homologar:

| Origen | Destino |
|---|---|
| string | `Text` / `VARCHAR(n)` |
| numérico | `Integer` / `Numeric` / `Float` |
| fecha | `Date` |
| timestamp | `TIMESTAMP` |

## Migraciones (Flyway)

Estructura por pipeline en `migrations/{flujo}/sql/`:

- `V1__foreign_tables.sql` — `postgres_fdw` y foreign tables hacia `cve_geo` (entidades, municipios, localidades). Nunca duplicar geografía en el servidor.
- `V2__catalogs_{flujo}.sql` — catálogos `cat_*` (omitir si no aplica).
- `V3__tables_{flujo}.sql` — tablas principales `stg_*`. La columna `nullable` debe coincidir con `schemas.py`.
- `V4__views_{flujo}.sql` — vistas de integración con joins a `cvegeo`. Filtrar `WHERE cve_ent = 14` solo si el pipeline es Jalisco-only.

Reglas operativas:

- Aplicar migraciones siempre vía `just flyway-*` contra la BD docker local.
- Errores de lógica → corregir el script de migración existente. **No** crear migraciones nuevas para parchar.
- Mantener `flyway.conf.example` versionado y `flyway.conf` ignorado.

## Lectura de la BD

Usar la BD docker local vía `just`. No conectar a producción para validar.
