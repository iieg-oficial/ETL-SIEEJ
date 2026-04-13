import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

from core.pipeline import Pipeline
from core.pipelines.marginacion.config import settings
from core.pipelines.marginacion.stages.extract import MarginacionExtract
from core.pipelines.marginacion.stages.transform import MarginacionTransform
from core.pipelines.marginacion.stages.load import MarginacionLoad


def run_bootstrap():
    for year in settings.DATA_YEARS:
        pipeline = Pipeline(
            name="marginacion",
            stages=[
                MarginacionExtract(year=year),
                MarginacionTransform(year=year),
                MarginacionLoad(year=year),
            ],
        )
        pipeline.run(mode="bootstrap")


default_args = {
    "owner": "José Velazco H.",
    "retries": 3,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    "etl_marginacion_bootstrap",
    default_args=default_args,
    description="Marginacion Bootstrap - CONAPO (On Demand)",
    start_date=datetime(year=2024, month=1, day=1),
    catchup=False,
    tags=["etl", "marginacion", "bootstrap", "on-demand", "conapo"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )

if __name__ == "__main__":
    run_bootstrap()
