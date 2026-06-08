import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

from core.pipeline import Pipeline
from core.pipelines.nacimientos_dgis.stages.extract import NacimientosDgisExtract
from core.pipelines.nacimientos_dgis.stages.transform import NacimientosDgisTransform
from core.pipelines.nacimientos_dgis.stages.load import NacimientosDgisLoad


def run_bootstrap():
    pipeline = Pipeline(
        name="nacimientos_dgis",
        stages=[
            NacimientosDgisExtract(),
            NacimientosDgisTransform(),
            NacimientosDgisLoad(),
        ],
    )
    pipeline.run(mode="bootstrap")


default_args = {
    "owner": "Jose Velazco",
    "retries": 3,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    "etl_nacimientos_dgis_bootstrap",
    default_args=default_args,
    description="Nacimientos DGIS Bootstrap - On Demand",
    start_date=datetime(year=2024, month=1, day=1),
    catchup=False,
    schedule=None,
    tags=["etl", "nacimientos_dgis", "bootstrap", "on-demand", "demographics"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )

if __name__ == "__main__":
    run_bootstrap()
