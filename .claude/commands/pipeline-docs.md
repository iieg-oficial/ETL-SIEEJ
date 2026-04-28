---
description: Genera o actualiza el README interno del pipeline y regenera el diagrama
  ER.
argument-hint: '[nombre del pipeline]'
---

> Use el agente `docs-agent`.

Genera la documentación del pipeline:

- **Pipeline:** {{flujo}}

Entregables:
- `core/pipelines/{{flujo}}/README.md` siguiendo el skill `docs-pipeline`.
- `core/pipelines/{{flujo}}/assets/erd.png` (regenerar solo si `schemas.py` cambió).

Validar que nombres de tabla/columna y variables `.env` documentados coincidan con el código real. No documentar lo que no esté verificado en código.
