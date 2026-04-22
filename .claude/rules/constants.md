---
paths:
  - "core/pipelines/**/*.py"
---

# Constants

All pipeline-level constants (UPPER_SNAKE_CASE variables) must live in `core/pipelines/{pipeline}/constants.py`.

Never define constants at the top of `stages/`, `schemas.py`, `mappings.py`, or any other pipeline file.

## What belongs in constants.py

- `NULL_VALUES` — list of raw strings to treat as null
- `RENAME_HEADER` / `rename_table(year)` — column rename mappings
- `CAPITALIZE_COLS`, `TITLE_COLS` — columns to capitalize/title-case
- `DATE_COLS` — columns to parse as dates
- Any other module-level list, dict, or scalar used across stages

## What does NOT belong in constants.py

- SQLAlchemy models → `schemas.py`
- Static catalog dicts (id → label) → `mappings.py`
- Table name enums → `attributes/` or `attributes.py`
- Local variables inside functions — keep them where they are used

## Import pattern

```python
from core.pipelines.{pipeline}.constants import NULL_VALUES, RENAME_HEADER
```

## When reviewing or generating code

- If a constant is defined at module level in any file other than `constants.py`, move it there.
- If `constants.py` does not exist yet for a new pipeline, create it before writing any stage.
