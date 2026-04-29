# Pipeline: Pobreza Multidimensional

Indicadores municipales de pobreza multidimensional del CONEVAL para los años 2010, 2015 y 2020. Cubre las 2,469 localidades municipales de México con métricas de pobreza, carencias sociales y líneas de ingreso.

## Fuente

Medición de pobreza a nivel municipal publicada por el Consejo Nacional de Evaluación de la Política de Desarrollo Social (CONEVAL).

| Atributo | Valor |
|---|---|
| **URL** | [Concentrado_indicadores_de_pobreza_2020.zip](https://www.coneval.org.mx/Medicion/Documents/Pobreza_municipal/2020/Concentrado_indicadores_de_pobreza_2020.zip) |
| **Formato** | Excel (hoja `Concentrado municipal`, datos desde fila 9, encabezados multi-nivel filas 5-6) |
| **Registros** | ~7,407 (2,469 municipios × 3 años) |
| **Llave natural** | `(cve_mun, anio)` |
| **Periodicidad** | Bianual (nueva edición cada 2-3 años) |
| **Comportamiento** | sobreescribe — el archivo reemplaza a la versión anterior completa |

## Estructura

```
pobreza_multidimencional/
├── .env.example     # Variables de entorno con valores de ejemplo
├── config.py        # Settings del pipeline (extiende BaseConfig)
├── consts.py        # Constantes: EXCEL_COL_NAMES, INDICATOR_PREFIXES, NULL_VALUES, DATA_YEARS
├── schemas.py       # Modelos SQLAlchemy (CatEntidad, PobrezaMultidimencionalDatos)
└── stages/
    ├── extract.py   # Descarga ZIP y extrae XLSX
    ├── transform.py # Wide → tidy (municipio × año), extrae catálogos
    └── load.py      # Carga catálogos + datos en BD
```

Archivos relacionados:

- `dags/etl_pobreza_multidimencional.py` — DAG de Airflow (bootstrap, `schedule=None`)
- `migrations/pobreza_multidimencional/sql/` — Migraciones Flyway V1–V3
- `migrations/pobreza_multidimencional/flyway.conf.example` — Config de ejemplo

## Esquema de base de datos

```
+------------------------------------+     +-------------------------------------------+
| stg_pobreza_multidimencional_      |     | stg_pobreza_multidimencional_datos        |
| cat_entidad                        |     |-------------------------------------------|
|------------------------------------|     | id              SERIAL PK                 |
| id              SERIAL PK          |<----| cat_entidad_id  INTEGER FK                |
| cve_ent         VARCHAR(2) UNIQUE  |     | cve_mun         VARCHAR(5)                |
| nombre_entidad  VARCHAR(100)       |     | nombre_municipio VARCHAR(150)             |
+------------------------------------+     | anio            SMALLINT    -- 2010/15/20 |
                                           | poblacion       INTEGER                   |
                                           | pobreza_porcentaje / _personas / ...      |
                                           | [~46 columnas de indicadores]             |
                                           | UNIQUE (cve_mun, anio)                    |
                                           +-------------------------------------------+
```

**Vista analítica**: `vw_pobreza_multidimencional` — JOIN de `datos` + `cat_entidad`, expone todas las columnas de métricas con `nombre_municipio` y `nombre_entidad`.

**Catálogos**: 32 entidades sincronizadas vía `insert_records` con `ON CONFLICT DO NOTHING` usando `cve_ent` como llave.

**Estrategia de update**: `bootstrap_only` — la fuente sobreescribe completamente en cada edición. Re-ingestión completa vía `flyway-reset` + bootstrap.

## Indicadores disponibles

Cada indicador tiene 3 columnas: `_porcentaje` (FLOAT), `_personas` (INTEGER), y `_carencias_promedio` (FLOAT, excepto `vul_ingreso` y `no_pobre`).

| Indicador | Descripción |
|---|---|
| `pobreza` | Pobreza total |
| `pobreza_ext` | Pobreza extrema |
| `pobreza_mod` | Pobreza moderada |
| `vul_carencia` | Vulnerable por carencia social |
| `vul_ingreso` | Vulnerable por ingreso |
| `no_pobre` | No pobre y no vulnerable |
| `rez_edu` | Rezago educativo |
| `car_salud` | Carencia acceso a salud |
| `car_seg_soc` | Carencia seguridad social |
| `car_viv` | Carencia calidad de vivienda |
| `car_sbv` | Carencia servicios básicos de vivienda |
| `car_ali` | Carencia acceso a alimentación |
| `al_1_car` | Al menos una carencia social |
| `tres_mas_car` | Tres o más carencias sociales |
| `lpi` | Ingreso < línea de pobreza |
| `lpei` | Ingreso < línea de pobreza extrema |

## Arquitectura

Sigue el patrón de 3 etapas `Stage` → `Pipeline`:

```
PobrezaMultidimencionalExtract → PobrezaMultidimencionalTransform → PobrezaMultidimencionalLoad
```

| Etapa | Entrada | Salida |
|---|---|---|
| **Extract** | Ninguna | `{"file_path": str, "zip_path": str}` |
| **Transform** | `file_path` | `{"df": DataFrame, "catalogs": dict, "row_count": int}` |
| **Load** | `df` + `catalogs` | `{"row_count": int}` |

### Extract

1. Descarga el ZIP desde `POBREZA_MULTIDIMENCIONAL_SOURCE_URL` (timeout 180 s).
2. Extrae `Concentrado_indicadores_de_pobreza_2020.xlsx`.
3. Elimina el ZIP; guarda el XLSX en `data/extract/pobreza_multidimencional/`.

### Transform

1. Lee el XLSX (`skiprows=8`, `usecols=range(1,146)`) y asigna `EXCEL_COL_NAMES`.
2. Filtra filas donde `cve_mun` no sea un código de 5 dígitos.
3. Aplica `NULL_VALUES`; convierte métricas `_personas` a `Int64` y porcentajes a `float`.
4. Pivota de formato wide a tidy: 3 DataFrames (uno por año) → concatena → 7,407 filas.
5. Extrae catálogo de entidades federativas (32 entidades únicas).

### Load

1. Sincroniza `cat_entidad` con `insert_records` (conflict key: `cve_ent`).
2. Construye mapa `cve_ent → cat_entidad_id`.
3. Resuelve `cat_entidad_id` en el DataFrame.
4. `bulk_insert` en lotes de `POBREZA_MULTIDIMENCIONAL_LOAD_BATCH_SIZE` (default 2,000).
5. Sincroniza secuencias SERIAL.

## Periodicidad

- **Bootstrap**: `schedule=None`, ejecución bajo demanda. Corre `run_bootstrap()` al ejecutar `python dags/etl_pobreza_multidimencional.py` directamente.

## Setup local

```bash
# 1. Copiar y completar variables de entorno
cp core/pipelines/pobreza_multidimencional/.env.example \
   core/pipelines/pobreza_multidimencional/.env

# 2. Aplicar migraciones
just flyway-reset pobreza_multidimencional

# 3. Ejecutar bootstrap
conda activate etl
python dags/etl_pobreza_multidimencional.py
```
