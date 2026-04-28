---
name: python-rules
description: Reglas de estilo y estructura de código Python para todo el proyecto ETL SIEEJ.
applyTo: "core/**/*.py,dags/**/*.py,plugins/**/*.py"
---

## Estilo

- PEP8, código simple y legible.
- Funciones atómicas y reutilizables.
- Tipado en argumentos y retorno de toda función.
- Docstrings claros (estilo Google o NumPy).
- Comentarios sobrios y puntuales. No usar separadores decorativos como `# ===== Título =====`.

## Naming

- `snake_case` para variables y funciones.
- `PascalCase` para clases.
- `UPPER_CASE` para constantes.
- Archivos y nombres internos en utf-8 sin acentos: reemplazar `á é í ó ú` por `a e i o u` y `ñ` por `ni`.

## Imports

Al inicio del archivo, en este orden y separados por línea en blanco:

1. `import` de stdlib
2. `from` de stdlib
3. Third-party
4. Locales (`from core...`)

Nunca importar dentro de funciones.

## Estructura y reutilización

- Antes de implementar un helper, validar si ya existe en `core/utils/`. Si no existe, crearlo en `core/pipelines/{flujo}/helpers/`.
- Evitar hardcoding: todo valor literal usado más de una vez o relevante para el dominio vive en `core/pipelines/{flujo}/constants.py`.
- Constantes (UPPER_SNAKE_CASE) **solo** en `constants.py`. Nunca en `stages/`, `schemas.py` o `mappings.py`.

## Manejo de errores

- `try/except` en operaciones I/O y red.
- Loggear el error con `logger.exception` antes de re-raise o de un fallback explícito.
- Nunca capturar `Exception` sin volver a propagarla o registrarla.

## Logging

Usar el logger configurado en `core/utils/logger.py`. No usar `print` en código de producción.

## Entorno

- Ejecutar con conda env `etl` o `.venv` (Python 3.12).
- Si falta el env: `conda create -n etl python=3.12` o `python -m venv .venv`.
- Toda nueva dependencia se agrega a `requirements.txt` con versión pinneada.
