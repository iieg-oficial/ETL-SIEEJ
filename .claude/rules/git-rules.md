---
name: git-rules
description: Reglas de control de versiones, ramas, commits y .gitignore para ETL
  SIEEJ.
paths:
- '**'
---

## Commits

- Formato: `tipo(scope): mensaje en inglés imperativo`. Detalle en el skill `git-pipeline-commits` y en [docs/convencion-commits.md](../../docs/convencion-commits.md).
- Solo encabezado. Sin cuerpo, sin `Co-Authored-By`.
- Máximo 72 caracteres en la primera línea.
- Un commit = un cambio lógico. Commits por funcionalidad para evitar deuda técnica.
- Scope = nombre del pipeline cuando aplica (ej: `feat(asg_imss): add extract stage`).

## Staging

- **Nunca** usar `git add .` ni `git commit -a`.
- Agregar archivos uno por uno o por grupos explícitos.

## Ramas

- Crear desde `develop`.
- Formato: `<issue_number>-<issue_title>`, ej: `123-pipeline-nombre-flujo`.
- Una rama por issue.

## Pre-commit

- Hook `ruff check` activo. Revisar la salida del commit y arreglar antes de re-intentar.
- No usar `--no-verify` para saltar validaciones.

## .gitignore

Mantener actualizado. Vigilar que **no** se commiteen:

- `.env`, `*.env.local`
- `*.pyc`, `__pycache__/`
- Datos crudos: `*.csv`, `*.xlsx`, `*.zip`, `*.pkl` salvo que estén en `assets/` y sean intencionales.
- Archivos generados en `data/extract/`, `data/transform/`, `data/load/`, `logs/`.

## Issues y PRs

- Toda implementación arranca con un issue creado desde el template de [.github/ISSUE_TEMPLATE/new-pipeline.md](../../.github/ISSUE_TEMPLATE/new-pipeline.md).
- Toda fusión se hace vía PR usando [.github/pull_request_template.md](../../.github/pull_request_template.md), con `Closes #N`.
