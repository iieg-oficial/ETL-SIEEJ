import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from core.pipeline import Pipeline
from core.pipelines.defunciones.stages.extract import DefuncionesExtract
from core.pipelines.defunciones.stages.load import DefuncionesLoad
from core.pipelines.defunciones.stages.transform import DefuncionesTransform


def run_bootstrap() -> None:
    pipeline = Pipeline(
        name="defunciones",
        stages=[
            DefuncionesExtract(mode="bootstrap"),
            DefuncionesTransform(mode="bootstrap"),
            DefuncionesLoad(mode="bootstrap"),
        ],
    )
    pipeline.run(mode="bootstrap")


default_args_bootstrap = {
    "owner": "Jose Velazco",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "etl_defunciones_bootstrap",
    default_args=default_args_bootstrap,
    description="Defunciones Bootstrap - carga de catalogos on demand",
    start_date=datetime(year=2026, month=1, day=1),
    schedule=None,
    catchup=False,
    tags=["etl", "defunciones", "bootstrap", "on-demand"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )


if __name__ == "__main__":
    run_bootstrap()
