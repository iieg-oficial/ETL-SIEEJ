---
name: pipeline-readme
description: Template canónico del README de un pipeline SIEEJ. Estructura basada en `core/pipelines/censo_poblacion/README.md` y `repd/README.md`. Úsalo cuando generes o actualices la documentación interna de un pipeline.
argument-hint: <pipeline>
---

# Skill: README de Pipeline

Fuente única del formato y contenido esperado en `core/pipelines/{pipeline}/README.md`. Refleja el código realmente implementado, no el teórico.

## Template base

```markdown
# Pipeline: {Nombre Humano}

{Una o dos frases describiendo qué datos contiene y de dónde vienen}

## Fuente

{Descripción breve de la dependencia/origen de los datos. Incluir un enlace público si aplica.}

| Atributo | Valor |
|---|---|
| **URL / Origen** | `https://...` o descripción |
| **Formato** | Excel (hoja `DATOS`, header fila 13) / CSV / API / Google Drive |
| **Registros aprox.** | ~37,000 |
| **Llave natural** | `feb` (folio estatal de búsqueda) |
| **Periodicidad** | Mensual |
| **Comportamiento** | mixto — los registros existentes pueden cambiar |

## Estructura

\`\`\`
{pipeline}/
├── .env.example     # Variables de entorno con valores de ejemplo
├── config.py        # Settings del pipeline (extiende BaseConfig)
├── consts.py        # Constantes: NULL_VALUES, COLUMN_RENAME_MAP, etc.
├── schemas.py       # Modelos SQLAlchemy
└── stages/
    ├── extract.py
    ├── transform.py
    └── load.py
\`\`\`

Archivos relacionados fuera del directorio:

- `dags/etl_{pipeline}.py` — DAG de Airflow (bootstrap + update)
- `migrations/{pipeline}/sql/` — Migraciones Flyway
- `migrations/{pipeline}/flyway.conf.example` — Config de ejemplo

## Esquema de base de datos

Preferir un ERD ASCII (o SVG en `assets/erd_{pipeline}.svg`) con las tablas, columnas principales y FKs.

\`\`\`
+---------------------------+     +-----------------------------------+
| stg_{pipeline}_cat_ejemplo|     | stg_{pipeline}_datos              |
|---------------------------|     |-----------------------------------|
| id SERIAL PK              |<----| cat_ejemplo_id INTEGER FK         |
| name VARCHAR(100) UNIQUE  |     | llave_natural VARCHAR(64) UNIQUE  |
+---------------------------+     | municipio_id INTEGER (cvegeo FDW) |
                                  | fecha_dato DATE                   |
                                  | record_hash VARCHAR(64)           |
                                  | created_at / updated_at TIMESTAMP |
                                  +-----------------------------------+
\`\`\`

**Catálogos**: {cómo se sincronizan — `ON CONFLICT DO NOTHING` vía `insert_records`}.

**Municipios** (si aplica): {cómo se resuelven contra `cvegeo_municipalities` — tupla `(estado, municipio)` normalizada a UPPER}.

**Estrategia de update**: bootstrap_only / upsert / SCD2. {Descripción breve del porqué}.

## Arquitectura

Sigue el patrón de 3 etapas `Stage` → `Pipeline`:

\`\`\`
{Nombre}Extractor → {Nombre}Transformer → {Nombre}Loader
\`\`\`

### Flujo entre etapas

| Etapa | Entrada | Salida |
|-------|---------|--------|
| **Extract** | Ninguna | `{"file_path": ...}` |
| **Transform** | `file_path` | `{"df": ..., "catalogs": {...}, "row_count": N}` |
| **Load** | df + catalogs | `{"row_count": N}` |

## Flujo del pipeline

### Extract
1. {Paso real 1 — ej. Descarga el XLSX desde la API}
2. {Paso real 2}
3. Guarda en `data/extract/{pipeline}/` con timestamp

### Transform
1. Lee el archivo (sheet `DATOS`, header fila X)
2. Normaliza headers a snake_case sin acentos
3. Aplica `COLUMN_RENAME_MAP`
4. Limpia `NULL_VALUES`
5. Parsea `DATE_COLUMNS`
6. Normaliza geografía a UPPER (si aplica)
7. Extrae `CATALOG_COLUMNS`
8. Sanitiza NaN residuales

### Load
1. Sincroniza catálogos (insert on conflict do nothing)
2. Construye mapas `name → id`
3. Resuelve cvegeo (si aplica)
4. Calcula `record_hash` (si SCD2)
5. `bootstrap`: bulk insert completo
6. `update`: upsert o SCD2 según estrategia
7. Sincroniza secuencias SERIAL

## Periodicidad

{Descripción de los DAGs y su schedule}

- **Bootstrap**: `schedule=None`, bajo demanda
- **Update**: `"0 3 1 * *"` — mensual el día 1 a las 03:00

## Configuración

Variables en `.env` (ver `.env.example` y `config.py`):

| Variable | Default | Descripción |
|---|---|---|
| `{NOMBRE}_DB_HOST` | `localhost` | Host de la BD (Docker: `host.docker.internal`) |
| `{NOMBRE}_SOURCE_URL` | — | URL de la fuente |
| `{NOMBRE}_LOAD_BATCH_SIZE` | `5000` | Filas por batch en INSERT |

Para migraciones Flyway, ver `migrations/{pipeline}/flyway.conf.example`.

## Migraciones

- **V1** `catalogos` — N tablas catálogo dinámicas
- **V2** `cvegeo` — FDW a BD cvegeo (si aplica)
- **V3** `tabla_principal` — tabla de datos {+ `_history` si SCD2}
- **V4** `vista` — vista analítica con joins a catálogos y cvegeo

## Utilidades reutilizadas

- `core.utils.bulk_ops`: `insert_records`, `bulk_insert`, `upsert_records`, `sync_id_sequence`
- `core.utils.clean.list_values_to_null` — limpieza de nulos
- `core.utils.normalize.normalize_col`, `uppercase_col` — normalización de texto
- `core.utils.parse_datetime.parse_month_year` — parseo de fechas
- `core.utils.records.compute_record_hash` — hash SHA-256 para SCD2

```

## Reglas de contenido

- **Siempre reflejar el código real**, no el ideal. Si el `load.py` no usa `upsert_records`, no lo menciones.
- **Diagramas ASCII** de tablas deben coincidir con `schemas.py` y las migraciones SQL.
- **Sin credenciales reales** (tokens, URLs internas de producción, usuarios).
- **Secciones Extract/Transform/Load** en pasos numerados cortos que describan qué hace el código.
- **Longitudes `VARCHAR(n)`** y FKs en el ERD deben coincidir con `schemas.py`.

## Casos especiales

### Pipelines con múltiples fuentes (estilo `censo_poblacion` / `censos_economicos`)

Reemplazar la sección **Fuente** por una tabla con múltiples filas, una por fuente:

```markdown
| Fuente | Tipo | Nivel geográfico |
|---|---|---|
| Censo 2010 | ZIP → CSV | Localidad |
| Intercensal 2015 | XLS | Municipio |
| Censo 2020 | ZIP → CSV | Localidad |
```

### Pipelines con ERD externo

Si el ERD es complejo, generarlo como SVG en `core/pipelines/{pipeline}/assets/erd_{pipeline}.svg` y referenciarlo:

```markdown
## Esquema de base de datos

![ERD](assets/erd_{pipeline}.svg)
```

## Referencias de estilo

- `core/pipelines/censo_poblacion/README.md` — estilo corto con múltiples fuentes + ERD en SVG.
- `core/pipelines/repd/README.md` — estilo detallado con ERD ASCII + SCD2 + cvegeo.
- `core/pipelines/censos_economicos/README.md` — estilo con tabla de utilidades reutilizadas.
- `core/pipelines/fiscalia/README.md` — fuente Google Drive.
