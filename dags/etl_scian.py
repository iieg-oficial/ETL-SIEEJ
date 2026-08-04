import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

from core.pipeline import Pipeline
from core.pipelines.scian.stages.extract import ScianExtract
from core.pipelines.scian.stages.transform import ScianTransform
from core.pipelines.scian.stages.load import ScianLoad


def run_bootstrap():
    pipeline = Pipeline(
        name="scian",
        stages=[
            ScianExtract(),
            ScianTransform(),
            ScianLoad(),
        ],
    )
    pipeline.run(mode="bootstrap")


default_args = {
    "owner": "alejandroiieg",
    "retries": 3,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    "etl_scian_bootstrap",
    default_args=default_args,
    description="SCIAN Bootstrap - Estructura del SCIAN México 2023, INEGI (On Demand)",
    start_date=datetime(year=2023, month=1, day=1),
    schedule=None,
    catchup=False,
    tags=["etl", "scian", "bootstrap", "on-demand", "inegi"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )

if __name__ == "__main__":
    run_bootstrap()
