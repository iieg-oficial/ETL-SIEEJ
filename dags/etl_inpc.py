import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from datetime import datetime, timedelta

from core.db import Database
from core.pipeline import Pipeline
from core.pipelines.inpc.stages.extract import InpcExtract
from core.pipelines.inpc.stages.transform import InpcTransform
from core.pipelines.inpc.stages.load import InpcLoad
from core.pipelines.inpc.schemas import InpcCiudades
from core.pipelines.inpc.config import settings
from core.schedules import schedule_for
from core.utils.bulk_ops import get_last_update


def run_bootstrap():
    pipeline = Pipeline(
        name="inpc",
        stages=[
            InpcExtract(start_year=settings.BOOTSTRAP_START_YEAR),
            InpcTransform(),
            InpcLoad(),
        ],
    )
    pipeline.run(mode="bootstrap")


def run_update():
    db = Database(settings.DB_NAME, settings.database_url)
    db.connect()
    with db.get_session() as session:
        last_date = get_last_update(session, InpcCiudades, InpcCiudades.fecha.key)
    db.disconnect()

    start_year = last_date.year if last_date else settings.BOOTSTRAP_START_YEAR

    pipeline = Pipeline(
        name="inpc",
        stages=[
            InpcExtract(start_year=start_year),
            InpcTransform(date_from=last_date),
            InpcLoad(),
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
    "etl_inpc_bootstrap",
    default_args=default_args_bootstrap,
    description="INPC Bootstrap - Initial full load (On Demand)",
    start_date=datetime(year=2026, month=1, day=12, hour=3),
    catchup=False,
    max_active_runs=1,
    tags=["etl", "inpc", "bootstrap", "on-demand"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )

with DAG(
    "etl_inpc_update",
    default_args=default_args_update,
    description="INPC Update - Monthly update",
    schedule=schedule_for("etl_inpc_update"),
    start_date=datetime(year=2026, month=1, day=12, hour=3),
    catchup=False,
    max_active_runs=1,
    tags=["etl", "inpc", "update"],
) as dag_update:
    update_task = PythonOperator(
        task_id="run_update",
        python_callable=run_update,
    )


if __name__ == "__main__":
    # run_bootstrap()
    run_update()
