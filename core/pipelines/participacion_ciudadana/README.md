# participacion_ciudadana

## Descripción general

Pipeline ETL de participación electoral ciudadana a nivel municipal del INE. Carga los porcentajes de participación por municipio de Jalisco para las elecciones de 2012, 2015, 2018 y 2021, a partir de un archivo consolidado almacenado en Google Drive.

## Fuente general

https://www.ine.mx

## Fuente específica

```shell
GDRIVE_FILE_ID=
```

El archivo CSV consolidado se obtiene desde Google Drive (acceso público con el file ID).

## Características de los datos

| Característica | Valor |
|---|---|
| Última fecha disponible | `2021` |
| Frecuencia de actualización | Trienal |
| Desagregación | Municipal |
| ¿Tiene update? | No |
| Update | No aplica |

## Diagrama de entidad relación

![ERD](assets/erd.svg)

## Diccionario de variables

### stg_participacion

| variable | descripción |
|---|---|
| `entidad_id` | Clave de entidad federativa (14 = Jalisco) |
| `municipio_id` | Clave del municipio |
| `porc_participacion` | Porcentaje de participación electoral (0–100) |
| `anio` | Año de la elección |

## Migraciones

| migración | descripción |
|---|---|
| `V1__foreign_tables.sql` | FDW hacia la base `cvegeo` |
| `V2__table_participacion.sql` | Tabla principal `stg_participacion` |
| `V3__view_participacion.sql` | Vista analítica |
| `V4__initialize_materialized_view.sql` | Expone geometrías municipales en el FDW de `cvegeo` |
| `V5__materialized_views_participacion_ciudadana.sql` | Vista materializada `vm_porcentaje_participacion_geo` para consumo GIS |

## Variables de entorno

| variable | descripción |
|---|---|
| `GDRIVE_FILE_ID` | ID del archivo CSV en Google Drive |

## Notas metodológicas

### Extract

Descarga el CSV desde Google Drive usando `gdown` con el file ID. Almacena el resultado en un `.pkl` para evitar descargas repetidas.

### Transform

Renombra columnas, filtra a años de elección válidos, convierte porcentajes a numérico (elimina el símbolo `%`), limpia nulos y pivotea el formato wide → long (municipio × año).

### Load

Inserción directa de los registros en `stg_participacion` con `bulk_insert` y
refresco de `vm_porcentaje_participacion_geo` al terminar una carga exitosa.

## Ejecución

**Bootstrap** (única ejecución):

```shell
just flyway-migrate participacion_ciudadana
conda run -n etl python -m core.pipelines.participacion_ciudadana bootstrap
```

No tiene flujo update.

## Notas adicionales

El archivo de Google Drive debe actualizarse manualmente después de cada proceso electoral. Para incorporar resultados de 2024 es necesario actualizar el archivo fuente y ejecutar nuevamente el bootstrap.
