---
name: new-pipeline
description: Creates a complete ETL pipeline from scratch — schemas, extract, transform, load, DAGs, migrations, and verification. Invoke when the user asks to create a new pipeline, add a new data source, or build a new ETL process.
user-invocable: true
---

## RESUME PROTOCOL

If invoked mid-implementation, detect current stage and ask:
"¿Deseas continuar desde {detected_stage} o desde otra etapa? Falta: {remaining_steps}"

---

## PHASE 0 — Sources & Schema Discovery

**If no URLs provided**, ask:
- What are the download URLs? (one per level: state, municipality, locality, year, etc.)

**Once URLs are available**, explore each one:

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

Identify:
- Available columns and data types
- Header/footer rows to discard
- Encoding issues
- Whether column names vary by year (→ use `rename_table(year) -> dict`)
- Columns with null or mixed values (strings + numerics)

Propose to the user:
- `RENAME_HEADER` (source col → snake_case)
- Columns to keep
- Resulting tables (main + catalogs if applicable)
- Schema structure (types, nullable, foreign keys)

**Wait for user confirmation before writing any file.**

Once accepted, ask in a single message:
1. **Pipeline name** — if not mentioned yet
2. **Source type** — iterable or non-iterable? (see below)
3. **Static catalogs** — tables with fixed values (grades, types)? Which ones?
4. **DAG** — start_date, schedule (or bootstrap only), retries, retry_delay
5. **Views** — filter only Jalisco (`WHERE cve_ent = 14`) or all states?

### Iterable vs Non-iterable Sources

This decision drives architecture in every subsequent phase:

| Aspect | Iterable | Non-iterable |
|---|---|---|
| URL pattern | Fixed, parameterized by year/entity | Changes each release |
| Extract `__init__` | `__init__(self, year: int)` | `__init__(self)` |
| File paths | Include param (`extract_{year}.pkl`) | Static name |
| Load strategy | `upsert_records` with `conflict_keys` | `bulk_insert` (bootstrap) |
| DAG schedule | `@yearly` or cron | `None` (bootstrap only) |
| Update process | Automatic via DAG | Manual re-run with new URL in `.env` |

Then continue without further questions.

---

## PHASE 1 — Schemas

Read first:
- `core/pipelines/establecimientos_de_salud/schemas.py`
- `core/pipelines/establecimientos_de_salud/attributes/establecimientos.py`
- `core/pipelines/establecimientos_de_salud/mappings.py`

### Attributes form

- **Folder** (multiple enums): `attributes/__init__.py`, `attributes/base.py`, `attributes/{pipeline}.py`
- **Flat** (one enum): `attributes.py`

### Files to create

- `core/pipelines/{pipeline}/constants.py`
- `core/pipelines/{pipeline}/attributes.py` or `attributes/`
- `core/pipelines/{pipeline}/schemas.py`
- `core/pipelines/{pipeline}/.env` and `.env.example` — URLs as env vars

### Database rules

- Table names: lowercase, no accents (ñ → ni), underscores, plural, no prefixes
- Every table has `id: Mapped[int]` as primary key
- Foreign key columns: `{singular_table_name}_id`
- Use SQLAlchemy 2.0 (`Mapped`, `mapped_column`) — never 1.x (`Column`, `declarative_base`)
- Every main table has `fecha_actualizacion: Date (NOT NULL)` unless periodicity is captured by a `periodos` catalog

### Constants rules

All module-level constants live **only** in `constants.py`. Never define them in `stages/`, `schemas.py`, or `mappings.py`.

What belongs in `constants.py`:
- `NULL_VALUES` — raw strings to treat as null
- `RENAME_HEADER` / `rename_table(year)` — column rename mappings
- `CAPITALIZE_COLS`, `TITLE_COLS` — columns to capitalize/title-case
- `DATE_COLS` — columns to parse as dates

---

## PHASE 2 — Extract

Read first:
- `core/pipelines/establecimientos_de_salud/stages/extract.py`
- `core/pipelines/marginacion/stages/extract.py`

### Rules

- **Iterable**: `__init__(self, year: int)`, file paths include param
- **Non-iterable**: `__init__(self)`, static file paths
- URLs from `.env` / config — never hardcoded
- Filter footer rows: `pd.to_numeric(df[col], errors="coerce").notna()`
- If one loop serves multiple levels: single private method returning a tuple
- Save as pickle to `data/extract/{pipeline}/`

### Checklist

- [ ] Column renames match source exactly
- [ ] Empty-DataFrame guard when source returns 0 records
- [ ] No silent fetch failures (raise on non-200)
- [ ] File paths include iterable parameter if applicable

---

## PHASE 3 — Transform

Read first:
- `core/utils/clean.py`, `core/utils/normalize.py`, `core/utils/mappings.py`
- `core/pipelines/establecimientos_de_salud/stages/transform.py`
- `core/pipelines/marginacion/stages/transform.py`

### Order in `action()`

1. `pd.to_numeric(df[col], errors="coerce")` for float columns **before** `list_values_to_null`
2. `pd.to_datetime(df[col])` for datetime columns **before** `list_values_to_null`
3. `list_values_to_null(df, rm_list=NULL_VALUES)`
4. `normalize_col()` → `.title()` → `apply_accents()` for proper name columns
5. `df[col] = df[col].dt.date` **after** null cleaning
6. `pd.to_numeric(df[col], errors="coerce").astype("Int64")` for nullable integers

### Key patterns

- FK mapping: `normalize_col()` before `.map()`
- Deduplication (strings): `drop_duplicates_col(df, col).dropna(subset=[col])`
- Deduplication (integers/numeric): `df.drop_duplicates(subset=[col]).dropna(subset=[col])`
- Geographic keys: `cve_geo_id = int(f"{entidad_id:02}{municipio_id:03}{localidad_id:04}")`

### Checklist

- [ ] Float columns in `object` dtype cast with `pd.to_numeric` before `list_values_to_null`
- [ ] Datetime columns converted before `list_values_to_null`
- [ ] No unintended null/column drops
- [ ] No duplicates in catalog tables
- [ ] Empty input guard: check `df.empty` and return immediately with same empty structure

---

## PHASE 4 — Load

Read first:
- `core/utils/bulk_ops.py`, `core/utils/files.py`
- `core/pipelines/establecimientos_de_salud/stages/load.py`
- `core/pipelines/marginacion/stages/load.py`

### Rules

- `df.astype(object).where(df.notna(), None)` before insert — converts `pd.NA` safely
- Exclude SERIAL id: `[c for c in Model.columns() if c != Model.id.key]`
- **Iterable**: `upsert_records` with `conflict_keys`
- **Non-iterable**: `bulk_insert` (bootstrap only)
- Load order: catalogs first, then main table
- `finalization()`: `cleanup_pipeline_data`, log inserted = total − records_before

### Checklist

- [ ] `df.astype(object).where(df.notna(), None)` before every insert
- [ ] SERIAL `id` excluded from INSERT columns
- [ ] Catalogs loaded before main table
- [ ] `sync_id_sequence` called after catalog inserts
- [ ] FK mapping verified — no NaN after `.map()`
- [ ] Correct load strategy for source type (upsert vs bulk_insert)

---

## PHASE 5 — DAGs

Use values confirmed in Phase 0.

- **Iterable**: schedule by year/entity; `start_date` = first available year
- **Non-iterable**: `schedule=None`, bootstrap only

---

## PHASE 6 — Migrations

Read first: `migrations/establecimientos_de_salud/sql/V1__foreign_tables.sql`

Create:
- `V1__foreign_tables.sql` — postgres_fdw + foreign tables
- `V2__catalogs_{pipeline}.sql` — catalog tables (skip if none)
- `V3__tables_{pipeline}.sql` — main tables; nullable must match `schemas.py`
- `V4__views_{pipeline}.sql` — join with cvegeo; `WHERE cve_ent = 14` if Jalisco-only
- `flyway.conf` and `flyway.conf.example`

---

## PHASE 7 — Verification

```bash
just flyway-reset {pipeline}
python dags/etl_{pipeline}.py
```

Review all phase checklists before marking done.

---

## PHASE 8 — README

Run `/update-readme`.

---

## NEVER

- Define constants outside `constants.py`
- Hardcode URLs in stage files
- Call `list_values_to_null` before casting float or datetime columns
- Include SERIAL `id` in INSERT column lists
- Use `replace({np.nan: None})` — use `df.astype(object).where(df.notna(), None)` instead
- Use `bulk_insert` for iterable pipelines (duplicates on re-run)
- Use `upsert_records` for non-iterable pipelines without a meaningful conflict key
- Use SQLAlchemy 1.x style
- Write any file before user confirms the schema proposal in Phase 0
