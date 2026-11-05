# Plantilla de pipeline

Genera la estructura inicial de un pipeline. Se ejecuta desde la raíz del repositorio:

```shell
just new-pipeline <nombre_pipeline>
just new-pipeline <nombre_pipeline> "Nombre del responsable"
```

El segundo parámetro es opcional: define el `owner` del DAG, que por defecto es `IIEG`.

El nombre debe estar en `snake_case`. El comando falla sin modificar nada si el nombre es inválido o si el pipeline ya existe.

## Qué genera

```text
core/pipelines/<nombre_pipeline>/
├── stages/       # __init__.py, extract.py, transform.py, load.py
├── queries/
├── attributes/   # base.py, <nombre_pipeline>.py
├── constants/    # pipeline.py
├── mappings/
├── assets/
├── config.py
├── schemas.py
├── .env.example
├── .env
└── README.md

migrations/<nombre_pipeline>/
├── flyway.conf
├── flyway.conf.example
└── sql/

dags/
└── etl_<nombre_pipeline>.py
```

- `.env` y `flyway.conf` se crean como copia de sus `.example` y no se versionan. Hay que reemplazar sus marcadores por los valores reales.
- `README.md` parte de `docs/readme-pipeline.md`.
- Las carpetas sin archivos conservan un `.gitkeep` para que git las registre.
- El DAG generado es solo de bootstrap y bajo demanda (`schedule=None`). Para agregar un update, registra su calendario en `core/schedules/registry.py`.
- La plantilla no genera las migraciones SQL.
