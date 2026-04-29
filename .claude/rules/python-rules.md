---
description: Python coding standards. Applies to all .py files.
---

# Python Rules

> Aplican a: DEA, EDA, ETL, TEST

## Rules

- Seguir PEP8. Funciones atómicas y reutilizables con docstrings en inglés.
- Tipado estricto en argumentos y valor de retorno de todas las funciones.
- Manejo de excepciones con `try/except` explícito. Usar `logging`, nunca `print`.
- Imports al inicio del archivo en orden: stdlib → third-party → local. Nunca dentro de funciones.
- Sin hardcoding de valores: usar constantes `UPPER_CASE` definidas en `constants.py` o `consts.py` del pipeline.
- Nomenclatura: `snake_case` para variables y funciones, `PascalCase` para clases, `UPPER_CASE` para constantes.
- Antes de crear un helper, verificar si existe en `core/utils/`. Si no existe, crearlo en `helpers/` del pipeline.
- Archivos en UTF-8. Usar `normalize_text` de `core/utils/normalize.py` para nombres de variables y columnas; no incluir tildes, ñ ni caracteres especiales en identificadores.
- Sin comentarios decorativos (p.ej. `#=== Título ===`). Comentarios breves, puntuales y en inglés.
- **Entorno:** siempre usar conda `etl` (Python 3.12) para ejecutar scripts Python. Activar con `conda activate etl` antes de correr cualquier script. No usar `python` o `python3` del sistema sin verificar que pertenece al entorno `etl`.
- Agregar dependencias a `requirements.txt` con versión fijada.
- Respetar `line-length = 120` definido en `pyproject.toml` (Ruff). Ejecutar `ruff check` antes de cada commit.
- Los archivos de stage heredan de `core.pipeline.Stage` (ABC). Implementar `source()`, `action()`, `finalization()`.
