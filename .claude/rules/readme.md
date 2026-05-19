---
paths:
  - "core/pipelines/**/README.md"
  - "core/pipelines/**/assets/**"
---

# Pipeline README

Minimalist style. Required sections in this order:

1. **Title** — `DB_NAME` (from `.env`) as H1
2. **ERD** — ERD image: `![ERD](assets/erd.svg)`
3. **Diccionario de variables** — one markdown table per main table (column → description). Only include columns whose purpose is not obvious from the name. Skip self-explanatory columns like `id`, `nombre`, `fecha_actualizacion`.
4. **Fuentes** — markdown table with source level, filename, and URL env var
5. **Actualización** — update frequency, whether manual or automatic, and a brief justification based on the nature of the data

## ERD generation

Generate with erdalchemy before writing the README. For updates, only regenerate if `schemas.py` changed.

```bash
python scripts/generate_erds.py
```
