import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

from core.pipeline import Pipeline
from core.pipelines.conapo.stages.extract import ConapoExtract
from core.pipelines.conapo.stages.transform import ConapoTransform
from core.pipelines.conapo.stages.load import ConapoLoad


def run_bootstrap():
    pipeline = Pipeline(
        name="conapo",
        stages=[
            ConapoExtract(),
            ConapoTransform(),
            ConapoLoad(),
        ],
    )
    pipeline.run(mode="bootstrap")


default_args = {
    "owner": "Alejandro Zarate",
    "retries": 3,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    "etl_conapo_bootstrap",
    default_args=default_args,
    description="CONAPO Population Bootstrap - On Demand",
    start_date=datetime(year=2024, month=1, day=1),
    catchup=False,
    max_active_runs=1,
    tags=["etl", "conapo", "bootstrap", "on-demand", "population"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )

if __name__ == "__main__":
    run_bootstrap()
