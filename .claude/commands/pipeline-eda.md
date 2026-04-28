---
description: Ejecuta o re-ejecuta solo la fase de Análisis Exploratorio (EDA) para
  un pipeline.
argument-hint: '[nombre del pipeline] [URLs]'
---

> Use el agente `eda-agent`.

Realiza el EDA del pipeline:

- **Pipeline:** {{flujo}}
- **URLs / fuentes:** {{fuentes}}

Sigue las reglas de [.github/instructions/eda-rules.instructions.md](../instructions/eda-rules.instructions.md) y el formato JSON del skill `eda-reporte`.

Entregables:
- Script(s) en `core/pipelines/{{flujo}}/eda/*.py`.
- Reporte en `core/pipelines/{{flujo}}/eda/reporte_*.json`.
- Resumen con 3-5 hallazgos clave y `open_questions` para validar con el usuario.
