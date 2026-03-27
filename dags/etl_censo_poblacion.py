import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

from core.pipeline import Pipeline
from core.pipelines.censo_poblacion.stages.extract import CensoPoblacionExtract
from core.pipelines.censo_poblacion.stages.transform import CensoPoblacionTransform
from core.pipelines.censo_poblacion.stages.load import CensoPoblacionLoad


def run_bootstrap():
    pipeline = Pipeline(
        name="censo_poblacion",
        stages=[
            CensoPoblacionExtract(),
            CensoPoblacionTransform(),
            CensoPoblacionLoad(),
        ],
    )
    pipeline.run(mode="bootstrap")


default_args = {
    "owner": "José Velazco H.",
    "retries": 3,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    "etl_censo_poblacion_bootstrap",
    default_args=default_args,
    description="Censo Poblacion Bootstrap - INEGI 2010, 2015, 2020 (On Demand)",
    start_date=datetime(year=2024, month=1, day=1),
    catchup=False,
    tags=["etl", "censo_poblacion", "bootstrap", "on-demand", "inegi"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )

if __name__ == "__main__":
    run_bootstrap()
