# Diccionario de datos institucional

## Convenciones de nomenclatura

Todas las tablas y vistas del esquema siguen un sistema de prefijos que indica su rol dentro
del flujo ETL. Entender esta convención es necesario para interpretar correctamente el diccionario.

| Prefijo | Capa | Propósito |
|---|---|---|
| `cat_*` | Catálogos | Tablas de referencia estáticas o semi-estáticas (tipos, claves, clasificadores) |
| `stg_*` | Staging | Datos crudos o en proceso de transformación; insumo directo del ETL |
| `vw_*` | Vistas normales | `CREATE [OR REPLACE] VIEW` con joins de lectura sobre `stg_*`/`cat_*` (ej. `vw_asg_imss`, `vw_nacimientos`) |
| `mv_*` | Vistas materializadas | `CREATE MATERIALIZED VIEW`, normalmente para consumo GIS o agregados costosos, con `REFRESH` disparado desde `load.py` (ej. `mv_enoe_tasas`) |

**Excepciones a tener en cuenta:**
- Algunas vistas materializadas de uso GIS (`iieg_gis`) se nombran por el concepto de negocio, sin prefijo `mv_` — ejemplo: `brecha_salarial`, `delitos_fiscalia_feminicidio` en `migrations/asg_imss/sql/V6__vistas_materializadas_asg_imss.sql` y `migrations/fiscalia/sql/`.
- No existe un prefijo `ce_view_*`/`ce_vista_*` en el código; el estándar real verificado en las migraciones es `vw_*`/`mv_*`.

### Base geográfica de referencia: `cvegeo`

`cvegeo` es una base de datos PostgreSQL independiente que centraliza la geografía oficial de
México (verificado directamente en el servidor `iieg-db-etl`, contenedor `postgis_db`). Cada
pipeline que requiere referencias geográficas la accede mediante `postgres_fdw`, declarando
tablas foráneas en su migración `V1__foreign_tables.sql`.

La base contiene 5 tablas en total:
| Tabla | Alcance | Filas |
|---|---|---|
| `cvegeo_states` | Nacional (32 entidades) | 32 |
| `cvegeo_municipalities` | Nacional (todos los municipios de México) | 2,475 |
| `cvegeo_regions` | Solo Jalisco (12 regiones administrativas IIEG) | 12 |
| `cvegeo_county_seats` | Solo Jalisco (cabeceras municipales) | 125 |
| `cvegeo_state_boundary` | Solo Jalisco (límite estatal) | 1 |

### Relación con los pipelines

`entidad_id` se une contra
`cvegeo_states.cve_ent`. `municipio_id`, en cambio, **no tiene una columna de unión única**;
coexisten tres patrones distintos según el pipeline:

| Patrón | `JOIN` típico | Pipelines que lo usan |
|---|---|---|
| **Compuesto** (`cve_mun` + `cve_ent`) | `m.cve_mun = x.municipio_id AND m.cve_ent = x.entidad_id` | `agropecuario_siap`, `censo_poblacion`, `censos_economicos`, `centros_educativos`, `denue`, `escuelas`, `establecimientos_de_salud`, `participacion_ciudadana`, `produccion_ganadera`, `enoe_microdatos`, `fiscalia` |
| **Código CVEGEO directo** (`cvegeo`, 5 dígitos) | `m.cvegeo = x.municipio_id` | `conapo`, `intensidad_migratoria`, `marginacion`, `nacimientos_dgis`, `delitos_fuero_comun` (con `::INTEGER`), `efipem` (con `LPAD(...::text, 5, '0')`) |
| **Surrogate key** (`id` interno de `cvegeo_municipalities`) | `m.id = x.municipio_id` | `defunciones`, `repd` |

**Ejemplo — pipeline `intensidad_migratoria`** (usa el patrón "Código CVEGEO directo"):

Las tablas foráneas se declaran en
`migrations/intensidad_migratoria/sql/V1__foreign_tables.sql` y se usan con JOIN en las vistas
de `V3__views_iim.sql`:

```sql
-- Ejemplo: pipeline intensidad_migratoria
LEFT JOIN cvegeo_municipalities m ON m.cvegeo = i.municipio_id
```

Antes de escribir un `JOIN` nuevo, verifica cuál de los tres patrones usa tu pipeline revisando
cómo se pobló `municipio_id` en `load.py`; no asumas el patrón de `intensidad_migratoria` por
defecto.
