# Pipeline: Censos Económicos

Pipeline ETL para los Censos Económicos de INEGI (datos abiertos). Descarga, limpia y carga los datos censales en PostgreSQL.

## Fuente

Los Censos Económicos son el proyecto estadístico más grande de México sobre actividad económica. Se realizan cada 5 años por INEGI y cubren todas las unidades económicas del país, capturando variables como personal ocupado, producción, ingresos, gastos y activos fijos por sector, municipio y tamaño de empresa. Los datos abiertos incluyen microdatos a nivel establecimiento con clasificación [SCIAN](https://www.inegi.org.mx/scian/).

Más información y descarga directa: https://www.inegi.org.mx/programas/ce/2024/

## Estructura

```
censos_economicos/
├── .env.example     # Variables de entorno con valores de ejemplo
├── config.py        # Settings del pipeline (extiende BaseConfig)
├── consts.py        # Constantes: slugs, URLs, columnas económicas
├── schemas.py       # Modelos SQLAlchemy (6 tablas)
└── stages/
    ├── extract.py   # Descarga y extracción de ZIPs desde INEGI
    ├── transform.py # Limpieza de catálogos y validación de CSVs
    └── load.py      # Carga de catálogos y datos a PostgreSQL
```

Archivos relacionados fuera de este directorio:

- `dags/etl_censos_economicos.py` — DAG de Airflow (bootstrap + update anual)
- `migrations/censos_economicos/sql/` — Migraciones Flyway para establecer las tablas
- `migrations/censos_economicos/flyway.conf.example` — Configuración de ejemplo para Flyway

## Arquitectura

Sigue el patrón de 3 etapas del framework (`Stage` → `Pipeline`):

```
CEExtractor → CETransformer → CELoader
```

Cada etapa implementa `source()`, `action()`, `finalization()` del ABC `Stage`. El `Pipeline` encadena las etapas secuencialmente, pasando datos entre ellas.

### Flujo de datos entre etapas

| Etapa | Entrada | Salida |
|-------|---------|--------|
| **Extract** | Ninguna | Inventario de archivos (rutas a CSVs por año/slug) |
| **Transform** | Inventario | Catálogos limpios (listas de dicts) + rutas a CSVs de datos |
| **Load** | Catálogos + rutas | Estadísticas de carga |

Los CSVs de datos nunca se cargan completos en memoria entre etapas — se procesan uno por uno en el Loader para mantener el consumo de memoria acotado.

## Tablas

| Tabla | Tipo | Constraint único |
|-------|------|------------------|
| `ce_catalogos_actividades` | Catálogo | `codigo` |
| `ce_catalogos_entidades_municipios` | Catálogo | `cvegeo` |
| `ce_catalogos_estratos` | Catálogo | `id_estrato` |
| `ce_diccionarios_datos` | Referencia | `(anio, nombre_columna)` |
| `ce_archivos_fuente` | Metadata | `(anio, slug, tipo_archivo)` |
| `ce_datos` | Fact table | `(anio, e03, e04, codigo, id_estrato)` |

La tabla principal (`ce_datos`) tiene 98 columnas de variables económicas (`Float`, nullable — `NULL` indica dato confidencial suprimido por INEGI).

## Utilidades del framework reutilizadas

- `insert_records()` — Inserción de catálogos con ON CONFLICT DO NOTHING
- `sync_id_sequence()` — Sincronización de secuencias PG después de cargas masivas
- `lowercase_headers()` — Normalización de encabezados CSV
- `list_values_to_null()` — Limpieza de valores vacíos/NA → None

## Configuración

Variables en `.env` (ver `.env.example` y `config.py`):

| Variable | Default | Descripción |
|----------|---------|-------------|
| `CE_DOWNLOAD_MAX_WORKERS` | 4 | Hilos concurrentes de descarga |
| `CE_DOWNLOAD_TIMEOUT` | 120 | Timeout HTTP en segundos |
| `CE_DOWNLOAD_MAX_RETRIES` | 3 | Reintentos por descarga |
| `CE_DOWNLOAD_RETRY_BACKOFF` | 5.0 | Backoff inicial en segundos (se duplica por reintento) |
| `CE_LOAD_BATCH_SIZE` | 5000 | Filas por batch en INSERT |
| `CE_YEARS` | 2024 | Años censales a procesar (separados por coma) |

Hereda `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` de `BaseConfig`.

Para migraciones Flyway, ver `migrations/censos_economicos/flyway.conf.example`.

## Extensión a otros años censales

Para agregar un año censal (ej. 2019):

1. Agregar una nueva entrada `2019` en `CE_YEARS_CONFIG` en `consts.py` con la URL template, slugs y patrones de archivo correspondientes (todo autocontenido en la entrada)
2. Actualizar `.env`: `CE_YEARS=2019,2024`

No se requieren cambios en las etapas ni en el DAG.
