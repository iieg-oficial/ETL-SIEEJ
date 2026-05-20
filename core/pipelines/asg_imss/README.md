# Pipeline: ASG IMSS (Asegurados, Salarios y Trabajadores Eventuales)

Reescritura completa del flujo IMSS-ASG para Jalisco. Sustituye a `asg_imss_old` con un modelo
estrella normalizado (12 catálogos + tabla de hechos append-only + vista espejo del CSV),
catálogos auto-poblables y carga mes a mes tolerante a fallos por archivo.

> El flujo `asg_imss_old` se conserva temporalmente en el repositorio en lo que se valida la
> paridad funcional con consumidores aguas abajo; no recibe mantenimiento.

## Fuente

IMSS publica dos artefactos sobre datos abiertos en `http://datos.imss.gob.mx`:

| Atributo | Catálogo (diccionario) | Datos mensuales |
|---|---|---|
| **URL** | `…/diccionario_de_datos_1.xlsx` | `…/asg-{YYYY-MM-DD}.csv` (último día del mes) |
| **Formato** | XLSX (10 hojas, headers en fila 2 → `skiprows=1`) | CSV separador `\|` |
| **Encoding** | n/a | `utf-8` con fallback a `latin-1` |
| **Periodicidad** | Ocasional (cuando IMSS actualiza el diccionario) | Mensual, publicado la primera semana del mes siguiente |
| **Cobertura** | Nacional | Nacional — el pipeline filtra a Jalisco (`cve_entidad='14'`) en transform |
| **Header HTTP** | `User-Agent` de navegador obligatorio (`core.constants.http.BROWSER_HEADERS`); IMSS bloquea agentes no estándar | Igual |
| **Estrategia de update** | Re-sincroniza claves nuevas con `SIN DESCRIPCION` | Append-only (solo-inserciones) |

Hojas del diccionario consumidas (en orden topológico):
`delegación-subdelegación`, `entidad-municipio`, `sector 1`, `sector 2`, `sector 4`,
`Tamaño de registro patronal`, `sexo`, `Rango edad`, `Rango salario`, `Rango UMA`.

## Estructura

```
asg_imss/
├── .env.example     # Variables de entorno
├── config.py        # Settings (extiende BaseConfig)
├── attributes.py    # Listas de columnas, mapeos de header, constantes
├── schemas.py       # Modelos SQLAlchemy (AsgImssBase)
├── eda/
│   ├── eda_asg_imss.py
│   └── reporte_eda.json
└── stages/
    ├── extract.py   # AsgImssCatalogExtractor, AsgImssDataExtractor, compute_target_dates
    ├── transform.py # AsgImssCatalogTransformer, AsgImssDataTransformer
    └── load.py      # AsgImssCatalogLoader, AsgImssDataLoader (stateful)
```

Archivos relacionados fuera del directorio:

- [dags/etl_asg_imss.py](../../../dags/etl_asg_imss.py) — DAGs bootstrap + update mensual.
- [migrations/asg_imss/sql/](../../../migrations/asg_imss/sql/) — Migraciones Flyway V1–V3.

## ERD

```
+----------------+      +-------------------+
| cat_delegacion |<-----| cat_subdelegacion |
+----------------+      +-------------------+
        |                        |
        +-------+      +---------+
                |      |
+-------------+ |      | +--------------+
| cat_entidad |<+------+ | cat_municipio|
+-------------+          +--------------+
       |                        |
       +-----+        +---------+
             |        |
             v        v
       +---------------------+
       |    stg_asg_imss     |   (BIGSERIAL id, fecha_corte DATE,
       |  append-only fact   |    12 FK catálogos, 12 métricas INT,
       +---------------------+    5 métricas NUMERIC(18,2))
             ^   ^   ^   ^   ^   ^   ^   ^   ^
             |   |   |   |   |   |   |   |   |
+-------------+  |   |   |   |   |   |   |   +-- cat_rango_uma
| cat_sector_1|<-+   |   |   |   |   |   +------ cat_rango_salario
+-------------+      |   |   |   |   +---------- cat_rango_edad
       ^             |   |   |   +-------------- cat_sexo
       |             |   |   +------------------ cat_tamano_registro_patronal
+-------------+      |   |
| cat_sector_2|<-----+   |
+-------------+          |
       ^                 |
       |                 |
+-------------+          |
| cat_sector_4|<---------+
+-------------+
```

**Notación**: las FK de los tres sectores en `stg_asg_imss` son `NULL`-able; el resto son
`NOT NULL`. No existen FK contra `cve_geo`/INEGI: el catálogo de municipios del IMSS no
comparte formato con la CVEGEO de INEGI.

## Modelo de datos

### Catálogos

| Tabla | Cardinalidad observada (2026-01) | Notas |
|---|---:|---|
| `cat_delegacion` | 35 | `clave VARCHAR(3)` UNIQUE |
| `cat_subdelegacion` | 133 | FK → `cat_delegacion`; UNIQUE `(delegacion_id, clave)` |
| `cat_entidad` | 32 | `clave CHAR(2)` UNIQUE |
| `cat_municipio` | 2 540 | FK → `cat_entidad`; UNIQUE `(entidad_id, clave)` |
| `cat_sector_1` | 10 | `clave CHAR(1)` |
| `cat_sector_2` | 67 | FK → `cat_sector_1` |
| `cat_sector_4` | 290 | FK → `cat_sector_2` |
| `cat_tamano_registro_patronal` | 8 | `clave VARCHAR(2)` (uppercase, p.ej. `S1`…`S7`) |
| `cat_sexo` | 3 | Incluye literal `"NA"` |
| `cat_rango_edad` | 15 | Claves `E1`…`E15` |
| `cat_rango_salario` | 26 | Claves `W1`…`W25`+`NA` |
| `cat_rango_uma` | 26 | Claves `U1`…`U25`+`NA` |

Convención común: `id SERIAL PK`, `clave` con `UNIQUE`, `descripcion TEXT NOT NULL`.

### Tabla principal y vista

| Objeto | Descripción |
|---|---|
| `stg_asg_imss` | Hechos append-only. `id BIGSERIAL PK`, `fecha_corte DATE`, 12 FK a catálogos (sectores nullable), 12 métricas `INTEGER`, 5 métricas `NUMERIC(18,2)` (masa salarial), `created_at TIMESTAMPTZ`. **Sin** UNIQUE sobre llaves naturales ni hashes SCD. |
| `vw_asg_imss` | Espejo del CSV publicado por IMSS: expone solo las `clave` (códigos SK) resueltas vía JOIN, sin descripciones. Mantiene nombres de columna del CSV original tras la normalización de `tamano_patron`. |

## Reglas de negocio confirmadas

- **Filtro Jalisco**: transform conserva únicamente filas con `cve_entidad == '14'`
  (`ENTIDAD_FILTRO_CVE` en [attributes.py](attributes.py)). El modelo soporta cualquier
  entidad por flexibilidad futura.
- **Literal `"NA"`**: es un **valor válido** de catálogo en 9 de los 12 catálogos
  (`NA_LITERAL_VALID_CATALOGS`). Solo los tres catálogos de sector no admiten `"NA"`;
  ahí el faltante se representa como `NULL` real en la FK de `stg_asg_imss`.
- **Padding de sectores**: transform garantiza longitudes fijas
  `sector_economico_1=1`, `sector_economico_2=2`, `sector_economico_4=4`
  (`SECTOR_KEY_LENGTHS`). Las jerarquías `sector_2 → sector_1` y `sector_4 → sector_2`
  se derivan por prefijo de la clave.
- **Header con caracter de reemplazo**: algunos CSV llegan con `tama\ufffdo_patron`
  (U+FFFD) o `tamaño_patron`; `CSV_HEADER_RENAMES` los unifica a `tamano_patron`.
- **Auto-poblado de catálogos**: si en el CSV mensual aparece una clave no presente en
  el catálogo, `AsgImssDataLoader` la inserta con `descripcion='SIN DESCRIPCION'` y
  contabiliza el evento (`_auto_inserted_counter`) para reporte en `teardown`.
- **Limpieza en transform**: strip global, eliminación de filas completamente vacías,
  `drop_duplicates` exacto sobre todas las columnas y casteo numérico (`fillna(0)` en
  enteros, `fillna(0.0)` en decimales).
- **`fecha_corte`**: lo asigna transform a partir del `target_date` recibido (último día
  del mes publicado), no del nombre del archivo.

## Arquitectura

Dos sub-flujos independientes coordinados por el DAG:

```
catálogos:  AsgImssCatalogExtractor → AsgImssCatalogTransformer → AsgImssCatalogLoader
datos:      AsgImssDataExtractor     → AsgImssDataTransformer    → AsgImssDataLoader
                            (iterado mes a mes; falla parcial no aborta el DAG)
```

`AsgImssDataLoader` es **stateful**: el DAG lo instancia una vez, llama `setup()` antes del
bucle (abre conexión y carga cachés de catálogos en memoria), procesa N meses y al final
ejecuta `teardown()`. Esto evita reconectar y reconsultar los catálogos por cada mes.

### Flujo entre etapas

| Etapa | Entrada | Salida |
|---|---|---|
| `AsgImssCatalogExtractor` | — | `{"file_path": str}` (XLSX) |
| `AsgImssCatalogTransformer` | `file_path` | `dict` con listas por catálogo (`delegacion`, `subdelegacion`, …) |
| `AsgImssCatalogLoader` | catálogos parseados | `{"status": "ok"}` |
| `AsgImssDataExtractor` | `target_date` | `{"file_path", "target_date"}` (CSV) |
| `AsgImssDataTransformer` | `file_path`, `target_date` | `{"df", "target_date", "rows_in", "rows_out"}` |
| `AsgImssDataLoader` | `df`, `target_date` | `{"rows_inserted", "auto_inserted"}` |

## Flujo del pipeline

### Extract

1. Inyecta `BROWSER_HEADERS` en todas las solicitudes HTTP (IMSS bloquea agentes no
   estándar).
2. Reintenta hasta `MAX_RETRIES` con backoff fijo de 3 segundos.
3. Catálogo: descarga binario del XLSX a `data/extract/asg_imss/`.
4. Datos: `compute_target_dates(mode)` arma la lista a procesar:
   - `bootstrap`: rango `[ASG_IMSS_DATA_START_DATE, ASG_IMSS_DATA_END_DATE]` (último día
     de mes). Si `END` está vacío usa el último mes cerrado.
   - `update`: únicamente el último mes cerrado.
5. Por cada fecha descarga `asg-YYYY-MM-DD.csv`, decodifica `utf-8` con fallback a
   `latin-1` y persiste como UTF-8.

### Transform (catálogos)

1. Lee el XLSX hoja por hoja con `skiprows=1`, `dtype=str`, `keep_default_na=False`.
2. Aplica strip y lowercase a headers.
3. Sectores: expande rangos `"X - Y"` de `sector 1` en filas individuales; aplica
   `zfill` a `sector_2` y `sector_4` y deriva la clave del padre por prefijo.
4. Catálogo `tamano_registro_patronal`: normaliza la clave a uppercase para alinear con
   el CSV de hechos.

### Transform (datos)

1. Lee el CSV con `dtype=str`, `keep_default_na=False`; intenta `utf-8`, fallback
   `latin-1`.
2. Renombra headers según `CSV_HEADER_RENAMES`.
3. Strip global, conversión `""→NaN`, `dropna(how="all")`, restaura `""`.
4. `drop_duplicates()` exacto.
5. `zfill(2)` a `cve_entidad` y filtro `== '14'`.
6. Padding de sectores (solo donde la clave no esté vacía).
7. `tamano_patron` → uppercase.
8. Casteo de las 12 métricas enteras a `int` (con `fillna(0)`) y las 5 decimales a
   `float` (con `fillna(0.0)`).
9. Asigna `fecha_corte = target_date`.

### Load

1. Catálogos: `insert_records(..., on_conflict_do_nothing)` en orden topológico
   (delegacion → subdelegacion → entidad → municipio → sector_1 → sector_2 → sector_4
   → 5 simples). Sincroniza la secuencia `SERIAL` de cada tabla al final.
2. Datos:
   - Cachés en memoria por catálogo (`clave → id` para simples, `(parent_id, clave) → id`
     para subdelegacion/municipio).
   - Para cada CSV resuelve FK por clave. Si falta, `INSERT … ON CONFLICT DO NOTHING
     RETURNING id` con `descripcion='SIN DESCRIPCION'` y actualiza la caché.
   - Las FK de sector se quedan en `None` cuando la clave llega vacía (NULL en BD).
   - `bulk_insert` en lotes de `BATCH_SIZE`.
   - `teardown` loggea el conteo de claves auto-pobladas por catálogo.

## Periodicidad y ejecución

Dos DAGs en [dags/etl_asg_imss.py](../../../dags/etl_asg_imss.py):

- **`etl_asg_imss_bootstrap`** — `schedule=None`. Bajo demanda. Procesa el rango completo
  configurado en `.env`. Tasks: `bootstrap_catalogos` → `bootstrap_datos`.
- **`etl_asg_imss_update`** — `cron "0 12 10 * *"` (día 10 de cada mes a las 12:00).
  Re-sincroniza catálogos y carga únicamente el último mes cerrado. Tasks:
  `update_catalogos` → `update_datos`.

En ambos DAGs, una falla por mes individual en el sub-flujo de datos se loggea como
`ERROR` y el bucle continúa con el siguiente mes; el conteo final
(`ok / fail / filas_insertadas`) se loggea al cierre.

### Comandos

Preparar BD y migraciones con [justfile](../../../justfile):

```bash
just env-init asg_imss          # crea core/pipelines/asg_imss/.env desde el .example
just pipeline-deploy asg_imss   # env-init + flyway-config + create-db + flyway-migrate
# o paso a paso:
just create-db asg_imss
just flyway-migrate asg_imss
```

Bootstrap (manual, fuera de Airflow):

```bash
conda run -n etl python -m dags.etl_asg_imss
# o desde la UI de Airflow: trigger del DAG etl_asg_imss_bootstrap
```

Update mensual: gestionado por Airflow a través de `etl_asg_imss_update`.

## Variables de entorno

Definidas en [.env.example](.env.example).

| Variable | Default | Descripción |
|---|---|---|
| `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` / `DB_NAME` | — | Conexión a PostgreSQL del pipeline |
| `ASG_IMSS_CATALOG_URL` | URL oficial IMSS | XLSX del diccionario de datos |
| `ASG_IMSS_DATA_URL` | URL oficial IMSS | Template del CSV mensual con placeholder `{date}` (`YYYY-MM-DD`) |
| `ASG_IMSS_DATA_START_DATE` | `2015-01-31` | Inicio del rango en modo `bootstrap` |
| `ASG_IMSS_DATA_END_DATE` | `""` | Fin del rango; vacío = último mes cerrado |
| `BATCH_SIZE` | `5000` | Filas por chunk en `bulk_insert` |
| `MAX_RETRIES` | `3` | Reintentos HTTP por archivo |
| `TIMEOUT` | `300` | Timeout HTTP (segundos) |
| `LOG_LEVEL` | `INFO` | Nivel de log |

## Migraciones

- **V1** `catalogs_asg_imss` — 12 tablas catálogo con jerarquías
  (delegacion→subdelegacion, entidad→municipio, sector_1→sector_2→sector_4) y simples.
- **V2** `table_asg_imss` — `stg_asg_imss` (BIGSERIAL, 12 FK, 17 métricas, `fecha_corte`,
  índices por catálogo y fecha). Sin UNIQUE sobre llaves naturales.
- **V3** `view_asg_imss` — `vw_asg_imss` espejo del CSV original: solo expone `clave` de
  cada catálogo resuelta por JOIN; `LEFT JOIN` en los tres sectores; agrega
  `fecha_corte`.

## Validación de la última corrida

Resultados de la ejecución de validación end-to-end (corte `2026-01-31`):

| Objeto | Filas |
|---|---:|
| `stg_asg_imss` (fecha_corte=2026-01-31, Jalisco) | **474 262** |
| `cat_delegacion` | 35 |
| `cat_subdelegacion` | 133 |
| `cat_entidad` | 32 |
| `cat_municipio` | 2 540 |
| `cat_sector_1` | 10 |
| `cat_sector_2` | 67 |
| `cat_sector_4` | 290 |
| `cat_tamano_registro_patronal` | 8 |
| `cat_sexo` | 3 |
| `cat_rango_edad` | 15 |
| `cat_rango_salario` | 26 |
| `cat_rango_uma` | 26 |

## Notas

- **Sin FK contra `cve_geo`**: el catálogo de municipios del IMSS no es compatible con
  la clave geoestadística de INEGI; por eso `cat_municipio` es un catálogo propio y
  `stg_asg_imss` no referencia las foreign tables de `cvegeo`.
- **`User-Agent` obligatorio**: IMSS responde `403`/contenido vacío sin un
  `User-Agent` de navegador. Se usa `core.constants.http.BROWSER_HEADERS` en ambos
  extractores.
- **Coexistencia con `asg_imss_old`**: ambos pipelines viven en el repositorio durante la
  ventana de migración. Una vez validada la paridad con consumidores, `asg_imss_old`
  (código, DAG, migraciones) se retirará en un PR independiente.
- **`vw_asg_imss` sin descripciones**: por diseño, la vista replica el CSV publicado
  (códigos), no la versión humanamente legible. Si se necesita un join completo con
  descripciones, debe construirse a partir de `stg_asg_imss` + catálogos según consumo.

## Brechas documentadas

- No existe `assets/erd.svg` para este pipeline; el ERD se documenta en ASCII arriba.
  Cuando se ejecute el generador de ERDs, sustituir el bloque por
  `![ERD](assets/erd.svg)`.
- El reporte EDA (`eda/reporte_eda.json`) describe el catálogo `delegación-subdelegación`
  como una única tabla de 134 filas; la implementación lo descompone en
  `cat_delegacion` (35) + `cat_subdelegacion` (133). La descomposición vive en
  `AsgImssCatalogTransformer.action` y es la fuente de verdad.
