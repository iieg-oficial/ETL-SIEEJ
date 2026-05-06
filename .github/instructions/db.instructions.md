---
name: db
description: Reglas de base de datos para el proyecto SIEEJ — SQLAlchemy 2.x, Flyway, nomenclatura y convenciones de esquema. Los templates SQL y las integraciones van en skills.
applyTo: "migrations/**/*.sql,core/pipelines/**/schemas.py,core/pipelines/**/config.py"
---

# Database — Reglas

> Templates SQL → skill `generate-migration`. Integración cvegeo → skill `cvegeo-integration`. Patrón SCD2 → skill `scd2-pattern`. Comandos `just flyway-*` → `flyway.instructions.md`. Este archivo define **reglas y convenciones**, no código de ejemplo.

## SQLAlchemy 2.x — Reglas

- Usar siempre `DeclarativeBase` + `Mapped` + `mapped_column`. No usar la API antigua (`Column`, `relationship` sin tipos).
- Cada pipeline declara su propia `{Pipeline}Base(DeclarativeBase)` — no compartir Base entre pipelines.
- Un modelo por tabla; el `__tablename__` debe coincidir exactamente con el nombre de la tabla en el SQL de migraciones.
- Toda llave natural: `UniqueConstraint` **y** `Index` con nombre explícito (`uq_...`, `ix_...`).
- Campos opcionales: `Mapped[Optional[T]]`.
- Timestamps: `created_at`, `updated_at` con `server_default=func.now()` (y `onupdate=func.now()` en `updated_at`).
- Si hay múltiples catálogos del mismo tipo, registrar `CATALOG_MODELS: dict[str, type]` para iteración dinámica en `load.py`.

### Tipos recomendados

| Dato | Python | SQLAlchemy / PostgreSQL |
|---|---|---|
| Texto corto ≤ 100 | `str` | `String(n)` / `VARCHAR(n)` |
| Texto largo sin límite | `str` | `Text` / `TEXT` |
| Entero | `int` | implícito / `INTEGER` |
| Decimal | `float` / `Decimal` | `Numeric(p, s)` / `NUMERIC(p, s)` |
| Fecha | `date` | implícito / `DATE` |
| Timestamp | `datetime` | implícito / `TIMESTAMP` |
| Booleano | `bool` | implícito / `BOOLEAN` |

## Nomenclatura de BD

| Elemento | Formato |
|---|---|
| Tabla catálogo | `stg_{pipeline}_cat_{nombre}` |
| Tabla principal | `stg_{pipeline}_datos` o `stg_{pipeline}_{entidad}` |
| Tabla SCD2 vigente | `stg_{pipeline}_{entidad}_current` |
| Tabla SCD2 historial | `stg_{pipeline}_{entidad}_history` |
| Vista analítica | `vw_{pipeline}_{entidad}` |
| Constraint UNIQUE | `uq_{pipeline}_{tabla}_{columnas}` |
| Constraint FK | `fk_{pipeline}_{tabla}_{ref}` |
| Índice | `ix_{pipeline}_{tabla}_{columnas}` |

Todo en `schema public` salvo que exista razón explícita.

## Flyway — Reglas

### Nomenclatura de archivos

- Formato: `V{n}__{descripcion_snake_case}.sql`.
- Numeración secuencial **sin saltos**.
- Descripción corta y clara (español o inglés, consistente por pipeline).
- Estructura estándar: V1 catálogos, V2 cvegeo (si aplica), V3 tabla principal, V4 vista.
- **Nunca** modificar un script ya aplicado — crear siempre un nuevo `V{n+1}`.

### Idempotencia (obligatoria)

Todo script SQL debe sobrevivir a `just flyway-reset {pipeline}` sin errores:

- `CREATE TABLE IF NOT EXISTS` siempre.
- `CREATE INDEX IF NOT EXISTS` siempre.
- `CREATE EXTENSION IF NOT EXISTS` siempre.
- `CREATE SERVER / USER MAPPING / FOREIGN TABLE IF NOT EXISTS` siempre.
- `CREATE OR REPLACE VIEW` para vistas.
- Constraints con nombre explícito para rollback seguro.

### flyway.conf

- Commitear **solo** `flyway.conf.example` (sin credenciales reales).
- `flyway.conf` va en `.gitignore` y nunca se sube.
- Copiar de un pipeline existente y ajustar `url` + `locations`.

## Config del pipeline — pydantic-settings

- Heredar siempre de `core.config.BaseConfig`.
- `model_config = SettingsConfigDict(env_file=env_path("{pipeline}"))`.
- Variables prefijadas con `{PIPELINE}_` en UPPER_SNAKE_CASE.
- Todas las variables con `Field(default=...)` — evitar settings sin default que revienten al importar.
- El `.env` real vive en `core/pipelines/{pipeline}/.env`, **nunca** se commitea. Solo `.env.example`.

## cvegeo FDW

Aplicar skill `cvegeo-integration` cuando el pipeline requiera resolver municipios/entidades INEGI. Resumen:

- Migración dedicada `V2__cvegeo.sql` con `postgres_fdw` + server + user mapping + foreign table.
- Columna `municipio_id INTEGER` en la tabla principal (sin FK formal hacia la tabla foreign).
- Resolución en `load.py` usando `core.utils.bulk_ops.get_cvegeo_mapping` + tupla `(estado_upper, municipio_upper)`.
- `SKIP_MUNICIPALITY_VALUES` en `consts.py` para valores que no deben resolverse.

## Checklist de BD antes del PR

- [ ] `just flyway-reset {pipeline}` pasa sin errores.
- [ ] `just flyway-validate {pipeline}` sin divergencias.
- [ ] `schemas.py` en sync con el SQL de migraciones (nombres de tablas, columnas, tipos, constraints).
- [ ] Ni `.env` ni `flyway.conf` están en el commit.
- [ ] `.env.example` y `flyway.conf.example` sí están commiteados.
- [ ] Nombres de constraints e índices siguen la convención.
