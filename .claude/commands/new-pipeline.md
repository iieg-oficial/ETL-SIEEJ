# New Pipeline Creation Guide

@.claude/rules/patterns.md
@.claude/rules/error-checklist.md
@.claude/rules/constants.md
@.claude/rules/databases.md

## Resume Protocol

When asked to read this file mid-implementation, check current progress and ask:
"¿Deseas continuar de {detected_stage} o de alguna otra etapa? Falta: {remaining_steps}"

---

## FASE 0 — Fuentes y schema

**Si el usuario no proporcionó URLs**, pedir:
- ¿Cuáles son las URLs de descarga? (una por nivel: estatal, municipal, localidad, año, etc.)

**Una vez que hay URLs**, descargar y explorar cada una:

```python
import io, requests, urllib3, pandas as pd
urllib3.disable_warnings()
r = requests.get(url, verify=False)
# CSV:  df = pd.read_csv(io.BytesIO(r.content), encoding="iso-8859-1")
# XLSX: df = pd.read_excel(io.BytesIO(r.content))
# ZIP:  ZipFile(io.BytesIO(r.content))
print(df.columns.tolist())
print(df.head(5))
print(df.dtypes)
print(df.shape)
```

Identificar:
- Columnas disponibles y tipos de dato
- Filas de encabezado/pie a descartar
- Problemas de encoding
- Si los nombres de columna varían por año (→ usar `rename_table(year) -> dict`)
- Qué columnas tienen valores nulos o mixtos (strings + numéricos)

Con esa información, proponer al usuario:
- `RENAME_HEADER` (source col → snake_case)
- Columnas a conservar
- Tablas resultantes (principal + catálogos si aplica)
- Estructura del schema (tipos, nullable, claves foráneas)

**Esperar confirmación del usuario antes de escribir cualquier archivo.**

Una vez aceptado, preguntar en un solo mensaje:
1. **Nombre del pipeline** — si no se mencionó aún
2. **Iterativo** — ¿la descarga itera por entidad, año u otro parámetro?
3. **Catálogos estáticos** — ¿hay tablas con valores fijos (grados, tipos)? ¿cuáles?
4. **DAG** — start_date, schedule (o solo bootstrap), retries, retry_delay
5. **Vistas** — ¿filtrar solo Jalisco (`WHERE cve_ent = 14`) o todos los estados?

Luego continuar sin más preguntas.

---

## FASE 1 — Schemas

Read first:
- `core/pipelines/establecimientos_de_salud/schemas.py`
- `core/pipelines/establecimientos_de_salud/attributes/establecimientos.py`
- `core/pipelines/establecimientos_de_salud/mappings.py`

Choose attributes form:
- **Folder** (multiple enums): `attributes/__init__.py`, `attributes/base.py`, `attributes/{pipeline}.py`
- **Flat** (one enum): `attributes.py`

Create:
- `core/pipelines/{pipeline}/constants.py`
- `core/pipelines/{pipeline}/attributes.py` or `attributes/`
- `core/pipelines/{pipeline}/schemas.py`
- `core/pipelines/{pipeline}/.env` and `.env.example` — URLs as env vars

---

## FASE 2 — Extract

- If iterative: `__init__(self, year: int)`, file paths include param
- If one loop serves multiple levels: single private method returning a tuple
- URLs from config/env, never hardcoded
- Filter footer rows: `pd.to_numeric(df[col], errors="coerce").notna()`
- Save as pickle to `data/extract/{pipeline}/`

---

## FASE 3 — Transform

Read first:
- `core/utils/clean.py`, `core/utils/normalize.py`, `core/utils/mappings.py`
- `core/pipelines/establecimientos_de_salud/stages/transform.py`
- `core/pipelines/marginacion/stages/transform.py`

Order in `action()`:
1. `pd.to_numeric(df[col], errors="coerce")` for float columns **before** `list_values_to_null`
2. `pd.to_datetime(df[col])` for datetime columns **before** `list_values_to_null`
3. `list_values_to_null(df, rm_list=NULL_VALUES)`
4. `normalize_col()` → `.title()` → `apply_accents()` for proper name columns
5. `df[col] = df[col].dt.date` **after** null cleaning
6. `pd.to_numeric(df[col], errors="coerce").astype("Int64")` for nullable integers

---

## FASE 4 — Load

Read first:
- `core/utils/bulk_ops.py`, `core/utils/files.py`
- `core/pipelines/establecimientos_de_salud/stages/load.py`
- `core/pipelines/marginacion/stages/load.py`

- `df.astype(object).where(df.notna(), None)` before insert
- Exclude SERIAL id: `[c for c in Model.columns() if c != Model.id.key]`
- `bulk_insert` for bootstrap, `upsert_records` with `conflict_keys` for incremental
- `finalization()`: `cleanup_pipeline_data`, log inserted = total − records_before

---

## FASE 5 — DAGs

Use values from FASE 0. Bootstrap only if data updates every 10+ years.

---

## FASE 6 — Migrations

Read first: `migrations/establecimientos_de_salud/sql/V1__foreign_tables.sql`

Create:
- `V1__foreign_tables.sql` — postgres_fdw + foreign tables
- `V2__catalogs_{pipeline}.sql` — catalog tables (skip if none)
- `V3__tables_{pipeline}.sql` — main tables; nullable must match schemas.py
- `V4__views_{pipeline}.sql` — join with cvegeo; `WHERE cve_ent = 14` if Jalisco-only
- `flyway.conf` and `flyway.conf.example`

---

## FASE 7 — Verificación

```
just flyway-reset {pipeline}
python dags/etl_{pipeline}.py
```

---

## FASE 8 — README

Run `/update-readme`.
