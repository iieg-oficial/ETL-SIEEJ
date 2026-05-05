---
name: airflow
description: Reglas arquitecturales de pipelines ETL con el patrón Stage/Pipeline y DAGs de Airflow. Define responsabilidades por etapa y contrato entre stages.
applyTo: "dags/**/*.py,core/pipelines/**/*.py,core/pipelines/**/stages/*.py"
---

# Airflow & ETL Architecture — Reglas

> Los templates de código completos están en los skills `scaffold-pipeline` y `scd2-pattern`. Este archivo define **qué hacer y qué no**, no cómo escribirlo.

## Patrón Stage

Toda etapa hereda de `core.pipelines.stage.Stage` e implementa exactamente tres métodos: `source()` → `action()` → `finalization()`.

| Método | Responsabilidad |
|---|---|
| `source()` | Valida `input_data`, abre conexiones, construye URLs. Devuelve el contexto que recibirá `action()`. |
| `action()` | Lógica principal (descarga / transformación / inserción). Devuelve el contexto que recibirá `finalization()`. |
| `finalization()` | Cierra recursos, limpia directorios temporales, reporta métricas de salida. |

- `Stage.__init__(pipeline_name, stage_name)` configura automáticamente `self.work_dir = data/{stage_name}/{pipeline_name}/` y `self.logger`.
- El retorno de cada método es un `dict` que se propaga al siguiente.
- `source()` de la primera etapa recibe `None`.

## Orquestador Pipeline

`core.pipeline.Pipeline(name, stages).run(mode)` ejecuta los stages en orden y propaga el contexto. `mode` siempre es `"bootstrap"` o `"update"`.

## Estructura obligatoria por pipeline

```
core/pipelines/{nombre}/{__init__.py, config.py, consts.py, schemas.py, .env.example}
core/pipelines/{nombre}/stages/{__init__.py, extract.py, transform.py, load.py}
dags/etl_{nombre}.py
migrations/{nombre}/{flyway.conf.example, sql/}
```

No reubicar archivos, no inventar carpetas adicionales. Si necesitas un helper solo usado por un pipeline, créalo dentro de `core/pipelines/{nombre}/`.

## Patrón DAG — dual por pipeline

Cada pipeline expone **uno o dos** DAGs en `dags/etl_{nombre}.py`:

| DAG | Schedule | Cuándo |
|---|---|---|
| `etl_{nombre}_bootstrap` | `schedule=None` | Siempre |
| `etl_{nombre}_update` | cron según periodicidad | Solo si periodicidad ≤ 3 meses |

Reglas:

- `catchup=False` siempre (salvo backfill explícito documentado).
- `if __name__ == "__main__": run_bootstrap()` al final del DAG para ejecución local.
- `sys.path.append(...)` al inicio para resolver `core.*` fuera de Docker.
- Un DAG = un pipeline. No mezclar múltiples pipelines en un solo archivo.
- No usar variables mutables globales; toda configuración va en `config.py` / `consts.py`.

## Responsabilidades por stage

### `extract.py`

- Descarga / lee la fuente y guarda artefacto en `self.work_dir`.
- Devuelve `{"file_path": str(path)}` (o lista de paths).
- **No** limpia `work_dir` en `finalization()` — lo hace `transform`.
- Para HTTP: `requests.get(url, timeout=180)` + `raise_for_status()` + validar `response.content`.
- Para Drive: usar `core.utils.gdrive`.

### `transform.py`

- Recibe `file_path`, produce DataFrame limpio.
- Orden recomendado: leer → normalizar headers → rename → limpiar nulos → parsear fechas → normalizar geo → extraer catálogos → sanitizar NaN residuales.
- Usar **siempre** las utilidades del proyecto: `core.utils.normalize`, `core.utils.clean`, `core.utils.parse_datetime`.
- En `finalization()`: `clean_directory(data/extract/{pipeline})` y `clean_directory(self.work_dir)`.
- Devuelve `{"df": df, "catalogs": dict, "row_count": int}`.

### `load.py`

- Abre conexión con `Database(PIPELINE_NAME, settings.database_url)` en `source()`.
- Ejecuta `{Pipeline}Base.metadata.create_all(engine)` para idempotencia.
- Usa `core.utils.bulk_ops`: `insert_records` (catálogos), `bulk_insert` (datos grandes), `upsert_records` (update sin historial).
- Para SCD2: aplicar skill `scd2-pattern`.
- Para cvegeo: aplicar skill `cvegeo-integration`.
- Ejecuta `sync_id_sequence` después de cargas masivas.
- Cierra la BD y limpia `self.work_dir` en `finalization()`.

## Prohibiciones

- **No** mezclar acceso a BD en `transform.py`.
- **No** mezclar transformaciones en `load.py` (solo resolución de IDs y hash).
- **No** usar `print()` — usar `self.logger`.
- **No** hardcodear credenciales, URLs o rutas (siempre en `config.py` / `consts.py`).
- **No** crear DAGs sin `catchup=False`.
- **No** devolver tipos distintos a `dict` desde los métodos de `Stage`.

## Referencias

- Skill `scaffold-pipeline` — templates completos de los 4 archivos del pipeline + DAG.
- Skill `scd2-pattern` — lógica de bootstrap / update con historial.
- Skill `cvegeo-integration` — resolución de municipios.
- `core/pipelines/repd/` — pipeline canónico completo.
- `core/pipelines/fiscalia/` — variante Google Drive.
