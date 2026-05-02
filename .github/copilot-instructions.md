# ETL SIEEJ — Guía del sistema de agentes / instructions / skills / prompts

Este repositorio usa un sistema modular de Copilot Customizations con responsabilidades separadas. Consulta este índice antes de asumir dónde está la información.

## Modelo mental (fábrica)

| Componente | Rol en la fábrica | Ubicación |
|---|---|---|
| **Agent** | Supervisor de planta — decide **qué** hacer y en qué orden | `.github/agents/*.agent.md` |
| **Instruction** | Manual operativo — reglas y convenciones auto-aplicadas | `.github/instructions/*.instructions.md` |
| **Skill** | Máquina especializada — templates y patrones on-demand | `.github/skills/<name>/SKILL.md` |
| **Prompt** | Orden de producción — entrada del cliente hacia el supervisor | `.github/prompts/*.prompt.md` |

## Reglas de separación

- **Agents** describen rol, entradas, plan por fases, deliverables y restricciones. **Nunca** contienen código, SQL o JSON de ejemplo: solo delegan a skills/instructions.
- **Instructions** contienen reglas de estilo, nomenclatura y convenciones aplicadas automáticamente por glob. Describen **qué hacer y qué no hacer**, no cómo escribirlo paso a paso.
- **Skills** son la única fuente de verdad para templates (código, SQL, estructura de archivos, secuencias de comandos). Se cargan on-demand cuando un agente los invoca.
- **Prompts** recopilan el input del usuario y lo entregan al agente correspondiente.

## Agents disponibles

| Agente | Invocable | Responsabilidad |
|---|---|---|
| `data-engineer` | Usuario | Orquestador principal del flujo "crear pipeline" (7 fases) |
| `eda` | Interno | Análisis exploratorio de la fuente → JSON estructurado |
| `db` | Interno | `schemas.py` + migraciones Flyway + validación |
| `etl` | Interno | Stages (extract/transform/load) + DAG + config |
| `docs` | Interno | `README.md` del pipeline + `.env.example` |
| `git` | Interno | Commits atómicos convencionales |
| `just` | Interno | Ejecución de comandos `just` y diagnóstico |

## Instructions (reglas auto-aplicadas)

| Instruction | applyTo |
|---|---|
| `python.instructions.md` | `**/*.py` |
| `commits.instructions.md` | `**` |
| `airflow.instructions.md` | `dags/**/*.py,core/pipelines/**/*.py,core/pipelines/**/stages/*.py` |
| `db.instructions.md` | `migrations/**/*.sql,core/pipelines/**/schemas.py,core/pipelines/**/config.py` |
| `flyway.instructions.md` | `justfile,migrations/**,compose.yaml` |

## Skills disponibles

| Skill | Uso |
|---|---|
| `scaffold-pipeline` | Templates de `config.py`, `consts.py`, `schemas.py`, stages, DAG, `.env.example` |
| `generate-migration` | Templates SQL V1–V4 + variante SCD2 |
| `eda-source` | Proceso de EDA y contrato JSON obligatorio |
| `pipeline-readme` | Template canónico del README de un pipeline |
| `cvegeo-integration` | Patrón FDW + resolución de municipios |
| `scd2-pattern` | Esquema `_current` + `_history` + lógica de load con versionado |
| `git-pipeline-commits` | Secuencia atómica de commits para un pipeline nuevo |
| `find-docs` / `context7-mcp` | Consultar docs actualizadas de libs/frameworks |

## Prompts disponibles

| Prompt | Agente al que delega |
|---|---|
| `/create-pipeline` | `data-engineer` |

## Regla de oro cuando se crea un pipeline

1. El usuario invoca `/create-pipeline` con el cuestionario.
2. `data-engineer` ejecuta las 7 fases en orden estricto.
3. Cada fase consume los skills e instructions correspondientes.
4. Ningún archivo se crea sin pasar por el skill que lo define.

## Dónde buscar qué

| Necesito saber... | Voy a... |
|---|---|
| Cómo se escribe un stage nuevo | Skill `scaffold-pipeline` |
| Reglas del patrón Stage/Pipeline | Instruction `airflow.instructions.md` |
| Cómo se escribe una migración V3 con SCD2 | Skill `generate-migration` + skill `scd2-pattern` |
| Reglas de nomenclatura SQL | Instruction `db.instructions.md` |
| Comandos para aplicar migraciones | Instruction `flyway.instructions.md` |
| Cómo integrar cvegeo | Skill `cvegeo-integration` |
| Formato del README del pipeline | Skill `pipeline-readme` |
| Convención de commits | Instruction `commits.instructions.md` |
| Secuencia exacta de commits al cerrar un pipeline | Skill `git-pipeline-commits` |
| Estilo de Python del proyecto | Instruction `python.instructions.md` |
