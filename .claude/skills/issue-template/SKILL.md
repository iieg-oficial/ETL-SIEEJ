---
name: issue-template
description: Crea el GitHub issue de un nuevo pipeline ETL usando el template del repo y deja la rama lista desde develop.
---

## Cuándo usar

Fase 4 del flujo: justo antes de empezar la implementación. Ejecutado por `git-agent`.

## Pasos

### 1. Recolectar datos

Tomar del contexto previo (EDA + propuesta de esquema):

- **Nombre del pipeline** (snake_case, sin acentos)
- **Fuente** (API / BD / Web Scraping / Archivo)
- **Frecuencia** (mensual / quincenal / semanal / diaria / on-demand)
- **Tablas destino** (lista de `cat_*` y `stg_*`)
- **Credenciales** necesarias (API key / usuario-password / token / ninguna)
- **Notas** adicionales

### 2. Crear el issue con `gh`

Generar el cuerpo a partir de [.github/ISSUE_TEMPLATE/new-pipeline.md](../../.github/ISSUE_TEMPLATE/new-pipeline.md), llenando los checkboxes correspondientes:

```bash
gh issue create \
  --title "[PIPELINE] {nombre_humano}" \
  --label "new-pipeline,feat" \
  --body-file /tmp/issue_body.md
```

Capturar el número devuelto (`#N`).

### 3. Crear la rama

```bash
# Slug = title sin "[PIPELINE] ", lowercase, espacios -> guiones
SLUG="pipeline-{flujo}"
git fetch origin develop
git checkout -b "{N}-${SLUG}" origin/develop
git push -u origin "{N}-${SLUG}"
```

### 4. Confirmar al usuario

Reportar:

- Número del issue creado y URL.
- Nombre de la rama y que ya está sincronizada con remoto.
- Próximo paso: regresar el control al `dea-agent` para implementación.

## Reglas

- Si el issue ya existe (mismo título), no duplicar; reusar el número y crear la rama.
- Nunca crear el issue contra `main`. Siempre `develop` como base.
- Labels exactos: `new-pipeline`, `feat`. Agregar más solo si el usuario lo pide.
