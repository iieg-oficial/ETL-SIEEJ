# pendientes

## Descripción general

Pipeline ETL para producir y distribuir localmente el modelo de elevación acondicionado y la pendiente de Jalisco a
partir del Continuo de Elevaciones Mexicano 4.0 (CEM 4.0) de INEGI. Entrega cinco productos raster sobre una rejilla
territorial común y calcula estadísticas municipales para las delimitaciones IIEG e INEGI.

La ruta productiva tiene exactamente tres stages: Extract, Transform y Load. El CEM nacional se conserva como fuente
inmutable y no se presenta como producto IIEG.

## Fuente general

https://www.inegi.org.mx/temas/relieve/

## Fuente específica

```shell
SOURCE_URL=https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/geografia/relieve/794551151600_t.zip
```

También puede configurarse `SOURCE_TIFF_PATH` para reutilizar el archivo nacional
`continuonacional_15m.tif` ya descargado.

## Características de los datos

| Característica | Valor |
|---|---|
| Última fecha disponible | `2024` |
| Frecuencia de actualización | Bajo demanda |
| Desagregación | Raster estatal de 15 m y estadísticas municipales |
| ¿Tiene update? | No |
| Update | Manual / bootstrap |
| Fuente | CEM 4.0 de INEGI, cobertura nacional |
| CRS fuente | `EPSG:6365` |
| CRS de productos | `EPSG:6368` |
| Resolución de productos | 15 × 15 m |
| Cobertura | Jalisco |

## Diagrama de entidad relación

El pipeline no almacena píxeles raster en PostgreSQL. Su modelo relacional está compuesto por el catálogo
`fuentes_limites_municipales`, la tabla `estadisticas_pendiente_municipales` y la vista
`vw_pendientes_estadisticas_municipales`, descritos a continuación.

## Diccionario de variables

### fuentes_limites_municipales

| variable | descripción |
|---|---|
| `id` | Identificador estable de la fuente territorial |
| `clave` | Clave de la fuente: `iieg` o `inegi` |
| `nombre_fuente` | Nombre legible de la delimitación |
| `descripcion` | Descripción institucional de la fuente |
| `version` | Versión del snapshot territorial de `cvegeo` |
| `procedencia` | Tabla y columna geométrica de origen |

### estadisticas_pendiente_municipales

| variable | descripción |
|---|---|
| `municipality_id` | `cve_mun` de Jalisco; no es el ID sustituto remoto de `cvegeo` |
| `cve_mun`, `cve_ent`, `cvegeo`, `municipio` | Identidad y nombre municipal |
| `fuente_limite_municipal_id` | FK local a la delimitación IIEG o INEGI |
| `elevation_*_m` | Mínimo, máximo, media, mediana, desviación, p05 y p95 de elevación en metros |
| `slope_degrees_*` | Mínimo, máximo, media, mediana, desviación, p05 y p95 de pendiente en grados |
| `slope_percent_*` | Media, mediana, p95 y máximo de pendiente porcentual |
| `valid_pixel_count` | Cantidad de píxeles válidos seleccionados por centro de píxel |
| `valid_area_ha` | Superficie raster válida en hectáreas |
| `municipality_vector_area_ha` | Superficie vectorial municipal en hectáreas |
| `rasterized_area_difference_ha` | Diferencia entre superficie rasterizada y vectorial |
| `coverage_percent` | Cobertura raster válida respecto de la superficie vectorial |
| `fecha_actualizacion` | Fecha de actualización de la estadística |

### vw_pendientes_estadisticas_municipales

Vista de consulta que incorpora el nombre municipal desde `cvegeo_municipalities` y la clave de la fuente territorial.
La identidad municipal se resuelve mediante `cve_ent = 14` y `cve_mun = municipality_id`.

## Migraciones

| migración | descripción |
|---|---|
| `V1__municipality_reference_pendientes.sql` | Habilita PostGIS/FDW, enlaza `cvegeo_municipalities` y valida los 125 municipios de Jalisco |
| `V2__tables_pendientes.sql` | Crea el catálogo territorial, la tabla de estadísticas, restricciones e índices |
| `V3__view_pendientes.sql` | Crea la vista municipal con identidad `cvegeo` y fuente territorial |
| `V4__comments_municipal_rasterization.sql` | Documenta las métricas de cobertura y rasterización municipal |

## Variables de entorno

| variable | descripción |
|---|---|
| `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` | Conexión PostgreSQL/PostGIS; `DB_NAME` es `pendientes` |
| `SOURCE_URL` | URL oficial del ZIP del CEM 4.0 |
| `SOURCE_TIFF_PATH` | Ruta opcional al TIFF nacional ya descargado; sustituye la descarga cuando se define |
| `CVEGEO_MUNICIPAL_BOUNDARY_SNAPSHOT_PATH` | Override opcional a un GeoPackage previamente congelado y validado |
| `SOURCE_ZIP_FILENAME` | Nombre local contractual del ZIP fuente |
| `FORCE_DOWNLOAD` | Fuerza la adquisición y reconstrucción controlada de artefactos de Extract |
| `DOWNLOAD_RETRIES` | Número de intentos de descarga |
| `DOWNLOAD_CONNECT_TIMEOUT`, `DOWNLOAD_READ_TIMEOUT` | Timeouts HTTP en segundos |
| `DOWNLOAD_CHUNK_SIZE` | Tamaño del bloque de descarga en bytes |
| `TARGET_SRID` | SRID de trabajo y productos, `6368` |
| `TARGET_RESOLUTION_M` | Resolución de la rejilla, 15 m |
| `AOI_BUFFER_M` | Buffer analítico, 10 000 m |
| `BOUNDARY_GEOMETRY_COLUMN` | Geometría estatal usada para el AOI: `geom_iieg` o `geom_inegi` |
| `STATS_MAX_CELLS`, `DIAGNOSTIC_SAMPLE_MAX_CELLS` | Límites de muestreo para estadísticas y diagnóstico |
| `EXPERIMENT_MANUAL_X`, `EXPERIMENT_MANUAL_Y` | Coordenada opcional EPSG:6368 para reproducción metodológica |
| `WHITEBOX_TOOLS_*` | Ejecutable, versión y checksum requeridos sólo para reproducir experimentos |

## Notas metodológicas

### Extract

Adquiere o reutiliza el CEM, valida su CRS, resolución, tipo, NoData y checksum, y conserva el raster nacional como
fuente inmutable. Consulta la base institucional compartida `cvegeo` para congelar `geom_iieg` y `geom_inegi` de
`public.cvegeo_municipalities`, además de contrastar `public.cvegeo_state_boundary`. Si se configura
`CVEGEO_MUNICIPAL_BOUNDARY_SNAPSHOT_PATH`, valida y reutiliza ese snapshot en lugar de consultar PostgreSQL.

### Transform

Valida los productos científicos congelados y los empaqueta como COG lossless sin recalcular FP2 ni Wood–Evans.
Calcula las estadísticas municipales desde el DEM acondicionado y la pendiente contextual, escribe el Parquet con
procedencia y genera el manifest final de Transform.

### Load

Valida los cinco COG terminados, los materializa por hardlink o copia atómica en `data/load/pendientes/`, comprueba sus
SHA-256 y hace upsert transaccional del catálogo territorial y las estadísticas municipales. No convierte GeoTIFF a
COG ni carga píxeles raster en PostgreSQL.

## Ejecución

**Bootstrap** (bajo demanda, DAG `etl_pendientes_bootstrap`, `schedule=None`):

```shell
just flyway-migrate pendientes
conda run -n etl python dags/etl_pendientes.py
```

El DAG ejecuta Extract → Transform → Load, usa `max_active_runs=1`, `retries=1`, `retry_delay=20` minutos y
`catchup=False`. No existe un flujo update automatizado.

## Notas adicionales

### Productos raster

Los tres productos continuos son `Float32`, NoData -9999, EPSG:6368, resolución 15 × 15 m y comparten rejilla y
máscara territorial de Jalisco:

- `modelo_elevacion_acondicionado_jalisco_15m.tif`;
- `pendiente_grados_jalisco_15m.tif`;
- `pendiente_porcentaje_jalisco_15m.tif`.

Los productos clasificados son `UInt8`, reservan 0 y usan NoData 255:

- `pendiente_grados_clasificada_jalisco_15m.tif`;
- `pendiente_porcentaje_clasificada_jalisco_15m.tif`.

Transform crea los cinco COG con compresión DEFLATE lossless, bloques de 512 píxeles y overviews `AVERAGE` para
productos continuos y `MODE` para clasificados.

### Metodología y validación

El acondicionamiento productivo es FP2 y la pendiente productiva es Wood–Evans 5 × 5. Horn 3 × 3 se conserva como
referencia metodológica histórica. La evaluación, parámetros, métricas, alternativas y limitaciones están documentados
en [METODOLOGIA.md](METODOLOGIA.md).

### Desarrollo local con `cvegeo`

`cvegeo` es una base institucional compartida. Pendientes reutiliza el driver, usuario, contraseña, host y puerto de
la conexión PostgreSQL configurada y cambia únicamente el nombre de la base. El SQL se administra mediante Git LFS.

```shell
git lfs install
git lfs pull
cp migrations/cvegeo/.env.example migrations/cvegeo/.env
# Configurar en migrations/cvegeo/.env las credenciales del PostgreSQL compartido.
just flyway-config cvegeo
just create-db cvegeo
just flyway-migrate cvegeo
```

### Pruebas

```shell
.venv/bin/python -m pytest -q tests/pipelines/pendientes
.venv/bin/python -m ruff check core/pipelines/pendientes tests/pipelines/pendientes
```

### Idempotencia y almacenamiento

Extract reutiliza descargas y snapshots válidos; Transform sólo reutiliza artefactos cuyos manifests y checksums
coinciden; Load vuelve a validar SHA-256 y usa upsert sin duplicar claves municipales. Los raster, GeoPackage, Parquet,
PNG experimentales y manifests de ejecución viven bajo `data/` y no se versionan.
