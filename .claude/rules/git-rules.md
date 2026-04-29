---
description: Git workflow rules. Applies to all files.
---

# Git Rules

> Aplican a: GIT

## Rules

- Nunca usar `git add .`. Agregar únicamente los archivos específicos del cambio.
- Seguir la convención de commits definida en el skill `git-pipeline-commits`. Mensajes en inglés imperativo.
- Un commit por funcionalidad (un stage, una migración, el DAG, la documentación). No mezclar cambios no relacionados.
- Crear la rama desde `develop` con el formato `{issue_number}-pipeline-{flujo}` (p.ej. `42-pipeline-fiscalia`).
- El proyecto tiene pre-commit con Ruff check. Revisar el output del commit y corregir errores antes de intentar de nuevo.
- No commitear archivos `.env`, `.pyc`, datos crudos (`.csv`, `.xlsx`, `.json` de fuentes) ni archivos de cache. Verificar `.gitignore` antes de cada commit.
- Mantener el `.gitignore` actualizado con las extensiones y rutas de datos del nuevo pipeline.
- El scope del commit es el nombre del flujo (p.ej. `feat(fiscalia): add extract stage`), no el componente (no `feat(pipeline)` ni `feat(dags)`).
- Al abrir el Pull Request, referenciar el issue con `Closes #{numero}` en la descripción.
- El PR se abre desde la rama del pipeline hacia `develop`, nunca directamente a `main`.
