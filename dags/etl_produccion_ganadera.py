import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from core.pipeline import Pipeline
from core.pipelines.produccion_ganadera.config import settings
from core.pipelines.produccion_ganadera.helpers import get_update_start_year, year_has_data
from core.pipelines.produccion_ganadera.stages.extract import GanaderaExtract
from core.pipelines.produccion_ganadera.stages.load import GanaderaLoad
from core.pipelines.produccion_ganadera.stages.transform import GanaderaTransform
from core.schedules import schedule_for
from core.utils.logger import get_logger

logger = get_logger(settings.PIPELINE_NAME)


def run_bootstrap():
    for year in range(settings.START_DATE, settings.END_DATE + 1):
        Pipeline(
            name=settings.PIPELINE_NAME,
            stages=[
                GanaderaExtract(year=year),
                GanaderaTransform(year=year),
                GanaderaLoad(year=year),
            ],
        ).run(mode="bootstrap")


def run_update():
    start_year = get_update_start_year()

    for year in range(start_year, datetime.now().year + 1):
        if not year_has_data(year):
            logger.info(f"[update] Year {year} returned empty, stopping update search")
            break

        Pipeline(
            name=settings.PIPELINE_NAME,
            stages=[
                GanaderaExtract(year=year),
                GanaderaTransform(year=year),
                GanaderaLoad(year=year),
            ],
        ).run(mode="update")


default_args = {
    "owner": "José Velazco H.",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "etl_produccion_ganadera_bootstrap",
    default_args=default_args,
    description="Produccion Ganadera Bootstrap — Carga inicial desde 2003 (On Demand)",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    schedule=None,
    tags=["etl", "produccion_ganadera", "bootstrap", "on-demand", "siap"],
) as dag_bootstrap:
    PythonOperator(task_id="run_bootstrap", python_callable=run_bootstrap)


with DAG(
    "etl_produccion_ganadera_update",
    default_args=default_args,
    description="Produccion Ganadera Update — Actualización anual (SIAP)",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    schedule=schedule_for("etl_produccion_ganadera_update"),
    tags=["etl", "produccion_ganadera", "update", "siap"],
) as dag_update:
    PythonOperator(task_id="run_update", python_callable=run_update)


if __name__ == "__main__":
    run_bootstrap()
