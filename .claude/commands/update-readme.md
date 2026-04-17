## Actualizar README

Update the existing `core/pipelines/{pipeline}/README.md` to match current pipeline state. Regenerate `core/pipelines/{pipeline}/assets/erd.png` if schemas changed.

Regenerate ERD with eralchemy2 only if `schemas.py` was modified:
```python
from eralchemy2 import render_er
render_er(Base, "core/pipelines/{pipeline}/assets/erd.png")
```

README must be written in Spanish.

Follow the same structure and rules as create-readme:

1. **Title** — the database name (`DB_NAME` from `.env`) as the H1 heading
2. **Esquema** — ERD image: `<img src="assets/erd.png" width="400" height="400">`
3. **Diccionario de variables** — one markdown table per main table (column → description). Only include columns whose purpose is not obvious from the name alone. Skip self-explanatory columns like `id`, `nombre`, `fecha_actualizacion`.
4. **Fuentes** — markdown table with source level, filename, and URL env var
5. **Actualización** — explain:
   - The update frequency (yearly, monthly, on-demand, etc.)
   - Whether updates are **manual or automatic**
   - A brief justification based on the nature of the data (e.g. "La fuente no ofrece API pública, por lo que la descarga debe realizarse manualmente desde el portal de INEGI cada año.")

When updating, reconcile the existing content against the current `schemas.py`, `.env`, and stage files — do not preserve outdated sections.
