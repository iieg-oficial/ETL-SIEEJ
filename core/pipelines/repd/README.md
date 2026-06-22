# repd

## Descripción general

Pipeline ETL del Registro Estatal de Personas Desaparecidas (REPD) de Jalisco. Descarga el registro actualizado de casos de personas desaparecidas e implementa SCD Tipo 2 para rastrear el historial de cambios en el estatus y la información de cada caso.

## Fuente general

https://repd.jalisco.gob.mx

## Fuente específica

```shell
REPD_DATA_URL=
```

## Características de los datos

| Característica | Valor |
|---|---|
| Última fecha disponible | `2025-05` |
| Frecuencia de actualización | Mensual |
| Desagregación | Estatal, Municipal |
| ¿Tiene update? | Sí |
| Update | Automático |

## Diagrama de entidad relación

![ERD](assets/erd.svg)

## Diccionario de variables

### stg_repd_case_current

| variable | descripción |
|---|---|
| `feb` | Folio Estadístico de Búsqueda (PK — identificador único del caso) |
| `disappearance_state_name` | Nombre del estado de desaparición |
| `location_state_name` | Nombre del estado de localización |
| `linked_feb` | FEB de caso relacionado (si existe) |
| `record_hash` | Hash SHA-256 del contenido del registro (para SCD2) |
| `current_version` | Número de versión actual del registro |
| `created_at` | Timestamp de creación del registro |
| `updated_at` | Timestamp de última actualización |

### stg_repd_case_history

| variable | descripción |
|---|---|
| `feb` | Folio Estadístico de Búsqueda |
| `is_current` | Indica si es la versión vigente |
| `valid_from` | Timestamp de inicio de vigencia |
| `record_hash` | Hash SHA-256 del contenido histórico |

## Migraciones

| migración | descripción |
|---|---|
| `V1__catalogos_repd.sql` | FDW a cvegeo (con geometrías) y CONAPO; catálogos de sexo, nacionalidad, rango de edad, estatus, condición y tipo de cierre |
| `V2__tabla_stg_repd.sql` | Tablas `stg_repd_case_current` y `stg_repd_case_history` |
| `V3__vista_repd.sql` | Vista analítica que resuelve catálogos y municipios |
| `V4__vistas_materializadas_repd.sql` | 6 vistas materializadas con geometrías y tasas CONAPO para consumo GIS |
| `V5__comments_repd.sql` | Comentarios en vistas materializadas |

## Vistas materializadas (consumo GIS)

6 vistas materializadas que agregan casos REPD por municipio y mes, con geometrías (`geom_iieg`, `geom_inegi` SRID 6368) y tasas por 100,000 habitantes (denominador CONAPO).

| vista | columnas clave | descripción |
|---|---|---|
| `personas_desaparecidas` | `total`, `total_hombres`, `total_mujeres`, `tasa_total`, `tasa_hombres`, `tasa_mujeres` | Reportes mensuales de personas desaparecidas por municipio (status_id = 2) |
| `personas_desaparecidas_hombres` | `total_hombres`, `tasa_hombres` | Vista filtrada sólo con desaparecidos hombres |
| `personas_desaparecidas_mujeres` | `total_mujeres`, `tasa_mujeres` | Vista filtrada sólo con desaparecidas mujeres |
| `personas_localizadas` | `total`, `total_hombres`, `total_mujeres`, `tasa_total`, `tasa_hombres`, `tasa_mujeres` | Personas localizadas por municipio y mes (status_id = 3) |
| `personas_localizadas_hombres` | `total_hombres`, `tasa_hombres` | Vista filtrada sólo con localizados hombres |
| `personas_localizadas_mujeres` | `total_mujeres`, `tasa_mujeres` | Vista filtrada sólo con localizadas mujeres |

Columnas comunes: `fid`, `nombre`, `fecha` (YYYY-MM-01), `clave_entidad` (14), `clave_municipio` (EEMMM), `geom_iieg`, `geom_inegi`.

Las vistas se crean con `WITH NO DATA`; se deben refrescar después de cada carga:

```shell
just psql repd -c "REFRESH MATERIALIZED VIEW personas_desaparecidas;"
just psql repd -c "REFRESH MATERIALIZED VIEW personas_desaparecidas_hombres;"
just psql repd -c "REFRESH MATERIALIZED VIEW personas_desaparecidas_mujeres;"
just psql repd -c "REFRESH MATERIALIZED VIEW personas_localizadas;"
just psql repd -c "REFRESH MATERIALIZED VIEW personas_localizadas_hombres;"
just psql repd -c "REFRESH MATERIALIZED VIEW personas_localizadas_mujeres;"
```

## Variables de entorno

| variable | descripción |
|---|---|
| `REPD_DATA_URL` | URL de descarga del archivo del REPD |

## Notas metodológicas

### Extract

Descarga el archivo de datos del REPD desde `REPD_DATA_URL` y lo almacena localmente. El archivo contiene el registro completo y actualizado de todos los casos.

### Transform

Normaliza texto, extrae catálogos (sexo, nacionalidad, rangos de edad, estatus, condición de localización, tipo de cierre), calcula el hash SHA-256 del contenido de cada caso para detección de cambios.

### Load

Compara hashes con los registros actuales en `stg_repd_case_current`. Los registros nuevos se insertan; los modificados se versionan en `stg_repd_case_history` y se actualizan en `current`. Los catálogos se sincronizan con `insert_records`.

## Ejecución

**Bootstrap** (carga inicial completa):

```shell
just flyway-migrate repd
conda run -n etl python -m core.pipelines.repd bootstrap
```

**Update mensual** (DAG `etl_repd_update`, cron `0 3 1 * *`):

```shell
conda run -n etl python -m core.pipelines.repd update
```

## Notas adicionales

El SCD2 permite auditar la evolución de cada caso a lo largo del tiempo. La tabla `stg_repd_case_history` puede crecer considerablemente si hay muchos cambios de estatus. La URL del REPD puede requerir autenticación institucional.
