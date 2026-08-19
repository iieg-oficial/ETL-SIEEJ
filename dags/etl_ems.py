import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from core.schedules import schedule_for


PIPELINE_NAME = "ems"


def run(mode: str = "bootstrap") -> None:
    """The INEGI ZIP always ships the full 2013-to-date series, so bootstrap and
    update run the same flow.

    What differs is the cadence: the upsert rewrites the preliminary figures as
    INEGI revises them and appends the newly published months.

    Imports live inside the callable on purpose: the DAG processor re-parses this
    file every couple of minutes, and pandas plus SQLAlchemy are only needed when
    a task actually runs.
    """
    from core.pipeline import Pipeline
    from core.pipelines.ems.stages.extract import EmsExtract
    from core.pipelines.ems.stages.load import EmsLoad
    from core.pipelines.ems.stages.transform import EmsTransform

    Pipeline(
        name=PIPELINE_NAME,
        stages=[EmsExtract(), EmsTransform(), EmsLoad()],
    ).run(mode=mode)


def run_bootstrap() -> None:
    run(mode="bootstrap")


def run_update() -> None:
    run(mode="update")


default_args = {
    "owner": "José Velazco H.",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "etl_ems_bootstrap",
    default_args=default_args,
    description="EMS Bootstrap — Carga inicial 2013 a la fecha (On Demand)",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    schedule=None,
    tags=["etl", "ems", "bootstrap", "on-demand", "inegi"],
) as dag_bootstrap:
    PythonOperator(task_id="run_bootstrap", python_callable=run_bootstrap)


with DAG(
    "etl_ems_update",
    default_args=default_args,
    description="EMS Update — Actualización mensual (INEGI)",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    schedule=schedule_for("etl_ems_update"),
    tags=["etl", "ems", "update", "inegi"],
) as dag_update:
    PythonOperator(task_id="run_update", python_callable=run_update)


if __name__ == "__main__":
    run_bootstrap()
