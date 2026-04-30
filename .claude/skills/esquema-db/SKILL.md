---
name: esquema-db
description: Genera el esquema SQL y las migraciones Flyway a partir del reporte EDA estandarizado.
---

# Skill: Esquema de Base de Datos

## Purpose
Invocar en la Fase 2 para traducir el análisis exploratorio a un esquema SQL versionado con Flyway.

## Steps

Determinar primero si el pipeline tiene nivel geográfico municipal o estatal (`reporte_eda.json → geografia.nivel`). El orden de las migraciones depende de esto.

### Ruta A — Pipeline con nivel geográfico (municipal o estatal)

| Versión | Nombre de archivo                        | Contenido                              |
|---------|------------------------------------------|----------------------------------------|
| V1      | `V1__foreign_tables.sql`                 | FDW cvegeo (estados y/o municipios)    |
| V2      | `V2__catalogs_{flujo}.sql`               | Tablas `cat_` por cada catálogo        |
| V3      | `V3__table_{flujo}.sql`                  | Tabla principal `stg_{flujo}`          |
| V4      | `V4__view_{flujo}.sql`                   | Vista de integración `v_{flujo}`       |

1. Generar `V1__foreign_tables.sql` con FDW cvegeo. Incluir solo las tablas foráneas que el pipeline usa (estados y/o municipios).
2. Generar `V2__catalogs_{flujo}.sql`. Una tabla `cat_` por cada columna con `es_catalogo: true` en el reporte EDA.
3. Generar `V3__table_{flujo}.sql` con tabla principal `stg_{flujo}`.
4. Generar `V4__view_{flujo}.sql` con vista de integración `v_{flujo}`.

### Ruta B — Pipeline sin nivel geográfico

| Versión | Nombre de archivo                        | Contenido                              |
|---------|------------------------------------------|----------------------------------------|
| V1      | `V1__catalogs_{flujo}.sql`               | Tablas `cat_` por cada catálogo        |
| V2      | `V2__table_{flujo}.sql`                  | Tabla principal `stg_{flujo}`          |
| V3      | `V3__view_{flujo}.sql`                   | Vista de integración `v_{flujo}`       |

### Pasos comunes a ambas rutas

5. Aplicar migraciones con `just flyway-migrate {flujo}` y verificar que no haya errores.
6. Generar diagrama ER con ERAlchemy2 y guardar en `./core/pipelines/{flujo}/assets/er_{flujo}.png`.

### Reglas de naming

- `V1__foreign_tables.sql` nunca lleva el nombre del flujo en el nombre de archivo.
- A partir de V2, el nombre sigue el patrón `V{n}__{descripcion}_{flujo}.sql`.
- Todos los scripts deben ser idempotentes (`IF NOT EXISTS`, `CREATE OR REPLACE`).

### Estructura de tablas

**Tabla catálogo (`cat_`):**
- PK: `id SMALLINT` (baja cardinalidad) o `id INTEGER` (alta cardinalidad)
- Columnas descriptivas en `snake_case` español

**Tabla principal (`stg_`):**
- PK: `id SERIAL PRIMARY KEY`
- FK: `{singular}_id INTEGER REFERENCES cat_{tabla}(id)`
- `fecha_actualizacion DATE NOT NULL` (salvo periodicidad en catálogo)
- Si SCD: `hash_id VARCHAR`, `valid_from DATE`, `valid_to DATE`, `is_current BOOLEAN`
- Índices en columnas de join frecuente

**Vista de integración (`v_`):**
- Desnormaliza `stg_` con catálogos
- Si SCD: `WHERE is_current = TRUE`
- Si geo: JOIN con tablas de `cve_geo` vía FDW
