import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from core.db import Database
from core.pipeline import Pipeline
from core.pipelines.agropecuario_siap.config import settings
from core.pipelines.agropecuario_siap.helpers import year_has_data
from core.pipelines.agropecuario_siap.schemas import StgAgricola
from core.pipelines.agropecuario_siap.stages.extract import AgropecuarioExtract
from core.pipelines.agropecuario_siap.stages.load import AgropecuarioLoad
from core.pipelines.agropecuario_siap.stages.transform import AgropecuarioTransform
from core.utils.bulk_ops import get_last_update
from core.utils.logger import get_logger

logger = get_logger(settings.PIPELINE_NAME)


def run_bootstrap():
    for year in range(settings.START_DATE, settings.END_DATE + 1):
        Pipeline(
            name=settings.PIPELINE_NAME,
            stages=[
                AgropecuarioExtract(year=year),
                AgropecuarioTransform(year=year),
                AgropecuarioLoad(year=year),
            ],
        ).run(mode="bootstrap")


def run_update():
    current_year = datetime.now().year
    db = Database(settings.DB_NAME, settings.database_url)
    db.connect()
    try:
        with db.get_session() as session:
            last_year = get_last_update(session, StgAgricola, StgAgricola.anio.key)
    finally:
        db.disconnect()

    start_year = (last_year + 1) if last_year else settings.START_DATE

    for year in range(start_year, current_year + 1):
        if not year_has_data(year):
            logger.info(f"[update] Year {year} returned empty, stopping update search")
            break

        Pipeline(
            name=settings.PIPELINE_NAME,
            stages=[
                AgropecuarioExtract(year=year),
                AgropecuarioTransform(year=year),
                AgropecuarioLoad(year=year),
            ],
        ).run(mode="update")


default_args = {
    "owner": "José Velazco H.",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "etl_agropecuario_siap_bootstrap",
    default_args=default_args,
    description="Agropecuario SIAP Bootstrap — Carga inicial desde 2003 (On Demand)",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    schedule=None,
    tags=["etl", "agropecuario_siap", "bootstrap", "on-demand", "siap"],
) as dag_bootstrap:
    PythonOperator(task_id="run_bootstrap", python_callable=run_bootstrap)


with DAG(
    "etl_agropecuario_siap_update",
    default_args=default_args,
    description="Agropecuario SIAP Update — Actualización anual (SIAP)",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    schedule="@yearly",
    tags=["etl", "agropecuario_siap", "update", "siap"],
) as dag_update:
    PythonOperator(task_id="run_update", python_callable=run_update)


if __name__ == "__main__":
    run_bootstrap()
