# Diccionario de datos institucional — SIEEJ ETL

## Convenciones de nomenclatura

Todas las tablas y vistas del esquema siguen un sistema de prefijos que indica su rol dentro
del flujo ETL. Entender esta convención es necesario para interpretar correctamente el diccionario.

| Prefijo | Capa | Propósito |
|---|---|---|
| `cat_*` | Catálogos | Tablas de referencia estáticas o semi-estáticas (tipos, claves, clasificadores) |
| `stg_*` | Staging | Datos crudos o en proceso de transformación; insumo directo del ETL |
| `ce_view_*` | Vistas finales (inglés) | Vistas de consumo expuestas a Superset y la API REST |
| `ce_vista_*` | Vistas finales (español) | Alias o variante de nomenclatura interna en español |

### Base geográfica de referencia: `cvegeo`

`cvegeo` es una base de datos PostgreSQL independiente que centraliza la geografía oficial de
México. Cada pipeline que requiere referencias geográficas la accede mediante `postgres_fdw`,
declarando tablas foráneas en su migración `V1__foreign_tables.sql`.

Sus dos tablas principales son:

| Tabla | Clave | Descripción |
|---|---|---|
| `cvegeo_states` | `cve_ent` | Estados de la República Mexicana |
| `cvegeo_municipalities` | `cvegeo` | Municipios (combina `cve_ent` + `cve_mun`) |

**Ejemplo — pipeline `intensidad_migratoria`:**

Las tablas foráneas se declaran en
`migrations/intensidad_migratoria/sql/V1__foreign_tables.sql` y se usan con JOIN en las vistas
de `V3__views_iim.sql`:

```sql
-- Ejemplo: pipeline intensidad_migratoria
LEFT JOIN cvegeo_municipalities m ON m.cvegeo = i.municipio_id
```

Este patrón — `municipio_id → cvegeo_municipalities.cvegeo` — es la FK geográfica estándar
para pipelines con granularidad municipal.
