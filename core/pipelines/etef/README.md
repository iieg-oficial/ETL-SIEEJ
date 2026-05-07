# Pipeline: ETEF — Exportaciones Trimestrales por Entidad Federativa

Exportaciones trimestrales de la Industria Manufacturera, Maquiladora y de Servicios de Exportación
(IMMEX) por entidad federativa y subsector SCIAN, publicadas por INEGI desde 2007.
Cobertura **nacional (32 estados)**; actualización trimestral con estrategia **SCD2**.

---

## Fuente

| Campo | Valor |
|---|---|
| **Proveedor** | INEGI |
| **URL** | `https://www.inegi.org.mx/contenidos/programas/exporta_ef/datosabiertos/conjunto_de_datos_eef_trimestral_csv.zip` |
| **Formato** | ZIP → CSV (UTF-8, separador `,`) |
| **Registros** | ~65,664 (histórico 2007-I a 2025-IV, todas las entidades) |
| **Periodicidad** | Trimestral |
| **Credenciales** | No requeridas (archivo público) |

El ZIP contiene el CSV `conjunto_de_datos/eef_trimestral_tr_cifra_2007_2025.csv` con el
histórico completo. La fuente es detección dinámica: si el nombre cambia, se selecciona
cualquier CSV en `conjunto_de_datos/`.

---

## Esquema de base de datos

### Tablas catálogo

| Tabla | Descripción |
|---|---|
| `stg_etef_cat_codigo_scian` | 27 subsectores SCIAN; columnas: `id`, `codigo` (UNIQUE), `descripcion`, `version` |

### Tabla principal

| Tabla | Descripción |
|---|---|
| `stg_etef_datos` | Exportaciones con SCD2. Llave natural: `(anio, trimestre, cve_ent, codigo_scian_id)`. Columnas mutables: `val_usd`, `estatus_cifra`, `estatus`. |

Columnas de `stg_etef_datos`:

```
id              SERIAL PK
anio            INTEGER
trimestre       VARCHAR(2)          -- e.g. "T1", "T2", "T3", "T4"
mes             VARCHAR(5)
prod_est        VARCHAR(150)
cobertura       VARCHAR(50)
cve_ent         INTEGER             -- clave INEGI de entidad federativa
codigo_scian_id INTEGER FK → stg_etef_cat_codigo_scian.id
val_usd         NUMERIC(15,2)       -- ~50% nulos (cifras no disponibles)
estatus_cifra   VARCHAR(20)
estatus         VARCHAR(30)
-- SCD2
row_hash        VARCHAR(64)         -- SHA-256 de val_usd|estatus_cifra|estatus
valid_from      TIMESTAMPTZ
valid_to        TIMESTAMPTZ         -- NULL cuando is_current = TRUE
is_current      BOOLEAN
-- Auditoría
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

Índices clave:

- `uq_etef_datos_llave_activa` — UNIQUE parcial `(anio, trimestre, cve_ent, codigo_scian_id)` WHERE `is_current = TRUE`
- `ix_etef_datos_anio_trimestre`, `ix_etef_datos_cve_ent`, `ix_etef_datos_codigo_scian_id`
- `ix_etef_datos_is_current`, `ix_etef_datos_row_hash`

### Vista de integración

| Vista | Descripción |
|---|---|
| `vw_etef_datos` | Expone únicamente registros activos (`is_current = TRUE`). JOIN con `stg_etef_cat_codigo_scian` (subsector) y `cvegeo_municipalities` (nombre de entidad vía FDW). |

La vista incluye: `anio`, `trimestre`, `mes`, `prod_est`, `cobertura`, `cve_ent`, `cvegeo`,
`nom_ent`, `codigo_scian`, `subsector`, `version_scian`, `val_usd`, `estatus_cifra`,
`estatus`, columnas SCD2 y auditoría.

---

## Estrategia SCD2

### Qué se versiona

| Columna mutable | Tipo | Descripción |
|---|---|---|
| `val_usd` | NUMERIC | Valor de exportación en USD. INEGI publica revisiones históricas. |
| `estatus_cifra` | VARCHAR | Estado de la cifra (p.ej. "Definitiva", "Preliminar"). |
| `estatus` | VARCHAR | Estatus del registro en la fuente. |

### Cálculo del hash

En `transform.py`:

```python
hash_input = df[["val_usd", "estatus_cifra", "estatus"]].fillna("").astype(str).agg("|".join, axis=1)
df["row_hash"] = hash_input.apply(lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest())
```

Se concatenan las tres columnas mutables con `|` como separador y se aplica SHA-256.

### Cuándo se abre/cierra una versión

En `load.py` (modo `update`):

1. Se cargan todos los registros activos (`is_current = TRUE`) a memoria.
2. Para cada fila del DataFrame transformado:
   - **Llave no encontrada** → INSERT nuevo registro (`is_current=True`, `valid_to=NULL`).
   - **Llave encontrada, hash igual** → Sin cambios (skip).
   - **Llave encontrada, hash diferente** → Se **cierra** la versión activa (`is_current=False`, `valid_to=NOW()`) y se inserta una nueva versión activa.
3. El índice parcial `uq_etef_datos_llave_activa` garantiza que solo exista una versión `is_current=TRUE` por llave natural.

### Modo bootstrap

Inserta todos los registros históricos como versión inicial con `is_current=True` y `valid_from=NOW()`.
No hay versiones cerradas en el bootstrap.

---

## Implementación ETL

| Modo | Implementado | Estrategia |
|---|:---:|---|
| Bootstrap | ✅ | Carga completa 2007-I a 2025-IV |
| Update | ✅ | SCD2 (cerrar versión cambiada + nueva versión) |

### Extract

1. Descarga el ZIP desde `ETEF_SOURCE_URL` (timeout 180 s).
2. Detecta dinámicamente el CSV dentro del ZIP (prefiere `conjunto_de_datos/`).
3. Escribe el CSV en `data/extract/etef/etef_<timestamp>.csv`.
4. Elimina el ZIP local.

### Transform

1. Lee el CSV completo (UTF-8) en un `DataFrame` con dtype `str`.
2. Normaliza headers a `snake_case` vía `normalize_col` y aplica `COLUMN_RENAME_MAP`.
3. Sustituye valores en `NULL_VALUES` (`"NO APLICA"`, `"NA"`, `"N/A"`, `""`, etc.) por `None`.
4. Convierte tipos: `anio` → `Int64`, `cve_ent` → `Int64`, `val_usd` → `float`.
5. Calcula `row_hash` SHA-256 sobre columnas mutables (`val_usd|estatus_cifra|estatus`).
6. Extrae valores únicos del catálogo `codigo_scian`.
7. Construye columna `llave_natural` para trazabilidad en logs.
8. Sanitiza `NaN`/`NaT` residuales a `None`.

### Load

1. Crea/verifica las tablas SQLAlchemy contra la BD.
2. Sincroniza catálogo `codigo_scian` (INSERT … ON CONFLICT DO NOTHING).
3. Construye mapa `codigo → id` y resuelve `codigo_scian_id` en el DataFrame.
4. **Bootstrap**: `bulk_insert` directo (batches de `ETEF_LOAD_BATCH_SIZE`).
5. **Update**: SCD2 — cierra versiones modificadas y hace `bulk_insert` de nuevas versiones.
6. Sincroniza secuencias SERIAL de todas las tablas.

---

## Migraciones Flyway

| Versión | Archivo | Descripción |
|---|---|---|
| V1 | `V1__catalogos.sql` | Crea `stg_etef_cat_codigo_scian` con índice en `codigo`. |
| V2 | `V2__cvegeo.sql` | Instala `postgres_fdw`, define `cvegeo_server` y foreign table `cvegeo_municipalities`. |
| V3 | `V3__tabla_principal.sql` | Crea `stg_etef_datos` (sin SCD2 aún) con 4 índices analíticos. |
| V4 | `V4__vista.sql` | Vista `vw_etef_datos` sin columnas SCD2 (versión pre-SCD2). |
| V5 | `V5__scd2_etef.sql` | Agrega `prod_est`, `cobertura`, `row_hash`, `valid_from`, `valid_to`, `is_current`; reemplaza UNIQUE plano por índice parcial `uq_etef_datos_llave_activa`. |
| V6 | `V6__vista_scd2_etef.sql` | Reemplaza `vw_etef_datos` para incluir columnas SCD2 y filtrar `is_current = TRUE`. |

Aplicar migraciones:

```bash
# Copiar y configurar credenciales
cp migrations/etef/flyway.conf.example migrations/etef/flyway.conf
# Editar migrations/etef/flyway.conf con host, user, pass reales

# Aplicar todas las migraciones
just migrate etef

# Verificar estado
just flyway-info etef
```

---

## Variables de entorno

Definidas en `.env.example`. Crear `.env` local (no commitear).

| Variable | Default | Descripción |
|---|---|---|
| `ETEF_DB_HOST` | `localhost` | Host PostgreSQL (Docker: `host.docker.internal`) |
| `ETEF_DB_PORT` | `5432` | Puerto PostgreSQL |
| `ETEF_DB_USER` | `iieg` | Usuario de BD |
| `ETEF_DB_PASS` | `changeme` | Contraseña (reemplazar en producción) |
| `ETEF_DB_NAME` | `etef` | Nombre de la base de datos |
| `ETEF_SOURCE_URL` | URL INEGI | ZIP público de INEGI (no modificar salvo cambio de fuente) |
| `ETEF_LOAD_BATCH_SIZE` | `5000` | Registros por lote en INSERT |

---

## DAGs de Airflow

| DAG ID | Schedule | Modo | Descripción |
|---|---|---|---|
| `etl_etef_bootstrap` | `None` (on-demand) | bootstrap | Carga inicial histórica 2007-I a 2025-IV. Ejecutar manualmente una sola vez. |
| `etl_etef_update` | `@quarterly` | update | Actualización trimestral con SCD2. Se activa automáticamente cada trimestre. |

Ambos DAGs usan `PythonOperator` con 1 tarea (`run_bootstrap` / `run_update`) que ejecuta
`Pipeline(stages=[EtefExtractor, EtefTransformer, EtefLoader]).run(mode=…)`.

---

## Estructura de archivos

```
core/pipelines/etef/
├── .env.example            # Variables de entorno (plantilla)
├── README.md               # Este archivo
├── attributes.py           # EtefTables (StrEnum), MUTABLE_COLUMNS, HASH_COLUMNS, NATURAL_KEY_COLUMNS
├── config.py               # Settings: DB, URL fuente, batch size
├── consts.py               # PIPELINE_NAME, NULL_VALUES, COLUMN_RENAME_MAP, CATALOG_COLUMNS
├── schemas.py              # SQLAlchemy: CatCodigoScian, EtefDatos, CATALOG_MODELS
├── eda/
│   └── reporte_eda.json    # Reporte EDA: 65,664 filas, 10 columnas, 2007-I a 2025-IV
└── stages/
    ├── extract.py          # Descarga ZIP, extrae CSV dinámicamente
    ├── transform.py        # Limpieza, hash SCD2, extracción de catálogos
    └── load.py             # Bootstrap bulk insert + SCD2 update

dags/
└── etl_etef.py             # DAGs: etl_etef_bootstrap (None) + etl_etef_update (@quarterly)

migrations/etef/
├── flyway.conf.example
└── sql/
    ├── V1__catalogos.sql
    ├── V2__cvegeo.sql
    ├── V3__tabla_principal.sql
    ├── V4__vista.sql
    ├── V5__scd2_etef.sql
    └── V6__vista_scd2_etef.sql
```

---

## Ejecución

### Bootstrap (primera vez)

```bash
# 1. Aplicar migraciones
just migrate etef

# 2. Copiar y configurar variables de entorno
cp core/pipelines/etef/.env.example core/pipelines/etef/.env
# Editar .env con credenciales reales

# 3. Ejecutar bootstrap (requiere PostgreSQL activo)
conda run -n etl python dags/etl_etef.py
```

### Update trimestral

```bash
# Ejecutar manualmente (o esperar el trigger @quarterly en Airflow)
conda run -n etl python -c "
from core.pipelines.etef.stages.extract import EtefExtractor
from core.pipelines.etef.stages.transform import EtefTransformer
from core.pipelines.etef.stages.load import EtefLoader
from core.pipeline import Pipeline
Pipeline('etef', [EtefExtractor('update'), EtefTransformer('update'), EtefLoader('update')]).run('update')
"
```

---

## Notas

- **VAL_USD ~50% nulo**: Registros con cifras no disponibles tienen `val_usd=NULL`; se preservan correctamente.
- **Sin filtro geográfico**: El pipeline carga los 32 estados. No existe `ETEF_FILTER_CVE_ENT` en `config.py`.
- **Detección dinámica del CSV**: Si INEGI cambia el nombre del archivo dentro del ZIP, el extractor selecciona automáticamente el primer `.csv` disponible.
- **Bloqueador de validación**: PostgreSQL debe estar corriendo para que la etapa Load complete. En el entorno local sin BD disponible, Extract y Transform pasan correctamente pero Load falla al intentar conectarse. Ejecutar `just up` antes del bootstrap para levantar la BD.
