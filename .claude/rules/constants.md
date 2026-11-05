---
paths:
  - "core/pipelines/**/*.py"
---

# Constants

All pipeline-level constants (UPPER_SNAKE_CASE variables) must live in `core/pipelines/{pipeline}/constants/`, split by submodule and re-exported from `constants/__init__.py`. Existing pipelines may still use a flat `constants.py`.

Never define constants at the top of `stages/`, `schemas.py`, `mappings/`, or any other pipeline file.

## What belongs in constants/

- `NULL_VALUES` — list of raw strings to treat as null
- `RENAME_HEADER` / `rename_table(year)` — column rename mappings
- `CAPITALIZE_COLS`, `TITLE_COLS` — columns to capitalize/title-case
- `DATE_COLS` — columns to parse as dates
- Any other module-level list, dict, or scalar used across stages

## What does NOT belong in constants/

- SQLAlchemy models → `schemas.py`
- Static catalog dicts (id → label) → `mappings/`
- Table name enums → `attributes/`
- Local variables inside functions — keep them where they are used

## Import pattern

```python
from core.pipelines.{pipeline}.constants import NULL_VALUES, RENAME_HEADER
```

## When reviewing or generating code

- If a constant is defined at module level outside `constants/` (or the flat `constants.py` of an existing pipeline), move it there.
- New pipelines get `constants/` from `just new-pipeline <name>`.
