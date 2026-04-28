---
description: Corre pruebas end-to-end del pipeline en BD docker local (bootstrap +
  update) y reporta incidencias.
argument-hint: '[nombre del pipeline]'
---

> Use el agente `testing-agent`.

Valida end-to-end el pipeline:

- **Pipeline:** {{flujo}}

Pasos a ejecutar:
1. `just up-database`
2. `just flyway-reset {{flujo}}` y `just flyway-migrate {{flujo}}`
3. `python dags/etl_{{flujo}}.py` (bootstrap)
4. Validar BD (conteos, FKs, nulos, normalización, geo keys, vista V4).
5. Re-ejecutar para validar update (sin duplicados; SCD2 si aplica).

Entregable: reporte estructurado con incidencias accionables y sugerencias del agente al que reasignar.

Aplica reglas de [.github/instructions/testing-rules.instructions.md](../instructions/testing-rules.instructions.md).
