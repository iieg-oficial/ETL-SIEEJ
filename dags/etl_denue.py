import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

from core.pipeline import Pipeline
from core.pipelines.denue.stages.extract import DenueExtract
from core.pipelines.denue.stages.transform import DenueTransform
from core.pipelines.denue.stages.load import DenueLoad
from core.pipelines.denue.constants import ENTIDADES_MEXICO


def run_bootstrap():
    for entidad in ENTIDADES_MEXICO:
        pipeline = Pipeline(
            name="denue",
            stages=[
                DenueExtract(mode="bootstrap", entidad=entidad),
                DenueTransform(mode="bootstrap", entidad=entidad),
                DenueLoad(mode="bootstrap", entidad=entidad),
            ],
        )
        pipeline.run(mode="bootstrap")


def run_update():
    for entidad in ENTIDADES_MEXICO:
        pipeline = Pipeline(
            name="denue",
            stages=[
                DenueExtract(mode="update", entidad=entidad),
                DenueTransform(mode="update", entidad=entidad),
                DenueLoad(mode="update", entidad=entidad),
            ],
        )
        pipeline.run(mode="update")


default_args = {
    "owner": "José Velazco H.",
    "retries": 3,
    "retry_delay": timedelta(days=10),
}

with DAG(
    "etl_denue_bootstrap",
    default_args=default_args,
    description="DENUE Bootstrap - All entidades (On Demand)",
    start_date=datetime(year=2025, month=1, day=20),
    schedule=None,
    catchup=False,
    tags=["etl", "denue", "bootstrap", "on-demand", "inegi"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )

with DAG(
    "etl_denue_update",
    default_args=default_args,
    description="DENUE Update - All entidades",
    start_date=datetime(year=2025, month=1, day=20),
    schedule=timedelta(days=10),
    catchup=False,
    tags=["etl", "denue", "update", "inegi"],
) as dag_update:
    update_task = PythonOperator(
        task_id="run_update",
        python_callable=run_update,
    )

if __name__ == "__main__":
    run_bootstrap()
