---
paths:
  - "core/pipelines/**"
---

# Common Patterns

- Every main table has `fecha_actualizacion: Date (NOT NULL)`, unless periodicity is already captured by a `periodos` catalog
- Static catalogs live in `mappings.py`; dynamic catalogs are built in `transform._build_catalogs()`
- Geographic keys: `cve_geo_id = int(f"{entidad_id:02}{municipio_id:03}{localidad_id:04}")`
- Foreign key mapping uses `normalize_col()` before `.map()`
- Deduplication: `drop_duplicates_col(df, col).dropna(subset=[col])` — only for string columns (`drop_duplicates_col` calls `.str.lower()` internally). For integer/numeric columns use `df.drop_duplicates(subset=[col]).dropna(subset=[col])` directly.
- Normalize then apply accents on proper name columns: `normalize_col()` → `title()` → `apply_accents()`
- Null cleaning: `list_values_to_null(df, rm_list=NULL_VALUES)`
- SERIAL PK columns must be excluded from INSERT column lists — build them explicitly or filter with `[c for c in Model.columns() if c != Model.id.key]`
- Incremental stages must guard against empty input early: check `df.empty` (or all DataFrames empty) and return immediately with the same empty structure to avoid downstream KeyErrors
- `pd.NA` (produced by nullable integer types like `Int64`) is NOT converted by `replace({np.nan: None})`. Use `df.astype(object).where(df.notna(), None)` before `df_to_records` to safely convert all NA-like values to `None`.
- Float columns stored as `object` dtype (e.g. read from Excel): cast with `pd.to_numeric(df[col], errors="coerce")` BEFORE calling `list_values_to_null`, otherwise numeric-looking strings bypass null cleaning silently.
- When source column names include a year or variable (e.g. `IM_2020`, `GM_2020`), define rename mappings as functions `rename_table(year: int) -> dict` instead of static dicts.
