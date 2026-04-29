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

1. Generar `V1__foreign_tables.sql` siguiendo `template_v1_foreign_tables.sql`. Incluir solo las tablas foráneas que el pipeline usa (estados y/o municipios).
2. Generar `V2__catalogs_{flujo}.sql` siguiendo `template_v1_catalogos.sql`. Una tabla `cat_` por cada columna con `es_catalogo: true` en el reporte EDA.
3. Generar `V3__table_{flujo}.sql` siguiendo `template_v3_tabla.sql`.
4. Generar `V4__view_{flujo}.sql` siguiendo `template_v4_vista.sql`.

### Ruta B — Pipeline sin nivel geográfico

| Versión | Nombre de archivo                        | Contenido                              |
|---------|------------------------------------------|----------------------------------------|
| V1      | `V1__catalogs_{flujo}.sql`               | Tablas `cat_` por cada catálogo        |
| V2      | `V2__table_{flujo}.sql`                  | Tabla principal `stg_{flujo}`          |
| V3      | `V3__view_{flujo}.sql`                   | Vista de integración `v_{flujo}`       |

1. Generar `V1__catalogs_{flujo}.sql` siguiendo `template_v1_catalogos.sql`.
2. Generar `V2__table_{flujo}.sql` siguiendo `template_v3_tabla.sql`.
3. Generar `V3__view_{flujo}.sql` siguiendo `template_v4_vista.sql`.

### Pasos comunes a ambas rutas

5. Aplicar migraciones con `just flyway-migrate {flujo}` y verificar que no haya errores.
6. Generar diagrama ER con ERAlchemy2 y guardar en `./core/pipelines/{flujo}/assets/er_{flujo}.png`.

**Reglas de naming:**
- `V1__foreign_tables.sql` nunca lleva el nombre del flujo en el nombre de archivo.
- A partir de V2, el nombre sigue el patrón `V{n}__{descripcion}_{flujo}.sql`.
- Todos los scripts deben ser idempotentes (`IF NOT EXISTS`, `CREATE OR REPLACE`).

## Templates

→ `template_v1_foreign_tables.sql` — FDW cvegeo (Ruta A, V1)
→ `template_v1_catalogos.sql` — Tablas catálogo (Ruta A V2 / Ruta B V1)
→ `template_v3_tabla.sql` — Tabla principal (Ruta A V3 / Ruta B V2)
→ `template_v4_vista.sql` — Vista de integración (Ruta A V4 / Ruta B V3)
