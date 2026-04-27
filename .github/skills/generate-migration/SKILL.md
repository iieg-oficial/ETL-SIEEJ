---
name: generate-migration
description: Templates SQL idempotentes de Flyway para un pipeline SIEEJ. Cubre V1 catálogos, V2 cvegeo FDW (opcional), V3 tabla principal (con variantes SCD2), V4 vista analítica. Úsalo cuando necesites generar o extender las migraciones SQL de un pipeline.
argument-hint: <pipeline> [requiere_cvegeo=true|false] [scd2=true|false]
---

# Skill: Generar Migraciones Flyway

Fuente única de templates SQL. Las reglas de nomenclatura, idempotencia y comandos `just` están en `.github/instructions/db.instructions.md` y `flyway.instructions.md`.

## Estructura estándar de migraciones

Cada pipeline produce **4 archivos separados**, no una sola migración monolítica. Si no requiere cvegeo, omite `V2__cvegeo.sql` y renumera secuencialmente.

| Archivo | Contenido | Obligatorio |
|---|---|---|
| `V1__catalogos.sql` | Todas las tablas catálogo `stg_{pipeline}_cat_*` | Sí |
| `V2__cvegeo.sql` | Extensión FDW + server + user mapping + foreign table | Solo si `requiere_cvegeo=true` |
| `V3__tabla_principal.sql` | Tabla de datos + índices (+ `_history` si SCD2) | Sí |
| `V4__vista.sql` | Vista analítica `vw_{pipeline}_*` | Sí |

> Si no hay cvegeo, renumerar: V1 catálogos, V2 tabla, V3 vista.

Placeholders: `{pipeline}` (snake_case), `{cat}` (nombre del catálogo), `{Pipeline}` (PascalCase).

---

## Template: `V1__catalogos.sql`

```sql
-- =======================================================================
-- V1__catalogos.sql  |  Pipeline: {pipeline}
-- Tablas catálogo sincronizadas dinámicamente desde la fuente.
-- =======================================================================

CREATE TABLE IF NOT EXISTS public.stg_{pipeline}_cat_{cat} (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    CONSTRAINT uq_{pipeline}_cat_{cat}_name UNIQUE (name)
);

-- Repetir un bloque CREATE TABLE por cada catálogo identificado en el EDA.
-- Ajustar VARCHAR(n) al max_length reportado por el análisis.
```

**Reglas**:

- Una tabla por cada columna marcada `is_catalog_candidate=true` en el EDA.
- `name VARCHAR(n)` donde `n` viene del EDA (`catalog_tables[*].max_length` + margen).
- Constraint con nombre explícito `uq_{pipeline}_cat_{cat}_name`.

---

## Template: `V2__cvegeo.sql` (solo si aplica)

```sql
-- =======================================================================
-- V2__cvegeo.sql  |  Pipeline: {pipeline}
-- Conexión FDW a la BD cvegeo para resolver municipios y entidades.
-- =======================================================================

CREATE EXTENSION IF NOT EXISTS postgres_fdw;

CREATE SERVER IF NOT EXISTS cvegeo_server
    FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (host 'localhost', port '5432', dbname 'cvegeo');

CREATE USER MAPPING IF NOT EXISTS FOR CURRENT_USER
    SERVER cvegeo_server
    OPTIONS (user '', password '');

CREATE FOREIGN TABLE IF NOT EXISTS public.cvegeo_municipalities (
    id      INTEGER,
    cvegeo  INTEGER,
    cve_ent INTEGER,
    cve_mun INTEGER,
    nomgeo  VARCHAR,
    nom_ent VARCHAR
) SERVER cvegeo_server
    OPTIONS (schema_name 'public', table_name 'municipalities');
```

Ver skill `cvegeo-integration` para credenciales, setup y uso en `load.py`.

---

## Template: `V3__tabla_principal.sql` — Variante simple (sin SCD2)

```sql
-- =======================================================================
-- V3__tabla_principal.sql  |  Pipeline: {pipeline}
-- Tabla principal de datos.
-- =======================================================================

CREATE TABLE IF NOT EXISTS public.stg_{pipeline}_datos (
    id              SERIAL PRIMARY KEY,
    llave_natural   VARCHAR(64) NOT NULL,
    cat_{cat}_id    INTEGER NOT NULL REFERENCES public.stg_{pipeline}_cat_{cat}(id),
    municipio_id    INTEGER,                               -- solo si cvegeo
    fecha_dato      DATE,
    valor_numerico  NUMERIC(12, 2),
    created_at      TIMESTAMP DEFAULT now(),
    updated_at      TIMESTAMP DEFAULT now(),
    CONSTRAINT uq_{pipeline}_datos_llave UNIQUE (llave_natural)
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_{pipeline}_datos_llave
    ON public.stg_{pipeline}_datos (llave_natural);

CREATE INDEX IF NOT EXISTS ix_{pipeline}_datos_fecha
    ON public.stg_{pipeline}_datos (fecha_dato);
```

---

## Template: `V3__tabla_principal.sql` — Variante SCD2

Para estrategia de update SCD2 con `record_hash` + tabla `_history`. Ver `migrations/repd/sql/V2__tabla_stg_repd.sql` como referencia canónica.

```sql
-- =======================================================================
-- V3__tabla_principal.sql  |  Pipeline: {pipeline}
-- Tabla vigente (_current) + tabla historial (_history) para SCD2.
-- =======================================================================

-- Tabla actual: una fila vigente por llave natural
CREATE TABLE IF NOT EXISTS public.stg_{pipeline}_datos_current (
    id               SERIAL PRIMARY KEY,
    llave_natural    VARCHAR(64) NOT NULL,
    cat_{cat}_id     INTEGER NOT NULL REFERENCES public.stg_{pipeline}_cat_{cat}(id),
    -- campos de negocio ...
    record_hash      VARCHAR(64) NOT NULL,
    current_version  INTEGER NOT NULL DEFAULT 1,
    created_at       TIMESTAMP DEFAULT now(),
    updated_at       TIMESTAMP DEFAULT now(),
    CONSTRAINT uq_{pipeline}_datos_current_llave UNIQUE (llave_natural)
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_{pipeline}_datos_current_llave
    ON public.stg_{pipeline}_datos_current (llave_natural);

-- Tabla historial: snapshot por versión
CREATE TABLE IF NOT EXISTS public.stg_{pipeline}_datos_history (
    id                 SERIAL PRIMARY KEY,
    current_id         INTEGER REFERENCES public.stg_{pipeline}_datos_current(id),
    llave_natural      VARCHAR(64) NOT NULL,
    version_num        INTEGER NOT NULL,
    is_current         BOOLEAN NOT NULL DEFAULT TRUE,
    valid_from         TIMESTAMP NOT NULL DEFAULT now(),
    valid_to           TIMESTAMP,
    -- mismos campos de negocio que _current ...
    record_hash        VARCHAR(64) NOT NULL,
    created_at         TIMESTAMP DEFAULT now(),
    CONSTRAINT uq_{pipeline}_datos_history_llave_version UNIQUE (llave_natural, version_num)
);

CREATE INDEX IF NOT EXISTS ix_{pipeline}_datos_history_llave
    ON public.stg_{pipeline}_datos_history (llave_natural);

CREATE INDEX IF NOT EXISTS ix_{pipeline}_datos_history_is_current
    ON public.stg_{pipeline}_datos_history (is_current);
```

Ver skill `scd2-pattern` para la lógica de carga correspondiente en `load.py`.

---

## Template: `V4__vista.sql`

```sql
-- =======================================================================
-- V4__vista.sql  |  Pipeline: {pipeline}
-- Vista analítica con nombres humanos (joins a catálogos y cvegeo).
-- =======================================================================

CREATE OR REPLACE VIEW public.vw_{pipeline}_datos AS
SELECT
    d.id,
    d.llave_natural,
    c.name        AS {cat},
    m.nomgeo      AS municipio,          -- omitir si no hay cvegeo
    m.nom_ent     AS entidad,            -- omitir si no hay cvegeo
    d.fecha_dato,
    d.valor_numerico,
    d.created_at,
    d.updated_at
FROM public.stg_{pipeline}_datos d
LEFT JOIN public.stg_{pipeline}_cat_{cat}       c ON c.id = d.cat_{cat}_id
LEFT JOIN public.cvegeo_municipalities           m ON m.id = d.municipio_id;
```

Para SCD2, la vista consulta `stg_{pipeline}_datos_current`.

---

## Reglas de idempotencia

- `CREATE TABLE IF NOT EXISTS` — siempre.
- `CREATE INDEX IF NOT EXISTS` — siempre.
- `CREATE EXTENSION IF NOT EXISTS` — siempre.
- `CREATE SERVER IF NOT EXISTS` — siempre.
- `CREATE USER MAPPING IF NOT EXISTS` — siempre.
- `CREATE FOREIGN TABLE IF NOT EXISTS` — siempre.
- `CREATE OR REPLACE VIEW` — sustituye a `IF NOT EXISTS` en vistas.
- Constraints con nombre explícito (`uq_`, `fk_`, `ix_`, `idx_`) para rollback seguro.
- Los scripts deben sobrevivir a `just flyway-reset {pipeline}` sin errores.

## Convención de nombres

| Elemento | Formato |
|---|---|
| Tabla catálogo | `stg_{pipeline}_cat_{nombre}` |
| Tabla de datos | `stg_{pipeline}_datos` o `stg_{pipeline}_{entidad}` |
| Tabla SCD2 vigente | `stg_{pipeline}_{entidad}_current` |
| Tabla SCD2 historial | `stg_{pipeline}_{entidad}_history` |
| Vista analítica | `vw_{pipeline}_{entidad}` |
| Índice | `ix_{pipeline}_{tabla}_{columnas}` |
| Constraint UNIQUE | `uq_{pipeline}_{tabla}_{columnas}` |
| Constraint FK | `fk_{pipeline}_{tabla}_{ref}` |

## Referencias

- `migrations/repd/sql/` — catálogos + cvegeo FDW + SCD2 + vista (canónico).
- `migrations/fiscalia/sql/` — catálogos mixtos.
- `migrations/censos_economicos/flyway.conf.example` — template `.conf`.
