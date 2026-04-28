---
name: pipeline-docs
description: Genera o actualiza el README interno del pipeline y regenera el diagrama ER.
agent: docs-agent
argument-hint: "[nombre del pipeline]"
---

Genera la documentación del pipeline:

- **Pipeline:** ${input:flujo}

Entregables:
- `core/pipelines/${input:flujo}/README.md` siguiendo el skill `docs-pipeline`.
- `core/pipelines/${input:flujo}/assets/erd.png` (regenerar solo si `schemas.py` cambió).

Validar que nombres de tabla/columna y variables `.env` documentados coincidan con el código real. No documentar lo que no esté verificado en código.
