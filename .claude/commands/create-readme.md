## README

Create `core/pipelines/{pipeline}/README.md` and `core/pipelines/{pipeline}/assets/erd.png`.

Generate the ERD with eralchemy2:
```python
from eralchemy2 import render_er
render_er(Base, "core/pipelines/{pipeline}/assets/erd.png")
```

README must be written in Spanish.

README structure (minimalist, in this order):

1. **Title** — the database name (`DB_NAME` from `.env`) as the H1 heading
2. **Esquema** — ERD image: `<img src="assets/erd.png" width="400" height="400">`
3. **Diccionario de variables** — one markdown table per main table (column → description). Only include columns whose purpose is not obvious from the name alone. Skip self-explanatory columns like `id`, `nombre`, `fecha_actualizacion`.
4. **Fuentes** — markdown table with source level, filename, and URL env var
5. **Actualización** — explain:
   - The update frequency (yearly, monthly, on-demand, etc.)
   - Whether updates are **manual or automatic**
   - A brief justification based on the nature of the data (e.g. "La fuente no ofrece API pública, por lo que la descarga debe realizarse manualmente desde el portal de INEGI cada año.")
