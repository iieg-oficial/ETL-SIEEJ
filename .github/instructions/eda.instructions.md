---
applyTo: "**/eda/*.py"
---

# EDA Instructions

> Applies to: EDA scripts

## Rules

- Write EDA work as `.py` scripts, not notebooks. Notebooks make Git review harder.
- Save all EDA scripts under `./core/pipelines/{flujo}/eda/`. The filename must be `eda_{flujo}.py`.
- The script must cover these steps in order:
  1. Download or load the source files using the same logic planned for the `extract` stage.
  2. Show the first rows and column data types (`dtypes`).
  3. Report the total row count and total column count.
  4. Identify key columns such as IDs, dates, and periods.
  5. Count unique values per column to detect possible catalogs (`< 100` unique values means catalog candidate).
  6. Analyze geographic level: national, state, or municipal (`cve_ent`, `cve_mun`, and related fields).
  7. Analyze null and empty values: `NaN`, `NA`, `N/A`, empty strings, and whitespace.
  8. Analyze periodicity when multiple source files exist.
- The final script output must be the JSON report generated with the `eda-reporte` skill. Do not rely on prints alone; serialize the results.
- Do not save intermediate files inside `eda/`. Only the script and `reporte_eda.json` belong there.
- Import project utilities from `core.utils` when possible, such as `normalize_text` and `get_logger`.
