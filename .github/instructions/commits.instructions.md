---
name: commits
description: Convención de Conventional Commits para el proyecto ETL SIEEJ.
applyTo: "**"
---

# Convención de Commits — ETL SIEEJ

## Formato

```
<tipo>(<scope>): <descripción en imperativo>
```

## Tipos

| Tipo | Uso |
|------|-----|
| `feat` | Nueva funcionalidad o pipeline completo |
| `fix` | Corrección de error o bug |
| `update` | Modificación de funcionalidad existente |
| `refactor` | Refactorización sin cambio funcional |
| `chore` | Dependencias, configs, mantenimiento |
| `docs` | Solo documentación |
| `merge` | Merge de rama de pipeline hacia develop |

## Scopes

El scope **siempre es el nombre del flujo/pipeline** (e.g. `asg_imss`, `repd`, `fiscalia`), no el nombre del componente técnico.
Usa scopes de componente solo cuando el cambio es transversal (no pertenece a un pipeline concreto):

| Scope | Aplica a |
|-------|----------|
| `<nombre_pipeline>` | Cambios dentro de un pipeline específico — **usar siempre que sea posible** |
| `core` | Módulos base (`core/config.py`, `core/db.py`, `core/pipeline.py`) |
| `utils` | Utilidades (`core/utils/`) |
| `config` | Configuración del proyecto (`.env`, `compose.yaml`, etc.) |
| `docs` | Documentación (`docs/`, `README.md`, `CONTRIBUTING.md`) |

## Reglas

1. Tipo y scope en **minúsculas**: `feat(pipeline)` ✅ — `Feat(Pipeline)` ❌
2. Descripción en **inglés**, modo **imperativo**: `"add extract stage"` ✅ — `"added extract stage"` ❌
3. Máximo **72 caracteres** en la primera línea.
4. Scope obligatorio cuando el cambio es claro (`fix(core)` ✅ — `fix` ❌).
5. **Un commit = un cambio lógico**. No mezclar `feat` + `fix` en el mismo commit.
6. Sin commits `WIP` en el PR final.

## Ramas

Las ramas **no se crean manualmente**. Se generan automáticamente desde el issue de GitHub usando la opción "Create a branch" en la interfaz de GitHub. El nombre de la rama lo asigna GitHub a partir del título del issue (e.g. `feat/pipeline-asg_imss` o `123-add-asg-imss-pipeline`).

## Pre-commit hooks

El proyecto tiene configurado `.pre-commit-config.yaml`. Al hacer `git commit`, se ejecutan automáticamente:
1. **Validación del patrón de commit** — rechaza el commit si el mensaje no cumple la convención `<tipo>(<scope>): <descripción>`.
2. **`ruff check`** — linter de Python; rechaza el commit si hay errores de linting.

Si un commit es rechazado, corrige el problema indicado y vuelve a intentar el commit.

## Orden recomendado al crear un pipeline nuevo

```bash
git commit -m "feat(migrations): add V1 initial tables for {pipeline}"
git commit -m "feat({pipeline}): add config and constants"
git commit -m "feat({pipeline}): add schemas"
git commit -m "feat({pipeline}): add extract stage"
git commit -m "feat({pipeline}): add transform stage"
git commit -m "feat({pipeline}): add load stage"
git commit -m "feat({pipeline}): add bootstrap and update DAGs"
git commit -m "docs({pipeline}): add README"
```

## Ejemplos

```bash
# Nuevos pipelines (scope = nombre del pipeline)
git commit -m "feat(empleo_formal): add extract stage"
git commit -m "feat(migrations): add V1 initial tables for empleo_formal"
git commit -m "feat(empleo_formal): add bootstrap and update DAGs"

# Correcciones
git commit -m "fix(core): handle null values in normalize_headers"
git commit -m "fix(asg_imss): resolve timeout in extract for large files"

# Actualizaciones
git commit -m "update(asg_imss): change schedule to first of month"
git commit -m "update(utils): normalize_headers now strips leading/trailing spaces"

# Documentación
git commit -m "docs: add contributing guide"
git commit -m "docs(pipeline): add README for fiscalia"

# Mantenimiento
git commit -m "chore(deps): upgrade pandas to 2.2.0"
git commit -m "chore(config): update airflow worker memory limit"
```

## Lo que NO hacer

- ❌ No hacer push directo a `main` o `develop`
- ❌ No hacer `--force` en ramas compartidas
- ❌ No commitear `.env`, `flyway.conf` ni credenciales
- ❌ No commitear archivos de datos (`.xlsx`, `.csv`, `.parquet`)
- ❌ No mergear el propio PR sin revisión
