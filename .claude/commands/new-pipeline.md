---
description: Inicia el flujo completo de creación de un pipeline ETL desde EDA hasta
  PR (fases 0-8) usando el Data Engineer Agent.
argument-hint: '[nombre del pipeline] [URLs de la fuente]'
---

> Use el agente `dea`.

Quiero crear un nuevo pipeline ETL siguiendo las 9 fases definidas en [refactor.md](../../refactor.md).

**Información inicial:**

- **Nombre del pipeline (snake_case):** {{flujo}}
- **Fuente / URLs:** {{fuentes}}
- **Notas adicionales:** {{notas}}

**Tu trabajo:**

1. Si falta información (iterable vs no, frecuencia, alcance Jalisco, variante de update, credenciales), pregúntala en una sola tanda antes de empezar.
2. Coordina las 9 fases delegando a los subagentes especializados:
   - Fase 1 → `eda-agent`
   - Fase 2 → `db-agent`
   - Fase 4 (issue + rama) → `git-agent` modo `init`
   - Fase 5 → `etl-agent`
   - Fase 6 → `testing-agent`
   - Fase 7 → `docs-agent`
   - Fase 8 → `git-agent` modos `commit` + `pr`
3. Después de cada fase, valida el contrato y reporta el avance al usuario.
4. No escribas archivos antes de que el usuario apruebe la propuesta de esquema.

Aplica las reglas heredadas de `.github/instructions/`.
