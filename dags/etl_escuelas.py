import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from core.pipeline import Pipeline
from core.pipelines.escuelas.stages.extract import EscuelasExtract
from core.pipelines.escuelas.stages.load import EscuelasLoad
from core.pipelines.escuelas.stages.transform import EscuelasTransform


def run_bootstrap() -> None:
    pipeline = Pipeline(
        name="escuelas",
        stages=[
            EscuelasExtract(mode="bootstrap"),
            EscuelasTransform(mode="bootstrap"),
            EscuelasLoad(mode="bootstrap"),
        ],
    )
    pipeline.run(mode="bootstrap")


default_args_bootstrap = {
    "owner": "Alejandro Zarate",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "etl_escuelas_bootstrap",
    default_args=default_args_bootstrap,
    description="Escuelas Bootstrap - carga completa on demand",
    start_date=datetime(year=2026, month=1, day=1),
    schedule=None,
    catchup=False,
    tags=["etl", "escuelas", "bootstrap", "on-demand"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )


if __name__ == "__main__":
    run_bootstrap()
