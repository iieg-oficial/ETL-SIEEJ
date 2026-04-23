# Pipeline: ETEF (Exportaciones — EEF Trimestral)

Exportaciones trimestrales por entidad federativa y subsector SCIAN, publicadas por INEGI desde 2007. Datos filtrados a **Jalisco (CVE_ENT=14)**.

## Fuente

Publicación de INEGI con datos de exportaciones trimestrales. La fuente es un ZIP que contiene CSV con histórico completo 2007–2025, actualizado cada trimestre.

| Atributo | Valor |
|---|---|
| **URL** | `https://www.inegi.org.mx/contenidos/programas/exporta_ef/datosabiertos/conjunto_de_datos_eef_trimestral_csv.zip` |
| **Formato** | ZIP → CSV (UTF-8) |
| **Registros aprox.** | 65,664 (histórico 2007–2025, todas las entidades) |
| **Llave natural** | `(ANIO, TRIMESTRE, CVE_ENT, CODIGO_SCIAN)` |
| **Periodicidad** | Trimestral |
| **Comportamiento** | `sobreescribe` — el ZIP contiene todo 2007–2025; re-ingestión completa |

## Estructura

```
etef/
├── .env.example          # Variables de entorno
├── config.py             # Settings (BD, fuente, batch size, filtro geográfico)
├── consts.py             # Constantes: NULL_VALUES, COLUMN_RENAME_MAP, CATALOG_COLUMNS
├── schemas.py            # Modelos SQLAlchemy: CatCodigoScian, EtefDatos
└── stages/
    ├── extract.py        # Descarga ZIP, extrae CSV
    ├── transform.py      # Lee CSV, limpia, filtra Jalisco, extrae catálogos
    └── load.py           # Inserta catálogos y datos con resolución de FKs
```

Archivos relacionados:

- `dags/etl_etef.py` — DAG de Airflow (bootstrap + update trimestral)
- `migrations/etef/sql/` — 4 migraciones Flyway (catálogos, cvegeo FDW, tabla, vista)
- `migrations/etef/flyway.conf.example` — Config de ejemplo

## Esquema de base de datos

```
+--------------------------------------+     +-----------------------------------+
| stg_etef_cat_codigo_scian            |     | stg_etef_datos                    |
|--------------------------------------|     |-----------------------------------|
| id SERIAL PK                         |<----| id SERIAL PK                      |
| codigo VARCHAR(3) UNIQUE             |     | anio INTEGER                      |
| descripcion VARCHAR(255)             |     | trimestre VARCHAR(2)              |
| version VARCHAR(10)                  |     | mes VARCHAR(5)                    |
+--------------------------------------+     | cve_ent INTEGER (filter = 14)     |
                                             | codigo_scian_id INTEGER FK        |
                                             | val_usd NUMERIC(15,2) [50% NULL] |
                                             | estatus_cifra VARCHAR(20)        |
                                             | estatus VARCHAR(30)              |
                                             | created_at / updated_at TIMESTAMP|
                                             | UNIQUE (anio, trimestre, ...     |
                                             | cve_ent, codigo_scian_id)        |
                                             +-----------------------------------+

Vista analítica:
  vw_etef_datos — JOIN a catálogos SCIAN + cvegeo para nom_ent
```

**Catálogos**: 
- `stg_etef_cat_codigo_scian` — 27 subsectores SCIAN 2007 (códigos 000, 111, 112, ..., 339)
- Sincronizados vía `INSERT ... ON CONFLICT DO NOTHING`

**Georreferencia**: 
- Relacionada con `cvegeo_municipalities` vía `cve_ent` (entidad)
- Filtrado manual a **Jalisco (CVE_ENT=14)** en el stage de Transform

**Estrategia de actualización**: 
- `bootstrap_only` — El ZIP reemplaza todo 2007–2025 en cada carga trimestral
- No hay SCD2 (registros no cambian históricamente; es un snapshot re-ingestado)

## Arquitectura

Sigue el patrón de 3 etapas `Stage` → `Pipeline`:

```
EtefExtractor → EtefTransformer → EtefLoader
```

### Flujo entre etapas

| Etapa | Entrada | Salida |
|-------|---------|--------|
| **Extract** | Ninguna | `{"file_path": "data/extract/etef/eef_trimestral_tr_cifra_2007_2025.csv"}` |
| **Transform** | `file_path` | `{"df": <DataFrame>, "catalogs": {"codigo_scian": [...]}, "row_count": N}` |
| **Load** | df + catalogs | `{"mode": "bootstrap", "records_inserted": N, "catalogs_synced": 1}` |

## Flujo del pipeline

### Extract
1. Descarga ZIP desde la URL de INEGI (timeout 180s)
2. Extrae el archivo `eef_trimestral_tr_cifra_2007_2025.csv` del ZIP
3. Elimina el ZIP local
4. Retorna ruta al CSV: `data/extract/etef/eef_trimestral_*_*.csv`

### Transform
1. Lee CSV en UTF-8
2. Normaliza headers a `snake_case` y aplica `COLUMN_RENAME_MAP`
3. Limpia valores en `NULL_VALUES` (`"NO APLICA"`, `"NA"`, `""`, etc.)
4. **Filtra a Jalisco**: `cve_ent == 14` (reduce ~65K → ~4–5K registros)
5. Convierte tipos: `anio` → int, `val_usd` → float
6. Extrae valores únicos de `codigo_scian` → catálogo
7. Crea `llave_natural` concatenando `(anio|trimestre|cve_ent|codigo_scian)`
8. Sanitiza NaN/NaT residuales a None

### Load
1. Crea/verifica tablas SQLAlchemy
2. Sincroniza catálogo `codigo_scian` (insert on conflict)
3. Construye mapa `codigo → id`
4. Resuelve IDs de catálogo en el DataFrame
5. Bulk insert de registros en `stg_etef_datos` (batch size: 5000 por defecto)
6. Sincroniza secuencias SERIAL

## Periodicidad

- **Bootstrap DAG** (`etl_etef_bootstrap`): 
  - Schedule: `None` (manual/on-demand)
  - Carga completa 2007–2025
  - Tags: `["etl", "etef", "bootstrap", "on-demand"]`

- **Update DAG** (`etl_etef_update`):
  - Schedule: `"0 0 1 */3 *"` — 1er día de cada trimestre a las 00:00
  - Carga trimestral (re-ingestión completa del ZIP)
  - Tags: `["etl", "etef", "update"]`

## Configuración

Variables en `.env` (ver `.env.example` y `config.py`):

| Variable | Default | Descripción |
|---|---|---|
| `ETEF_DB_HOST` | `localhost` | Host de la BD (Docker: `host.docker.internal`) |
| `ETEF_DB_PORT` | `5432` | Puerto PostgreSQL |
| `ETEF_DB_USER` | `bi_iieg` | Usuario BD |
| `ETEF_DB_PASS` | `changeme` | Contraseña (no usar en producción) |
| `ETEF_DB_NAME` | `etef` | Nombre de la BD |
| `ETEF_SOURCE_URL` | URL INEGI | ZIP del INEGI (no cambiar) |
| `ETEF_LOAD_BATCH_SIZE` | `5000` | Registros por batch en INSERT |
| `ETEF_FILTER_CVE_ENT` | `14` | Filtro geográfico (Jalisco) |

Para migraciones Flyway:

```bash
# Configurar Flyway
just flyway-config etef
# Editar migrations/etef/flyway.conf con credenciales reales

# Aplicar migraciones
just flyway-reset etef

# Verificar
just flyway-info etef
```

## Migraciones

- **V1** `catalogos` — Tabla `stg_etef_cat_codigo_scian` con 27 códigos SCIAN
- **V2** `cvegeo` — Extensión `postgres_fdw`, server, foreign table a `cvegeo.municipalities`
- **V3** `tabla_principal` — Tabla `stg_etef_datos` con 4 índices (anio+trimestre, cve_ent, codigo_scian_id, llave natural)
- **V4** `vista` — Vista `vw_etef_datos` con nombres humanos (subsector + entidad desde cvegeo)

## Utilidades reutilizadas

- `core.utils.bulk_ops.insert_records` — Sincronización de catálogos
- `core.utils.bulk_ops.bulk_insert` — Bulk insert de datos principales
- `core.utils.bulk_ops.get_mapping` — Caché `name → id` para resolución de FKs
- `core.utils.bulk_ops.sync_id_sequence` — Sincronización de secuencias SERIAL
- `core.utils.clean.list_values_to_null` — Limpieza de valores nulos
- `core.utils.normalize.normalize_col` — Normalización de headers a snake_case
- `core.utils.files.clean_directory` — Limpieza de directorios temporales

## Ejecución local

```bash
# Activar environment
conda activate etl

# Ejecutar DAG bootstrap como script (sin Airflow)
python dags/etl_etef.py

# O con Airflow (después de just up)
just up
just logs airflow-dag-processor
```

## Notas

- **VAL_USD es 50% nulo**: Registros con estatus "No disponible" tienen val_usd=NULL (preservado correctamente)
- **Filtro manual a Jalisco**: Se aplica en Transform, no en la BD. Permite reutilizar el pipeline para otras entidades si es necesario
- **Re-ingestión completa**: Cada carga borra e inserta todo 2007–2025 (estrategia `bootstrap_only`); no hay deduplicación ni versionado
