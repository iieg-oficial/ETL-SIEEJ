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
| `V1__catalogos_repd.sql` | Catálogos de sexo, nacionalidad, rango de edad, estatus, condición y tipo de cierre |
| `V2__tabla_stg_repd.sql` | Tablas `stg_repd_case_current` y `stg_repd_case_history` |
| `V3__vista_repd.sql` | Vista analítica que resuelve catálogos y municipios |

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
