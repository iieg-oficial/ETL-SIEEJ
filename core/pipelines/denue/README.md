# denue

## Descripción general

Pipeline ETL del Directorio Estadístico Nacional de Unidades Económicas (DENUE) del INEGI. Descarga y carga el catálogo de establecimientos económicos activos en México por entidad federativa, incluyendo clasificación SCIAN, rango de personal y geolocalización, con actualización semestral.

## Fuente general

https://www.inegi.org.mx/app/mapa/denue/

## Fuente específica

```
https://www.inegi.org.mx/app/descarga/?ti=6
```

La descarga se realiza mediante scraping con Selenium; el sitio requiere navegación interactiva para obtener los enlaces de descarga por entidad.

## Características de los datos

| Característica | Valor |
|---|---|
| Última fecha disponible | `2025` |
| Frecuencia de actualización | Semestral |
| Desagregación | Nacional, Estatal, Municipal, Localidad |
| ¿Tiene update? | Sí |
| Update | Automático |

## Diagrama de entidad relación

![ERD](assets/erd.svg)

## Diccionario de variables

### stg_establecimientos

| variable | descripción |
|---|---|
| `id` | Clave única INEGI del establecimiento |
| `actualizacion_id` | FK a catálogo de actualizaciones (fecha del corte) |
| `nombre_establecimiento` | Nombre del establecimiento |
| `razon_social` | Razón social |
| `latitud` / `longitud` | Coordenadas geográficas |
| `fecha_alta` | Fecha de registro en el DENUE |
| `nombre_asentamiento` | Nombre del asentamiento humano |
| `ageb` | Clave de AGEB |
| `tipo_vial` | Tipo de vialidad (calle, avenida, boulevard, etc.) |
| `nom_vial` | Nombre de la vialidad |
| `numero_ext` | Número exterior del establecimiento |
| `cod_postal` | Código postal; `TEXT` para conservar los ceros a la izquierda |
| `telefono` | Teléfono de contacto, tal como viene del origen |
| `contacto_web` | Sitio web, correo electrónico o red social, tal como viene del origen |
| `localidad_id` | FK a catálogo de localidades |
| `sector_id` | FK a sector SCIAN |
| `subsector_id` | FK a subsector SCIAN |
| `rama_id` | FK a rama SCIAN |
| `subrama_id` | FK a subrama SCIAN |
| `clase_actividad_id` | FK a clase de actividad SCIAN |
| `rango_personal_id` | FK a rango de personal ocupado |
| `tipo_establecimiento_id` | FK a tipo de establecimiento |

## Migraciones

| migración | descripción |
|---|---|
| `V1__foreign_tables.sql` | FDW hacia la base `cvegeo` |
| `V2__catalogs_denue.sql` | Catálogos SCIAN (sectores, subsectores, ramas, subramas, clases) y tipos |
| `V3__tables_denue.sql` | Tabla principal `stg_establecimientos` |
| `V4__views_denue.sql` | Vista desnormalizada nacional |
| `V5__views_jalisco.sql` | Vista filtrada a Jalisco |
| `V6__domicilio_contacto_jalisco.sql` | Domicilio (vialidad, número exterior, código postal) y contacto en `stg_est_jal` |

## Variables de entorno

| variable | descripción |
|---|---|
| `DENUE_URL` | URL de la página de descarga del DENUE |
| `BOOTSTRAP_START_DATE` | Fecha mínima de alta para incluir en bootstrap (ej. `01/01/2016`) |
| `CHUNK_SIZE` | Tamaño de lote para inserción masiva |
| `SCIAN_FILE_ID` | Google Drive file ID del archivo `scian_2023.csv` |
| `SCIAN_CSV_NAME` | Nombre del archivo CSV de clasificación SCIAN |

## Notas metodológicas

### Extract

Navega el portal INEGI con Selenium para obtener los enlaces de descarga por entidad. Descarga los ZIPs, extrae los CSVs y almacena los datos en archivos `.pkl` por entidad.

### Transform

Lee los pickles, normaliza texto, construye los catálogos SCIAN a partir del CSV de clasificación, resuelve IDs foráneos y determina la fecha de actualización del corte.

### Load

Upsert de catálogos e inserción por lotes en `stg_establecimientos` con `upsert_records` para manejar actualizaciones semestrales.

## Ejecución

**Bootstrap** (carga inicial desde `BOOTSTRAP_START_DATE`):

```shell
just flyway-migrate denue
conda run -n etl python -m core.pipelines.denue bootstrap
```

**Update semestral** (DAG `etl_denue_update`, cada 10 días):

```shell
conda run -n etl python -m core.pipelines.denue update
```

## Notas adicionales

El scraping con Selenium requiere un navegador Chrome disponible. El bootstrap puede tardar muchas horas por la cantidad de establecimientos. El pipeline verifica automáticamente si existe un corte más reciente antes de descargar.
