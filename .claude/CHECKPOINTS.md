# CHECKPOINTS — Evaluación del estado final de un pipeline

> En sistemas multi-agente no se evalúa el camino, se evalúa el destino.
> Estos checkpoints son los criterios objetivos que un juez puede usar
> para decidir si el pipeline está completo y correcto.

---

## C1 — Estructura de archivos completa

- [ ] `core/pipelines/{pipeline}/constants.py` existe
- [ ] `core/pipelines/{pipeline}/attributes.py` o `attributes/` existe
- [ ] `core/pipelines/{pipeline}/schemas.py` existe
- [ ] `core/pipelines/{pipeline}/stages/extract.py` existe
- [ ] `core/pipelines/{pipeline}/stages/transform.py` existe
- [ ] `core/pipelines/{pipeline}/stages/load.py` existe
- [ ] `core/pipelines/{pipeline}/.env.example` existe
- [ ] `dags/etl_{pipeline}.py` existe
- [ ] `migrations/{pipeline}/sql/V1__foreign_tables.sql` existe
- [ ] `migrations/{pipeline}/sql/V3__tables_{pipeline}.sql` existe
- [ ] `migrations/{pipeline}/flyway.conf.example` existe

## C2 — Integridad del esquema

- [ ] Modelos SQLAlchemy usan estilo 2.0 (`Mapped`, `mapped_column`) — nunca 1.x
- [ ] Toda tabla tiene `id: Mapped[int]` como primary key
- [ ] Foreign keys siguen el patrón `{singular_table_name}_id`
- [ ] `schemas.py` refleja exactamente las columnas y tipos de las migraciones SQL
- [ ] Tablas de catálogo usan prefijo `cat_` (e.g., `cat_unidades`)
- [ ] Tablas principales usan prefijo `stg_` (e.g., `stg_establecimientos`)
- [ ] No hay URLs hardcodeadas en `stages/`

## C3 — Calidad del código

- [ ] No hay constantes UPPERCASE definidas fuera de `constants.py` (ni en `stages/`, `schemas.py`, `mappings.py`)
- [ ] No hay funciones helper definidas fuera de `helpers/` — los stages solo contienen métodos de clase
- [ ] Importaciones siguen el orden: stdlib → third-party → internal (`core.*`), con línea en blanco entre grupos
- [ ] Ninguna función nueva en el pipeline reimplementa lógica ya existente en `core/utils/`

## C4 — El pipeline ejecuta sin errores

- [ ] `just flyway-reset {pipeline}` termina con exit code 0
- [ ] `python dags/etl_{pipeline}.py` termina sin excepciones
- [ ] Registros insertados > 0 en la tabla principal

## C5 — Calidad de datos cargados

- [ ] `df.astype(object).where(df.notna(), None)` aplicado antes de cada insert
- [ ] SERIAL `id` excluido de la lista de columnas INSERT
- [ ] Catálogos cargados antes que la tabla principal
- [ ] `sync_id_sequence` llamado tras insertar catálogos con id fijo
- [ ] No hay `NaN` en columnas FK después de `.map()`

## C6 — Sesión cerrada correctamente

- [ ] `progress/history.md` tiene una entrada de la sesión actual
- [ ] `progress/current.md` solo contiene la plantilla vacía
- [ ] No hay archivos sin trackear sospechosos fuera del `.gitignore`
- [ ] Toda fase terminada tiene `status: "done"` en `feature_list.json`

---

**Cómo usar este archivo:** el agente revisor (`.claude/agents/reviewer.md`)
recorre cada checkbox, marca `[x]` o `[ ]`, y rechaza el cierre si quedan
boxes sin marcar en C1–C6.
