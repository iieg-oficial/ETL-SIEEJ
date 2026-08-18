import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from core.pipeline import Pipeline
from core.pipelines.enoe.config import settings
from core.pipelines.enoe.stages.extract import EnoeExtract
from core.pipelines.enoe.stages.load import EnoeLoad
from core.pipelines.enoe.stages.transform import EnoeTransform
from core.schedules import schedule_for


def run_bootstrap():
    pipeline = Pipeline(
        name="enoe",
        stages=[
            EnoeExtract(mode="bootstrap", start_year=settings.BOOTSTRAP_START_YEAR),
            EnoeTransform(mode="bootstrap"),
            EnoeLoad(mode="bootstrap"),
        ],
    )
    pipeline.run(mode="bootstrap")


def run_update():
    pipeline = Pipeline(
        name="enoe",
        stages=[
            EnoeExtract(mode="incremental"),
            EnoeTransform(mode="incremental"),
            EnoeLoad(mode="incremental"),
        ],
    )
    pipeline.run(mode="incremental")


default_args_bootstrap = {
    "owner": "Hector Moreno",
    "retries": 2,
    "retry_delay": timedelta(hours=1),
}

default_args_update = {
    "owner": "Hector Moreno",
    "retries": 3,
    "retry_delay": timedelta(days=3),
}

with DAG(
    "etl_enoe_bootstrap",
    default_args=default_args_bootstrap,
    description="ENOE Bootstrap — Carga histórica desde 2005 T1 (On Demand)",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["etl", "enoe", "bootstrap", "on-demand"],
) as dag_bootstrap:
    PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )

# Día 70 de cada trimestre: 10 de marzo, junio, septiembre y diciembre
with DAG(
    "etl_enoe_update",
    default_args=default_args_update,
    description="ENOE Update — Actualización trimestral (día 70 del trimestre)",
    schedule=schedule_for("etl_enoe_update"),
    start_date=datetime(2026, 3, 10, 3),
    catchup=False,
    max_active_runs=1,
    tags=["etl", "enoe", "update"],
) as dag_update:
    PythonOperator(
        task_id="run_update",
        python_callable=run_update,
    )


if __name__ == "__main__":
    run_bootstrap()
