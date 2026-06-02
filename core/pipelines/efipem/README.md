# efipem

## Descripción general

Pipeline ETL de las Estadísticas de Finanzas Públicas Estatales y Municipales (EFIPEM) del INEGI. Contiene datos anuales de ingresos, egresos y deuda de los municipios mexicanos, clasificados por tema, clasificador y concepto presupuestario.

## Fuente general

https://www.inegi.org.mx/programas/finanzas/

## Fuente específica

```shell
EFIPEM_SOURCE_URL=https://www.inegi.org.mx/contenidos/programas/finanzas/datosabiertos/conjunto_de_datos_efipem_municipal_csv.zip
```

## Características de los datos

| Característica | Valor |
|---|---|
| Última fecha disponible | `2023` |
| Frecuencia de actualización | Trimestral |
| Desagregación | Nacional, Municipal |
| ¿Tiene update? | No |
| Update | No aplica |

## Diagrama de entidad relación

![ERD](assets/erd.svg)

## Diccionario de variables

### stg_efipem_finanzas_trimestral

| variable | descripción |
|---|---|
| `anio` | Año del dato |
| `cvegeo` | Clave INEGI del municipio (5 dígitos) |
| `cve_ent` | Clave de entidad federativa |
| `cve_mun` | Clave del municipio dentro de la entidad |
| `tema_id` | FK a catálogo de temas (Ingresos, Egresos, Deuda) |
| `clasificador_id` | FK a catálogo de clasificadores presupuestarios |
| `concepto_id` | FK a catálogo de conceptos presupuestarios |
| `valor` | Monto en pesos |
| `estatus_id` | FK a catálogo de estatus de la cifra |

## Migraciones

| migración | descripción |
|---|---|
| `V1__foreign_tables.sql` | FDW hacia la base `cvegeo` |
| `V2__catalogs_efipem.sql` | Catálogos de temas, clasificadores, conceptos y estatus |
| `V3__table_efipem.sql` | Tabla principal `stg_efipem_finanzas_trimestral` |
| `V4__view_efipem.sql` | Vista analítica desnormalizada |

## Variables de entorno

| variable | descripción |
|---|---|
| `EFIPEM_SOURCE_URL` | URL del ZIP con todos los CSVs anuales del EFIPEM municipal |
| `EFIPEM_LOAD_BATCH_SIZE` | Tamaño de lote para inserción masiva |

## Notas metodológicas

### Extract

Descarga el ZIP desde `EFIPEM_SOURCE_URL`, lo descomprime en el directorio de trabajo y verifica que existan los CSVs anuales esperados.

### Transform

Lee y concatena todos los CSVs anuales, filtra los registros de Jalisco, normaliza nombres de columnas, extrae y deduplica los catálogos, y resuelve los IDs foráneos.

### Load

Upsert de catálogos e inserción masiva de datos en `stg_efipem_finanzas_trimestral` con `bulk_insert` por lotes.

## Ejecución

**Bootstrap** (carga histórica completa):

```shell
just flyway-migrate efipem
conda run -n etl python -m core.pipelines.efipem bootstrap
```

No tiene flujo update automatizado.

## Notas adicionales

El INEGI publica el EFIPEM municipal con rezago de aproximadamente 1 año. El ZIP descargado contiene un CSV por año; agregar nuevos años solo requiere ejecutar nuevamente el bootstrap ya que la inserción es idempotente para nuevos registros.
