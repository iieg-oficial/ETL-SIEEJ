---
paths:
  - "core/pipelines/**/README.md"
  - "core/pipelines/**/assets/**"
---

# Pipeline README

`docs/readme-pipeline.md` is the authoritative template. Read it before writing or restructuring a pipeline README, and keep its section names and order.

- Omit `Vistas` and `Notas adicionales` when they do not apply.
- `Diccionario de variables`: one table per main table. Only include columns whose purpose is not obvious from the name; skip columns like `id`, `nombre`, `fecha_actualizacion`.

## ERD generation

Generate with erdalchemy before writing the README. For updates, only regenerate if `schemas.py` changed.

```bash
python scripts/generate_erds.py
```
