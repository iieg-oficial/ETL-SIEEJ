import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

from core.pipeline import Pipeline
from core.pipelines.ilmm.stages.extract import IlmmExtract
from core.pipelines.ilmm.stages.transform import IlmmTransform
from core.pipelines.ilmm.stages.load import IlmmLoad
from core.pipelines.ilmm.config import settings


def run_bootstrap():
    pipeline = Pipeline(
        name="ilmm",
        stages=[
            IlmmExtract(years=settings.BOOTSTRAP_YEARS),
            IlmmTransform(),
            IlmmLoad(),
        ],
    )
    pipeline.run(mode="bootstrap")


def run_update():
    current_year = datetime.now().year
    pipeline = Pipeline(
        name="ilmm",
        stages=[
            IlmmExtract(years=[current_year]),
            IlmmTransform(),
            IlmmLoad(),
        ],
    )
    pipeline.run(mode="update")


default_args_bootstrap = {
    "owner": "José Velazco H.",
    "retries": 2,
    "retry_delay": timedelta(minutes=15),
}

default_args_update = {
    "owner": "José Velazco H.",
    "retries": 3,
    "retry_delay": timedelta(days=2),
}

with DAG(
    "etl_ilmm_bootstrap",
    default_args=default_args_bootstrap,
    description="ILMM Bootstrap - Carga histórica completa 2017-2024 (On Demand)",
    start_date=datetime(year=2026, month=1, day=12, hour=3),
    catchup=False,
    tags=["etl", "ilmm", "bootstrap", "on-demand"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )

with DAG(
    "etl_ilmm_update",
    default_args=default_args_update,
    description="ILMM Update - Actualización anual (1 de junio)",
    schedule="0 0 1 6 *",
    start_date=datetime(year=2026, month=1, day=12, hour=3),
    catchup=False,
    tags=["etl", "ilmm", "update"],
) as dag_update:
    update_task = PythonOperator(
        task_id="run_update",
        python_callable=run_update,
    )


if __name__ == "__main__":
    run_bootstrap()
