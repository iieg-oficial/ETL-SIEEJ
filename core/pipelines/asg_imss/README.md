# Pipeline: ASG IMSS

Pipeline ETL para los datos de asegurados al IMSS publicados en el portal de datos abiertos del IMSS (ASG — Asegurados por Género). Descarga, transforma y carga mensualmente los registros de trabajadores asegurados en Jalisco.

## Fuente

El IMSS publica mensualmente archivos CSV con el universo de asegurados permanentes y eventuales, desglosados por delegación, municipio, sector económico, tamaño del patrón, sexo, rango de edad, rango salarial y rango UMA. El archivo nacional contiene ~4.6 millones de filas; este pipeline filtra únicamente los registros de Jalisco (`cve_entidad == 14`), que representan ~449 mil filas por mes.

- **URL**: `http://datos.imss.gob.mx/sites/default/files/asg-{YYYY-MM-DD}.csv`
- **Formato**: CSV con separador `|`, ~4.6 M filas nacionales por mes
- **Alcance**: Solo Jalisco (`cve_entidad = 14`), ~449 K filas por mes
- **Frecuencia de actualización**: Mensual (último día del mes)
- **Disponibilidad histórica**: desde `2015-01-31`

## Estructura

```
asg_imss/
├── .env.example     # Variables de entorno con valores de ejemplo
├── config.py        # Settings del pipeline (extiende BaseConfig)
├── consts.py        # Constantes: URL, campos de hash, catálogos estáticos
├── schemas.py       # Modelos SQLAlchemy (12 tablas)
└── stages/
    ├── extract.py   # Descarga CSVs mensuales del portal IMSS
    ├── transform.py # Filtrado por entidad, tipado, hash y extracción de catálogos
    └── load.py      # Carga catálogos y upsert de datos por record_hash
```

Archivos relacionados fuera de este directorio:

- `dags/etl_asg_imss.py` — DAGs de Airflow (bootstrap + update mensual)
- `migrations/asg_imss/sql/` — Migración Flyway para crear las tablas
- `migrations/asg_imss/flyway.conf.example` — Configuración de ejemplo para Flyway

## Arquitectura

Sigue el patrón de 3 etapas del framework (`Stage` → `Pipeline`):

```
AsgImssExtractor → AsgImssTransformer → AsgImssLoader
```

Cada etapa implementa `source()`, `action()`, `finalization()` del ABC `Stage`. El `Pipeline` encadena las etapas secuencialmente, pasando datos entre ellas.

### Flujo de datos entre etapas

| Etapa | Entrada | Salida |
|-------|---------|--------|
| **Extract** | Ninguna | Lista de archivos descargados (rutas a CSVs) |
| **Transform** | Lista de CSVs | Pickles por mes + catálogos dinámicos (listas de dicts) |
| **Load** | Pickles + catálogos | Estadísticas de upsert |

Los CSVs nacionales nunca se procesan completos en memoria más allá de la etapa Transform: se leen, se filtran a Jalisco, se serializan como pickle y se liberan.

## Tablas

El pipeline gestiona 12 tablas en PostgreSQL: 11 catálogos y 1 tabla principal de datos.

### Catálogos estáticos (definidos en `consts.py`)

| Tabla | Clave única | Descripción |
|-------|-------------|-------------|
| `stg_asg_imss_cat_tamanio_patron` | `cve` | Tamaño del patrón por rango de puestos (S1–S7) |
| `stg_asg_imss_cat_sexo` | `cve` | Sexo del asegurado (1=Hombre, 2=Mujer, 3=No especificado) |
| `stg_asg_imss_cat_rango_edad` | `cve` | Rango de edad (E1–E14, de menores de 15 a 75+ años) |
| `stg_asg_imss_cat_rango_salarial` | `cve` | Rango salarial en múltiplos del salario mínimo (W1–W11) |
| `stg_asg_imss_cat_rango_uma` | `cve` | Rango salarial en múltiplos de la UMA (W1–W25) |

### Catálogos dinámicos (extraídos de los CSVs en bootstrap)

| Tabla | Clave única | Descripción |
|-------|-------------|-------------|
| `stg_asg_imss_cat_delegacion` | `cve_delegacion` | Delegaciones del IMSS presentes en el archivo fuente |
| `stg_asg_imss_cat_subdelegacion` | `(cve_delegacion, cve_subdelegacion)` | Subdelegaciones por delegación |
| `stg_asg_imss_cat_entidad_municipio` | `cve_municipio` | Municipios con su clave de entidad y delegación |
| `stg_asg_imss_cat_sector_1` | `cve_sector_1` | Sectores económicos de primer nivel |
| `stg_asg_imss_cat_sector_2` | `(cve_sector_1, cve_sector_2)` | Subsectores (segundo nivel) |
| `stg_asg_imss_cat_sector_4` | `(cve_sector_2, cve_sector_4)` | Fracciones SCIAN (cuarto nivel) |

### Tabla principal

| Tabla | Clave única | Descripción |
|-------|-------------|-------------|
| `stg_asg_imss_datos` | `record_hash` | Registro mensual de asegurados por combinación de dimensiones |

La tabla principal tiene 14 columnas de dimensiones, 12 métricas enteras (conteos de trabajadores) y 5 métricas de punto flotante (masa salarial). El `record_hash` es un SHA-256 calculado sobre 13 campos dimensionales + `fecha_corte`.

**Columnas métricas enteras**: `asegurados`, `no_trabajadores`, `ta`, `teu`, `tec`, `tpu`, `tpc`, `ta_sal`, `teu_sal`, `tec_sal`, `tpu_sal`, `tpc_sal`

**Columnas de masa salarial** (NUMERIC 16,2): `masa_sal_ta`, `masa_sal_teu`, `masa_sal_tec`, `masa_sal_tpu`, `masa_sal_tpc`

## Flujo del pipeline

### Extract

1. Calcula las fechas objetivo según el modo (ver [Modos del pipeline](#modos-del-pipeline)).
2. Omite archivos que ya existen en `data/extract/asg_imss/`.
3. Descarga cada CSV desde `http://datos.imss.gob.mx/sites/default/files/asg-{fecha}.csv`.
4. Detecta el encoding de la respuesta (UTF-8 → latin-1 → UTF-8 con sustitución).
5. Guarda cada archivo normalizado a UTF-8 en disco.
6. Respeta un intervalo de 3 segundos entre descargas para evitar detección como bot.

### Transform

1. Lee cada CSV con fallback de encoding (UTF-8 → latin-1).
2. Renombra `tamaño_patron` → `tamanio_patron` (normalización de `ñ`).
3. Filtra únicamente los registros donde `cve_entidad == 14` (Jalisco).
4. Convierte columnas métricas enteras a `int` (NaN → 0) y flotantes a `float` (NaN → 0.0).
5. Convierte columnas dimensionales numéricas a tipo numérico; las categóricas (sector económico) se dejan como nullable.
6. Agrega `fecha_corte` como tipo `date` derivado del nombre del archivo.
7. Calcula `record_hash` (SHA-256) sobre los 13 campos dimensionales + `fecha_corte`.
8. Convierte NaN restantes a `None` para compatibilidad con PostgreSQL.
9. Extrae catálogos dinámicos (delegaciones, subdelegaciones, municipios, sectores) acumulando valores únicos de todos los archivos procesados.
10. Serializa el DataFrame transformado como pickle en `data/transform/asg_imss/`.

### Load

1. Verifica y crea las tablas con `metadata.create_all()` si no existen.
2. **Solo en modo bootstrap**: carga los catálogos estáticos (`ON CONFLICT DO NOTHING`) y los catálogos dinámicos acumulados en Transform.
3. Para cada pickle, lee el DataFrame y aplica upsert sobre `stg_asg_imss_datos` por `record_hash`.
4. Elimina los pickles intermedios al finalizar (`clean_directory`).

## Modos del pipeline

| Modo | Fechas procesadas | Catálogos | Cuándo ejecutar |
|------|-------------------|-----------|-----------------|
| **bootstrap** | `2015-01-31` → último día del mes anterior | Se cargan en este paso | Una sola vez (carga inicial) |
| **update** | Solo el último día del mes anterior | No se recargan | Mensualmente (DAG automático) |

La fecha de inicio del bootstrap se controla con `ASG_START_DATE` (default: `2015-01-31`).

El extractor omite automáticamente archivos ya descargados, por lo que es seguro reejecutar el bootstrap sin duplicar descargas.

## Variables de entorno

Ver [.env.example](.env.example) para la plantilla completa. Las variables configurables son:

| Variable | Default | Descripción |
|----------|---------|-------------|
| `DB_USER` | — | Usuario de PostgreSQL |
| `DB_PASSWORD` | — | Contraseña de PostgreSQL |
| `DB_HOST` | `localhost` | Host de PostgreSQL |
| `DB_PORT` | `5432` | Puerto de PostgreSQL |
| `DB_NAME` | `asg_imss` | Base de datos de destino |
| `ASG_DOWNLOAD_TIMEOUT` | `300` | Timeout HTTP por descarga (segundos) |
| `ASG_DOWNLOAD_MAX_RETRIES` | `3` | Reintentos por archivo fallido |
| `ASG_LOAD_BATCH_SIZE` | `50000` | Filas por batch en upsert |
| `ASG_START_DATE` | `2015-01-31` | Fecha de inicio del bootstrap |
| `LOG_LEVEL` | `INFO` | Nivel de logging |

## Cómo ejecutar

### Bootstrap (carga inicial)

```bash
# 1. Configurar variables de entorno
cp core/pipelines/asg_imss/.env.example core/pipelines/asg_imss/.env
# Editar .env con los valores reales

# 2. Configurar Flyway y ejecutar migraciones
just flyway-config asg_imss
# Editar migrations/asg_imss/flyway.conf con la URL de conexión real
just flyway-migrate asg_imss

# 3. Ejecutar el DAG bootstrap desde Airflow (On Demand)
#    DAG: etl_asg_imss_bootstrap
```

### Update incremental (mes anterior)

El DAG `etl_asg_imss_update` se ejecuta automáticamente el día 1 de cada mes a las 06:00. Para ejecutarlo manualmente desde Airflow, activar y disparar el DAG desde la interfaz.

### Airflow

| Acción | DAG |
|--------|-----|
| Carga inicial completa | `etl_asg_imss_bootstrap` (trigger manual) |
| Actualización mensual | `etl_asg_imss_update` (schedule automático) |

## Programación

| DAG | Schedule | Trigger | Descripción |
|-----|----------|---------|-------------|
| `etl_asg_imss_bootstrap` | Sin schedule | Manual / On Demand | Carga histórica completa desde 2015 |
| `etl_asg_imss_update` | `0 6 1 * *` | Automático | Carga incremental el 1° de cada mes a las 06:00 |

El DAG de update descarga y procesa únicamente el archivo del último día del mes anterior.

## Migraciones

- **V1** (`V1__tablas_iniciales.sql`): Crea las 11 tablas catálogo y la tabla principal `stg_asg_imss_datos` con sus constraints únicos e índices.

Ver `migrations/asg_imss/flyway.conf.example` para la configuración de Flyway.

## Notas técnicas

- **Encoding**: El extractor intenta decodificar la respuesta HTTP como UTF-8; si falla, reintenta con latin-1; si vuelve a fallar, usa UTF-8 con sustitución de caracteres inválidos. El archivo siempre se escribe a disco en UTF-8. El transformer aplica la misma cascada al leer los CSVs del disco.
- **Normalización de columna con ñ**: El CSV fuente incluye la columna `tamaño_patron`; el transformer la renombra a `tamanio_patron` antes de procesar.
- **Estrategia de hash**: El `record_hash` es un SHA-256 sobre la concatenación ordenada de los 13 campos dimensionales (`fecha_corte`, `cve_delegacion`, `cve_subdelegacion`, `cve_entidad`, `cve_municipio`, `sector_economico_1`, `sector_economico_2`, `sector_economico_4`, `tamanio_patron`, `sexo`, `rango_edad`, `rango_salarial`, `rango_uma`). Esto garantiza idempotencia en los upserts: una misma combinación de dimensiones para el mismo mes siempre produce el mismo hash.
- **Conversión de NaN**: Los valores `float NaN` de pandas se convierten explícitamente a `None` antes del upsert para evitar errores de tipo en columnas nullable de PostgreSQL.
- **Catálogos dinámicos solo en bootstrap**: Delegaciones, subdelegaciones, municipios y sectores se extraen de los datos del CSV y se insertan únicamente durante el bootstrap (`ON CONFLICT DO NOTHING`). Las ejecuciones de update no los re-sincronizan.
- **Descarga robusta**: El extractor respeta un sleep de 3 segundos entre archivos consecutivos y retries con backoff de 3 segundos para evitar bloqueos en el servidor del IMSS.
- **Volumen de datos verificado**: 448,951 filas de Jalisco para `fecha_corte = 2025-03-31`.
