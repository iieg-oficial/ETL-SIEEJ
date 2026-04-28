---
name: git-pipeline-commits
description: Convención de commits y checklist para implementación incremental de pipelines ETL.
---

## Formato

```
<tipo>(<scope>): <descripción en inglés imperativo>
```

- Solo línea de encabezado. Sin cuerpo. Sin `Co-Authored-By`.
- Máximo 72 caracteres.
- En minúsculas, salvo nombres propios o siglas.

## Tipos

| Tipo | Uso |
|---|---|
| `feat` | Nueva funcionalidad o stage |
| `fix` | Corrección de bug |
| `update` | Modificación de funcionalidad existente |
| `refactor` | Refactor sin cambio funcional |
| `chore` | Configs, dependencias, mantenimiento |
| `docs` | Documentación |
| `merge` | Merge de pipeline a develop |

## Scopes

| Scope | Aplica a |
|---|---|
| `{flujo}` | Cambios dentro de `core/pipelines/{flujo}/` o `dags/etl_{flujo}.py` o `migrations/{flujo}/` |
| `core` | Módulos en `core/` (db, pipeline, config) |
| `utils` | Utilidades en `core/utils/` |
| `dags` | Cambios genéricos a DAGs (no específicos de un pipeline) |
| `migrations` | Cambios genéricos de Flyway |
| `config` | Configuración del proyecto |
| `docs` | Documentación |

**Para un pipeline específico el scope es siempre el nombre del pipeline**, no `pipeline` ni `dags` ni `migrations`.

## Secuencia recomendada para un pipeline nuevo

Un commit por funcionalidad para evitar deuda técnica:

1. `chore({flujo}): scaffold pipeline structure`
2. `feat({flujo}): add EDA scripts and report`
3. `feat({flujo}): add migrations V1-V4`
4. `feat({flujo}): add SQLAlchemy schemas and attributes`
5. `feat({flujo}): add extract stage`
6. `feat({flujo}): add transform stage`
7. `feat({flujo}): add load stage`
8. `feat({flujo}): add Airflow DAG`
9. `docs({flujo}): add internal README and ERD`
10. `fix({flujo}): <correcciones detectadas en testing>` (las que apliquen)

## Reglas operativas

- Nunca `git add .`. Agregar archivos por funcionalidad.
- Pre-commit corre `ruff check`. Si falla: corregir y reintentar; nunca usar `--no-verify`.
- Una rama por issue (`<issue_number>-<title>`), creada desde `develop`.
- Antes de abrir PR: rebase contra `develop` si hay conflictos.

## Ejemplos válidos

```
feat(asg_imss): add extract stage for monthly file
fix(repd): handle empty dataframe in transform
update(censos_economicos): change schedule to quarterly
docs(fiscalia): add internal README with ERD
chore(deps): upgrade pandas to 2.2.0
```

## Ejemplos inválidos

```
feat(pipeline): ...                # scope debe ser el nombre del flujo
Feat(asg_imss): ...                # mayúsculas
feat(asg_imss): added extract...   # debe ser imperativo (add, no added)
feat(asg_imss): agrega extract...  # debe ser inglés
```
