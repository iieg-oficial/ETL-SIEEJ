---
name: python
description: Convenciones globales de estilo y estructura para código Python.
applyTo: "**/*.py"
---

# Python Instructions

> Applies to: DEA, EDA, ETL, and Python code generated in this repository

## Rules

- Follow PEP8. Write atomic, reusable functions with English docstrings.
- Use strict typing for function arguments and return values.
- Handle exceptions explicitly with `try/except`. Use `logging`, never `print`.
- Keep imports at the top of the file in this order: standard library, third-party, local. Never import inside functions.
- Do not hardcode fixed values. Use `UPPER_CASE` constants defined in the pipeline `constants.py` or `consts.py`.
- Use `snake_case` for variables and functions, `PascalCase` for classes, and `UPPER_CASE` for constants.
- Before creating a new helper, check whether it already exists in `core/utils/`. If not, create it in the pipeline `helpers/` package.
- Keep files in UTF-8. Use `normalize_text` from `core/utils/normalize.py` for variable and column names. Do not use accents, `ñ`, or special characters in identifiers.
- Do not add decorative comments such as `#=== Title ===`. Keep comments short, precise, and in English.
- **Environment:** always use the `etl` conda environment (Python 3.12) for Python scripts. Activate `etl` or use `conda run -n etl`. Never use system `python` or `python3` unless you have verified it points to the `etl` environment.
- Add new dependencies to `requirements.txt` with pinned versions.
- Respect `line-length = 120` from `pyproject.toml` and run `ruff check` before each commit.
- Stage files must inherit from `core.pipeline.Stage` (ABC) and implement `source()`, `action()`, and `finalization()`.
