# Pipeline: REPD

Pipeline ETL para el Registro Estatal de Personas Desaparecidas (REPD) de Jalisco.

## Fuente de datos

El pipeline consume un archivo Excel (.xlsx) descargado directamente desde la API publica del REPD:

- **URL**: `https://repd.jalisco.gob.mx/api/v1/version_publica/exportrebdboptimizado/xls/`
- **Formato**: XLSX, hoja "DATOS", header en fila 13, 18 columnas, ~37,000 registros
- **Llave natural**: Folio Estatal de Busqueda (FEB), UUID unico por caso

## Esquema de base de datos

```
+---------------------------+     +-----------------------------------+
| stg_repd_cat_sex          |     | stg_repd_cat_nationality          |
|---------------------------|     |-----------------------------------|
| id SERIAL PK              |     | id SERIAL PK                      |
| name VARCHAR(60) UNIQUE   |     | name VARCHAR(100) UNIQUE          |
+---------------------------+     +-----------------------------------+

+---------------------------+     +-----------------------------------+
| stg_repd_cat_age_range    |     | stg_repd_cat_status               |
|---------------------------|     |-----------------------------------|
| id SERIAL PK              |     | id SERIAL PK                      |
| name VARCHAR(50) UNIQUE   |     | name VARCHAR(100) UNIQUE          |
+---------------------------+     +-----------------------------------+

+-----------------------------------+     +-------------------------------------------+
| stg_repd_cat_location_condition   |     | stg_repd_cat_location_classification      |
|-----------------------------------|     |-------------------------------------------|
| id SERIAL PK                      |     | id SERIAL PK                              |
| name VARCHAR(60) UNIQUE           |     | name VARCHAR(100) UNIQUE                  |
+-----------------------------------+     +-------------------------------------------+

+---------------------------+
| stg_repd_cat_closure_type |
|---------------------------|
| id SERIAL PK              |
| name VARCHAR(100) UNIQUE  |
+---------------------------+

+------------------------------------------------------------------+
|                     stg_repd_case_current                         |
|------------------------------------------------------------------|
| id SERIAL PK                                                     |
| feb VARCHAR(64) NOT NULL UNIQUE                                  |
| sex_id INTEGER NOT NULL -> stg_repd_cat_sex(id)                  |
| nationality_id INTEGER NOT NULL -> stg_repd_cat_nationality(id)  |
| age_range_id INTEGER NOT NULL -> stg_repd_cat_age_range(id)      |
| report_date DATE NOT NULL                                        |
| disappearance_date DATE                                          |
| disappearance_state_name VARCHAR(100)                            |
| disappearance_municipality_id INTEGER (cvegeo via FDW)           |
| status_id INTEGER NOT NULL -> stg_repd_cat_status(id)            |
| location_date DATE                                               |
| location_condition_id INTEGER -> stg_repd_cat_location_cond(id)  |
| location_classification_id INTEGER -> stg_repd_cat_loc_class(id) |
| location_state_name VARCHAR(100)                                 |
| location_municipality_id INTEGER (cvegeo via FDW)                |
| closure_date DATE                                                |
| closure_type_id INTEGER -> stg_repd_cat_closure_type(id)         |
| linked_feb VARCHAR(64)                                           |
| has_investigation_folder BOOLEAN                                 |
| record_hash VARCHAR(64) NOT NULL                                 |
| current_version INTEGER NOT NULL DEFAULT 1                       |
| created_at TIMESTAMP                                             |
| updated_at TIMESTAMP                                             |
+------------------------------------------------------------------+

+------------------------------------------------------------------+
|                     stg_repd_case_history                         |
|------------------------------------------------------------------|
| id SERIAL PK                                                     |
| case_current_id INTEGER -> stg_repd_case_current(id)             |
| feb VARCHAR(64) NOT NULL                                         |
| version_num INTEGER NOT NULL                                     |
| is_current BOOLEAN NOT NULL DEFAULT TRUE                         |
| valid_from TIMESTAMP NOT NULL                                    |
| valid_to TIMESTAMP                                               |
| (mismos campos de negocio que case_current)                      |
| record_hash VARCHAR(64) NOT NULL                                 |
| created_at TIMESTAMP                                             |
| UNIQUE (feb, version_num)                                        |
+------------------------------------------------------------------+

+------------------------------------+
| cvegeo_municipalities (FDW)        |
|------------------------------------|
| id INTEGER                         |
| cvegeo INTEGER                     |
| cve_ent INTEGER                    |
| cve_mun INTEGER                    |
| nomgeo VARCHAR                     |
| nom_ent VARCHAR                    |
+------------------------------------+
```

**Catalogos**: 7 tablas dinamicas (sex, nationality, age_range, status, location_condition, location_classification, closure_type). Se extraen del Excel y se sincronizan via ON CONFLICT DO NOTHING.

**Municipios**: Se resuelven contra `cvegeo_municipalities` (tabla foranea via FDW desde la BD `cvegeo`). La busqueda usa la tupla compuesta `(estado, municipio)` normalizada para evitar colisiones entre estados.

**Versionamiento SCD2**: `case_current` tiene la version vigente. `case_history` guarda snapshots con `version_num`, `is_current`, `valid_from` y `valid_to`. Los cambios se detectan comparando `record_hash` (SHA-256 de los campos de negocio).

## Flujo del pipeline

### Extract

1. Descarga el archivo XLSX desde la API del REPD
2. Valida que la respuesta no este vacia
3. Guarda el archivo con timestamp en `data/extract/repd/`

### Transform

1. Lee la hoja "DATOS" del Excel (header en fila 13)
2. Normaliza nombres de columnas (lowercase, sin acentos)
3. Limpia valores nulos (NO APLICA, NA, N/A)
4. Parsea fechas MM/YYYY a date con dia 1
5. Convierte carpeta de investigacion a boolean
6. Normaliza estados y municipios a UPPER
7. Extrae valores unicos para catalogos
8. Limpia carpetas de datos (extract + transform)

### Load

1. Inserta/sincroniza catalogos y construye caches name->id
2. Carga cache de municipios desde cvegeo via FDW
3. Resuelve IDs de catalogos y municipios en el DataFrame
4. Calcula record_hash por registro
5. **Bootstrap**: Inserta todos los registros en case_current y case_history (v1)
6. **Update**: Compara hashes, inserta nuevos, versiona cambios (SCD2)
7. Sincroniza secuencias y limpia carpeta de datos

## Periodicidad

Mensual (`0 3 1 * *`). El DAG de bootstrap es bajo demanda (schedule=None).

## Migraciones

- **V1**: FDW (postgres_fdw) + tablas catalogo
- **V2**: Tablas case_current y case_history con FKs
- **V3**: Vista analitica `stg_repd_case_current_vw` (joins a catalogos y municipios)
