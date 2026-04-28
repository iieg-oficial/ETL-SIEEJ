---
name: dag-airflow
description: Template dummy para crear el DAG de Airflow de un pipeline ETL siguiendo la convención del proyecto.
---

## Cuándo usar

Después de implementar `stages/{extract,transform,load}.py`. El DAG orquesta los stages y expone `bootstrap` y `update`.

## Reglas

- Airflow 3.x. Sintaxis `@dag` + `@task` (TaskFlow API).
- Retries por default 2, `retry_delay` 5 min.
- `catchup=False` salvo justificación explícita.
- Schedule:
  - Iterable: cron / preset alineado con periodicidad real.
  - No iterable: `schedule=None` (bootstrap manual).
- `start_date` = primer año disponible para iterables; `datetime.now() - 1d` para no-iterables.

## Template — `dags/etl_{flujo}.py`

```python
from datetime import datetime, timedelta

from airflow.decorators import dag, task

from core.pipelines.{flujo}.config import {Flujo}Config
from core.pipelines.{flujo}.stages.extract import Extract
from core.pipelines.{flujo}.stages.transform import Transform
from core.pipelines.{flujo}.stages.load import Load

DEFAULT_ARGS = {
    "owner": "iieg",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="etl_{flujo}",
    description="Pipeline ETL {flujo}",
    start_date=datetime(2024, 1, 1),
    schedule=None,                 # iterable: "@yearly" o cron real
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["etl", "{flujo}"],
    params={"bootstrap": False, "year": None},
)
def etl_{flujo}():

    @task
    def extract(year: int | None) -> str:
        stage = Extract(year=year) if year else Extract()
        return stage.run()

    @task
    def transform(extract_path: str) -> str:
        return Transform(input_path=extract_path).run()

    @task
    def load(transform_path: str, bootstrap: bool) -> dict:
        return Load(input_path=transform_path, bootstrap=bootstrap).run()

    extracted = extract("{{ params.year }}")
    transformed = transform(extracted)
    load(transformed, "{{ params.bootstrap }}")


etl_{flujo}_dag = etl_{flujo}()


def main(bootstrap: bool = True, year: int | None = None) -> None:
    """Ejecución directa para pruebas locales."""
    cfg = {Flujo}Config()
    extract_path = Extract(year=year, config=cfg).run() if year else Extract(config=cfg).run()
    transform_path = Transform(input_path=extract_path, config=cfg).run()
    Load(input_path=transform_path, bootstrap=bootstrap, config=cfg).run()


if __name__ == "__main__":
    main(bootstrap=True)
```

## Iterables

Para pipelines iterables, parametrizar `year` (o entidad) en el DAG y propagar a cada stage. Usar `upsert_records` con `conflict_keys` en Load.

## Verificación local

```bash
python dags/etl_{flujo}.py
```

Debe ejecutar el `main()` en bootstrap sin errores.
