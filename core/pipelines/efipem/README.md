# Pipeline: EFIPEM (Estadística de Finanzas Públicas Estatales y Municipales)

Ingresos y egresos trimestrales del gobierno del estado de Jalisco publicados por INEGI, limitado al nivel entidad federativa.

## Fuente

Publicación trimestral de INEGI con los datos CRI (ingresos), CEG (egresos por clasificación económica) y CFG (egresos por clasificación funcional).

| Atributo | Valor |
|---|---|
| **URL / Origen** | `https://www.inegi.org.mx/contenidos/programas/finanzas/datosabiertos/conjunto_de_datos_efipem_trimestral_csv.zip` |
| **Formato** | ZIP → CSV (`conjunto_de_datos/efipem_trimestral_tr_cifra_<rango>.csv`) |
| **Registros aprox.** | ~19,500 (32 entidades × 12 trimestres) — ~612 tras filtrar Jalisco |
| **Llave natural** | `(anio, trimestre, cve_ent, tema, clasificador, concepto)` |
| **Periodicidad** | Trimestral |
| **Comportamiento** | `sobreescribe` — cada publicación reemplaza el periodo completo |

Datos restringidos a `cve_ent='14'` (Jalisco) en transform.

## Estructura

```
efipem/
├── .env.example     # Variables de entorno con valores de ejemplo
├── config.py        # Settings del pipeline (extiende BaseConfig)
├── consts.py        # PIPELINE_NAME, NULL_VALUES, COLUMN_RENAME_MAP, CATALOG_COLUMNS, CLASIFICADOR_NORMALIZATION, SOURCE_CSV_GLOB
├── schemas.py       # Modelos SQLAlchemy (EfipemBase)
└── stages/
    ├── extract.py   # EfipemExtractor
    ├── transform.py # EfipemTransformer
    └── load.py      # EfipemLoader
```

Archivos relacionados fuera del directorio:

- `dags/etl_efipem.py` — DAGs de Airflow (bootstrap + update trimestral)
- `migrations/efipem/sql/` — Migraciones Flyway V1–V4
- `migrations/efipem/flyway.conf.example` — Config de ejemplo con placeholders FDW

## ERD

![ERD](assets/erd.svg)

```
+-----------------------------+          +-----------------------------------+
| stg_efipem_cat_trimestre    |          | stg_efipem_finanzas_trimestral    |
|-----------------------------|          |-----------------------------------|
| id SERIAL PK                |<----+    | id SERIAL PK                      |
| name VARCHAR(10) UNIQUE     |     |    | anio INTEGER                      |
+-----------------------------+     +----| trimestre_id INTEGER FK           |
                                         | cve_ent CHAR(2)                   |
+-----------------------------+          | entidad_id INTEGER (cvegeo FDW)   |
| stg_efipem_cat_tema         |     +----| tema_id INTEGER FK                |
|-----------------------------|     |    | clasificador_id INTEGER FK -------+--+
| id SERIAL PK                |<----+    | concepto_id INTEGER FK               |
| name VARCHAR(50) UNIQUE     |          | valor BIGINT                         |
+-----------------------------+          | estatus_id INTEGER FK -----+         |
                                         | created_at / updated_at    |         |
+-----------------------------+          +----------------------------|---------|
| stg_efipem_cat_clasificador |<---------+                            |         |
|-----------------------------|                                       |         |
| id SERIAL PK                |                                       |         |
| name VARCHAR(200) UNIQUE    |                                       |         |
+-----------------------------+                                       |         |
         ^                                                            |         |
         |                                                            |         |
+-----------------------------+                                       |         |
| stg_efipem_cat_concepto     |                                       |         |
|-----------------------------|                                       |         |
| id SERIAL PK                |<--------------------------------------+         |
| clasificador_id INTEGER FK  |                                                 |
| name VARCHAR(255)           |                                                 |
| UNIQUE(clasificador_id,name)|                                                 |
+-----------------------------+                                                 |
                                                                                |
+-----------------------------+                                                 |
| stg_efipem_cat_estatus      |<------------------------------------------------+
|-----------------------------|
| id SERIAL PK                |
| name VARCHAR(50) UNIQUE     |
+-----------------------------+

+-----------------------------+
| cvegeo_states (FDW)         |
|-----------------------------|
| id INTEGER                  |<---- entidad_id (referencia lógica, sin FK)
| cve_ent INTEGER             |
| nom_ent VARCHAR             |
+-----------------------------+
```

**Catálogos**: los cuatro simples (`trimestre`, `tema`, `clasificador`, `estatus`) se sincronizan con `insert_records(..., conflict_keys=["name"])`. `concepto` depende de `clasificador_id` y se sincroniza con `conflict_keys=["clasificador_id", "name"]`.

**Entidad cvegeo**: `cve_ent` (char(2)) se mapea a `cvegeo_states.id` vía FDW. No se crea FK física hacia la foreign table; `entidad_id` es una referencia lógica.

**Estrategia de update**: `bootstrap_only`-like con re-ingesta total. Como la fuente sobrescribe el periodo completo cada publicación, el modo `update` ejecuta `TRUNCATE ... RESTART IDENTITY` sobre `stg_efipem_finanzas_trimestral` y vuelve a cargar; los catálogos se preservan con `ON CONFLICT DO NOTHING`.

## Arquitectura

```
EfipemExtractor → EfipemTransformer → EfipemLoader
```

### Flujo entre etapas

| Etapa | Entrada | Salida |
|---|---|---|
| **Extract** | Ninguna | `{"file_path": str, "zip_path": str}` |
| **Transform** | `file_path` | `{"df": DataFrame, "catalogs": {...}, "concepto_pairs": [...], "row_count": N}` |
| **Load** | df + catálogos + pares concepto | `{"mode": str, "inserted": N}` |

## Flujo del pipeline

### Extract
1. Descarga el ZIP desde `EFIPEM_SOURCE_URL` (timeout 300s).
2. Extrae el ZIP en `data/extract/efipem/`.
3. Localiza el CSV de cifras con el patrón `conjunto_de_datos/efipem_trimestral_tr_cifra_*.csv`.
4. Retorna la ruta al CSV (no lo limpia: lo consume Transform).

### Transform
1. Lee el CSV como `dtype=str` (UTF-8).
2. Normaliza headers a minúsculas y aplica `COLUMN_RENAME_MAP` (`DESCRIPCION_CLASIFICADOR` → `concepto`).
3. Limpia `NULL_VALUES`.
4. Zero-pad de `cvegeo` y `cve_ent` a 2 dígitos.
5. **Filtra `cve_ent == '14'`** (Jalisco) — ~19,584 → ~612 filas.
6. Normaliza `clasificador` mediante `CLASIFICADOR_NORMALIZATION` (unifica em-dash y corrige `CEG-` → `CEG –`).
7. Tipa `anio` a `int` y `valor` a `int64` (BIGINT).
8. Extrae catálogos simples (`trimestre`, `tema`, `clasificador`, `estatus`) y los pares compuestos `(clasificador, concepto)`.
9. Limpia `data/extract/efipem/` y `data/transform/efipem/` en `finalization`.

### Load
1. `EfipemBase.metadata.create_all` como red de seguridad.
2. Sincroniza los 4 catálogos simples (`insert_records` on conflict do nothing) y construye caches `name → id`.
3. Sincroniza `stg_efipem_cat_concepto` usando `(clasificador_id, name)` como llave de conflicto.
4. Carga cache `cve_ent (zfill 2) → cvegeo_states.id` desde el FDW.
5. Resuelve en el DataFrame `trimestre_id`, `tema_id`, `clasificador_id`, `concepto_id`, `estatus_id`, `entidad_id`.
6. Valida que ningún FK obligatorio quede nulo (falla si encuentra alguno).
7. En modo `update`: `TRUNCATE TABLE stg_efipem_finanzas_trimestral RESTART IDENTITY`.
8. `bulk_insert` en chunks de `EFIPEM_LOAD_BATCH_SIZE`.
9. Sincroniza las 6 secuencias `SERIAL` en `finalization`.

## Periodicidad

Dos DAGs en `dags/etl_efipem.py`:

- **Bootstrap** (`etl_efipem_bootstrap`): `schedule=None`, bajo demanda.
- **Update** (`etl_efipem_update`): `"0 2 15 2,5,8,11 *"` — día 15 de febrero, mayo, agosto y noviembre a las 02:00 (mes medio de cada trimestre, ventana razonable tras la publicación de INEGI).

## Configuración

Variables en `.env` (ver `.env.example` y `config.py`):

| Variable | Default | Descripción |
|---|---|---|
| `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` / `DB_NAME` | `postgres` / `postgres` / `localhost` / `5432` / `sieej` | Conexión a PostgreSQL |
| `EFIPEM_SOURCE_URL` | URL oficial INEGI | ZIP de cifras trimestrales |
| `EFIPEM_LOAD_BATCH_SIZE` | `5000` | Filas por chunk en `bulk_insert` |
| `EFIPEM_CVE_ENT_FILTER` | `14` | Entidad a retener en transform (Jalisco) |
| `LOG_LEVEL` | `INFO` | Nivel de log |

Para migraciones Flyway, ver `migrations/efipem/flyway.conf.example` (incluye placeholders `fdw_*` para el FDW hacia la BD `cvegeo`).

## Migraciones

- **V1** `foreign_tables_efipem` — `CREATE EXTENSION postgres_fdw`, servidor `cvegeo_server`, user mapping y foreign table `cvegeo_states`.
- **V2** `catalogos_efipem` — 5 tablas catálogo (`trimestre`, `tema`, `clasificador`, `concepto`, `estatus`).
- **V3** `tabla_stg_efipem` — `stg_efipem_finanzas_trimestral` con FKs, `UNIQUE` compuesto e índices.
- **V4** `vista_efipem` — vista `stg_efipem_finanzas_trimestral_vw` que resuelve catálogos y entidad (join a `cvegeo_states`).

## Utilidades reutilizadas

- `core.utils.bulk_ops`: `insert_records`, `bulk_insert`, `get_mapping`, `sync_id_sequence`
- `core.utils.clean.list_values_to_null` — limpieza de nulos
- `core.utils.files.clean_directory` — limpieza de directorios entre stages

## Notas

- El CSV mezcla `em-dash` (`–`) y `hyphen` (`-`) en los valores de `CLASIFICADOR`; `CLASIFICADOR_NORMALIZATION` canoniza todos a `em-dash` con espacios para evitar duplicados en el catálogo.
- `VALOR` se tipa como `BIGINT` porque el máximo observado (~3.58 × 10¹¹) excede `INT4`.
- `cvegeo` y `cve_ent` del CSV son redundantes a nivel entidad (idénticos); se conserva `cve_ent` como columna final.
