---
name: pull-request-template
description: Abre el Pull Request de un pipeline al cierre de su implementación, llenando el template y vinculando el issue.
---

## Cuándo usar

Fase 8 (cierre). Después de los commits de implementación, testing y docs. Ejecutado por `git-agent`.

## Pre-requisitos

- Rama del issue al día con `develop` (rebase si hace falta).
- Pre-commit pasa.
- Pipeline corrió en bootstrap localmente sin errores.
- README interno actualizado y ERD generado.

## Pasos

### 1. Resumen de cambios

Inventariar:

- Archivos creados / modificados agrupados por área (pipeline / migrations / dags / docs).
- Resultado de testing (filas en BD por tabla, status del DAG, vista verificada).

### 2. Generar cuerpo del PR

Usar [.github/pull_request_template.md](../../.github/pull_request_template.md). Llenar:

- `Closes #{N}` con el issue.
- "Qué se hizo": párrafo breve con foco en valor entregado.
- Marcar tipo `feat` (default para nuevo pipeline).
- "Tareas completadas": checklist con los stages implementados, migraciones aplicadas, DAG corrido, README + ERD.
- "Notas": pasos manuales que el reviewer debe ejecutar (cargar `.env`, correr `just flyway-migrate {flujo}`, etc.).

### 3. Crear el PR con `gh`

```bash
gh pr create \
  --base develop \
  --head "$(git branch --show-current)" \
  --title "feat({flujo}): implement pipeline" \
  --body-file /tmp/pr_body.md \
  --label "feat,new-pipeline"
```

Solicitar review si el repo lo requiere:

```bash
gh pr edit --add-reviewer @org/etl-reviewers
```

### 4. Confirmar

Reportar URL del PR y los próximos pasos esperados (revisión, merge a `develop`).

## Reglas

- Base **siempre** `develop`. Nunca `main`.
- Título del PR sigue la misma convención de commits (`feat({flujo}): ...`).
- No usar `gh pr merge` automático. El merge es manual del reviewer.
- Si el pipeline tiene SCD o un paso manual extra, documentarlo en "Notas".
