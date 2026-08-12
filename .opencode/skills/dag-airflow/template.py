"""
Template de DAG de Airflow para un pipeline ETL.
Sustituir {flujo}, {Flujo} y los nombres de clase con los del pipeline real.
No referenciar pipelines existentes en el código generado.
"""
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from core.pipeline import Pipeline
from core.pipelines.{flujo}.stages.extract import {Flujo}Extract
from core.pipelines.{flujo}.stages.transform import {Flujo}Transform
from core.pipelines.{flujo}.stages.load import {Flujo}Load


def run_bootstrap() -> None:
    """Executes the initial full load of the {flujo} pipeline."""
    pipeline = Pipeline(
        name="{flujo}",
        stages=[
            {Flujo}Extract(mode="bootstrap"),
            {Flujo}Transform(mode="bootstrap"),
            {Flujo}Load(mode="bootstrap"),
        ],
    )
    pipeline.run(mode="bootstrap")


default_args_bootstrap = {
    "owner": "iieg",
    "retries": 1,
    "retry_delay": timedelta(minutes=30),
}

with DAG(
    "etl_{flujo}_bootstrap",
    default_args=default_args_bootstrap,
    description="{Flujo} Bootstrap — Initial full load (On Demand)",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    tags=["etl", "{flujo}", "bootstrap", "on-demand"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )


def run_update() -> None:
    """Performs the periodic update of the {flujo} pipeline."""
    pipeline = Pipeline(
        name="{flujo}",
        stages=[
            {Flujo}Extract(mode="update"),
            {Flujo}Transform(mode="update"),
            {Flujo}Load(mode="update"),
        ],
    )
    pipeline.run(mode="update")


default_args_update = {
    "owner": "iieg",
    "retries": 2,
    "retry_delay": timedelta(minutes=60),
}

with DAG(
    "etl_{flujo}_update",
    default_args=default_args_update,
    description="{Flujo} Update — Periodic incremental load",
    start_date=datetime(2024, 1, 1),
    schedule="0 6 1 * *",
    catchup=False,
    max_active_runs=1,
    tags=["etl", "{flujo}", "update"],
) as dag_update:
    update_task = PythonOperator(
        task_id="run_update",
        python_callable=run_update,
    )


def main() -> None:
    """Runs the full bootstrap pipeline locally for testing."""
    run_bootstrap()


if __name__ == "__main__":
    main()
