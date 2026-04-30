---
name: dag-airflow
description: Genera el DAG de Airflow del pipeline con sus operadores bootstrap y update.
---

# Skill: DAG Airflow

## Purpose
Invocar en la Fase 5 para generar el archivo DAG que orquesta los stages del pipeline en Airflow 3.x.

## Steps

1. Definir el `dag_id` con el formato `etl_{flujo}_bootstrap` y `etl_{flujo}_update`.
2. Configurar `schedule_interval` según la frecuencia del pipeline (`None` para bootstrap, cron para update).
3. Definir `default_args` con `owner`, `retries` y `retry_delay` por separado para bootstrap y update.
4. Crear las funciones `run_bootstrap()` y `run_update()` que instancian `Pipeline` con sus stages correspondientes.
5. Encadenar los stages con `>>` en el orden: `extract >> transform >> load`.
6. Agregar la función `main()` al final para ejecución local en modo bootstrap sin Airflow.
7. Usar el patrón `sys.path.append` al inicio para resolver imports del proyecto.
8. Guardar en `./dags/etl_{flujo}.py`.

## Template

```python
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from datetime import timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from core.pipeline import Pipeline
from core.pipelines.{flujo}.stages.extract import Extract
from core.pipelines.{flujo}.stages.transform import Transform
from core.pipelines.{flujo}.stages.load import Load


# --- Bootstrap DAG ---

bootstrap_args = {
    "owner": "iieg",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="etl_{flujo}_bootstrap",
    default_args=bootstrap_args,
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
    tags=["{flujo}", "bootstrap"],
) as dag_bootstrap:

    def run_bootstrap():
        pipeline = Pipeline(
            stages=[Extract(mode="bootstrap"), Transform(mode="bootstrap"), Load(mode="bootstrap")]
        )
        pipeline.run()

    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )


# --- Update DAG ---

update_args = {
    "owner": "iieg",
    "retries": 2,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="etl_{flujo}_update",
    default_args=update_args,
    schedule_interval="0 6 * * *",  # adjust to pipeline frequency
    start_date=days_ago(1),
    catchup=False,
    tags=["{flujo}", "update"],
) as dag_update:

    def run_update():
        pipeline = Pipeline(
            stages=[Extract(mode="update"), Transform(mode="update"), Load(mode="update")]
        )
        pipeline.run()

    update_task = PythonOperator(
        task_id="run_update",
        python_callable=run_update,
    )


def main():
    run_bootstrap()


if __name__ == "__main__":
    main()
```
