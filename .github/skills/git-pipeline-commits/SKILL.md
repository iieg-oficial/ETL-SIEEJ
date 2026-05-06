---
name: git-pipeline-commits
description: Secuencia canónica de commits atómicos para un pipeline ETL SIEEJ nuevo, siguiendo Conventional Commits con scope = nombre del pipeline. Úsalo al cerrar un pipeline y preparar el PR hacia `develop`.
argument-hint: <pipeline>
---

# Skill: Commits de un Pipeline

Plantilla de commits atómicos y seguros. Las reglas de convención están en `.github/instructions/commits.instructions.md`; este skill **solo provee la secuencia exacta** para el caso "crear un pipeline nuevo".

## Precondiciones

- Estar en una rama del issue (creada desde GitHub, no localmente).
- `conda activate etl` activo.
- Ruff sin errores:
  ```bash
  ruff check core/pipelines/{pipeline}/ dags/etl_{pipeline}.py
  ruff check --fix core/pipelines/{pipeline}/ dags/etl_{pipeline}.py  # si hay errores
  ```
- Ningún archivo sensible staged (ver sección "Archivos prohibidos").

## Secuencia canónica de commits

Scope = nombre del pipeline (`{pipeline}`). Un commit = un cambio lógico.

```bash
# 1. Migraciones (orden: V1 catálogos, V2 cvegeo, V3 tabla, V4 vista)
git add migrations/{pipeline}/sql/ migrations/{pipeline}/flyway.conf.example
git commit -m "feat({pipeline}): add initial Flyway migrations"

# 2. Config y constantes
git add core/pipelines/{pipeline}/__init__.py \
        core/pipelines/{pipeline}/config.py \
        core/pipelines/{pipeline}/consts.py
git commit -m "feat({pipeline}): add config and constants"

# 3. Schemas SQLAlchemy
git add core/pipelines/{pipeline}/schemas.py
git commit -m "feat({pipeline}): add SQLAlchemy schemas"

# 4. Extract stage
git add core/pipelines/{pipeline}/stages/__init__.py \
        core/pipelines/{pipeline}/stages/extract.py
git commit -m "feat({pipeline}): add extract stage"

# 5. Transform stage
git add core/pipelines/{pipeline}/stages/transform.py
git commit -m "feat({pipeline}): add transform stage"

# 6. Load stage
git add core/pipelines/{pipeline}/stages/load.py
git commit -m "feat({pipeline}): add load stage"

# 7. DAG de Airflow
git add dags/etl_{pipeline}.py
git commit -m "feat({pipeline}): add bootstrap and update DAGs"

# 8. Documentación
git add core/pipelines/{pipeline}/README.md \
        core/pipelines/{pipeline}/.env.example
git commit -m "docs({pipeline}): add README and env example"
```

Si la periodicidad es > 3 meses, el paso 7 es `"feat({pipeline}): add bootstrap DAG"` (sin update).

## Archivos prohibidos (nunca staged)

Verificar con `git status` antes de cada commit. Si aparece uno:

```bash
git reset HEAD <archivo>
```

| Patrón | Razón |
|---|---|
| `core/pipelines/{pipeline}/.env` | Credenciales reales |
| `migrations/{pipeline}/flyway.conf` | Credenciales Flyway |
| `data/**` | Datos descargados |
| `logs/**` | Logs locales |
| `*.pyc`, `__pycache__/` | Bytecode Python |
| `.ipynb_checkpoints/` | Jupyter temp |
| `tmp/**` | Exploración temporal |

## Variantes según tipo de cambio

| Tipo de PR | Tipo | Ejemplos |
|---|---|---|
| Pipeline nuevo | `feat` | `feat({pipeline}): add extract stage` |
| Bug en pipeline existente | `fix` | `fix({pipeline}): handle null municipios` |
| Cambio de funcionalidad | `update` | `update({pipeline}): switch to monthly cron` |
| Refactor sin cambio funcional | `refactor` | `refactor({pipeline}): extract hash to utils` |
| Solo documentación | `docs` | `docs({pipeline}): update ERD diagram` |
| Dependencias / config | `chore` | `chore({pipeline}): upgrade pandas to 2.2` |
| Cambios transversales a core | `feat(core)` / `feat(utils)` | `feat(core): add sync_id_sequence util` |

## Preparar el push y el PR

```bash
# Revisión final
git log --oneline $(git merge-base HEAD develop)..HEAD

# Subida (confirmar antes de ejecutar)
git push -u origin <nombre-rama>
```

Abrir PR hacia `develop` y completar el checklist de `CONTRIBUTING.md`. **Nunca** `--force` en ramas compartidas. **Nunca** push directo a `main`/`develop`.

## Checklist antes del push

- [ ] `ruff check` pasa sin errores.
- [ ] `just flyway-reset {pipeline}` y `just flyway-validate {pipeline}` OK.
- [ ] El pipeline corre end-to-end en bootstrap (`python dags/etl_{pipeline}.py`).
- [ ] `.env` y `flyway.conf` NO están staged.
- [ ] Cada commit tiene mensaje convencional `<tipo>({pipeline}): <descripción>`.
- [ ] Orden lógico: migrations → config → schemas → stages → DAG → docs.
- [ ] Sin commits `WIP` ni `debug`.
- [ ] Primera línea ≤ 72 caracteres.
