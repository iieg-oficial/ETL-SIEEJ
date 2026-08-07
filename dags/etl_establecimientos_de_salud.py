import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

from core.pipeline import Pipeline
from core.pipelines.establecimientos_de_salud.stages.extract import EstablecimientosExtract
from core.pipelines.establecimientos_de_salud.stages.transform import EstablecimientosTransform
from core.pipelines.establecimientos_de_salud.stages.load import EstablecimientosLoad
from core.pipelines.establecimientos_de_salud.config import settings


def run_bootstrap():
    end_year = datetime.today().year
    for year in range(settings.BOOTSTRAP_START_YEAR, end_year + 1):
        month = settings.BOOTSTRAP_START_MONTH if year == settings.BOOTSTRAP_START_YEAR else 1
        pipeline = Pipeline(
            name="establecimientos_de_salud",
            stages=[
                EstablecimientosExtract(mode="bootstrap", year=year, month=month),
                EstablecimientosTransform(mode="bootstrap"),
                EstablecimientosLoad(mode="bootstrap"),
            ],
        )
        pipeline.run(mode="bootstrap")


def run_update():
    pipeline = Pipeline(
        name="establecimientos_de_salud",
        stages=[
            EstablecimientosExtract(mode="update"),
            EstablecimientosTransform(mode="update"),
            EstablecimientosLoad(mode="update"),
        ],
    )
    pipeline.run(mode="update")


default_args_bootstrap = {
    "owner": "José Velazco H.",
    "retries": 1,
    "retry_delay": timedelta(minutes=15),
}

default_args_update = {
    "owner": "José Velazco H.",
    "retries": 6,
    "retry_delay": timedelta(days=5),
}

with DAG(
    "etl_establecimientos_de_salud_bootstrap",
    default_args=default_args_bootstrap,
    description="Establecimientos de Salud Bootstrap - Initial full load (On Demand)",
    start_date=datetime(year=2024, month=1, day=22, hour=3),
    catchup=False,
    max_active_runs=1,
    tags=["etl", "establecimientos_de_salud", "bootstrap", "on-demand"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )

with DAG(
    "etl_establecimientos_de_salud_update",
    default_args=default_args_update,
    description="Establecimientos de Salud Update - Monthly catch-up",
    schedule="@monthly",
    start_date=datetime(year=2024, month=1, day=22, hour=3),
    catchup=False,
    max_active_runs=1,
    tags=["etl", "establecimientos_de_salud", "update"],
) as dag_update:
    update_task = PythonOperator(
        task_id="run_update",
        python_callable=run_update,
    )


if __name__ == "__main__":
    # run_bootstrap()
    run_update()
