import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

PIPELINE_NAME = "emim"


def run(mode: str = "bootstrap") -> None:
    """The INEGI ZIP always ships the full 2018-to-date series, so bootstrap and
    update run the same flow.

    What differs is the cadence: the upsert rewrites the preliminary figures as
    INEGI revises them and appends the newly published months.

    Imports live inside the callable on purpose: the DAG processor re-parses this
    file every couple of minutes, and pandas plus SQLAlchemy are only needed when
    a task actually runs.
    """
    from core.pipeline import Pipeline
    from core.pipelines.emim.stages.extract import EmimExtract
    from core.pipelines.emim.stages.load import EmimLoad
    from core.pipelines.emim.stages.transform import EmimTransform

    Pipeline(
        name=PIPELINE_NAME,
        stages=[EmimExtract(), EmimTransform(), EmimLoad()],
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
    "etl_emim_bootstrap",
    default_args=default_args,
    description="EMIM Bootstrap — Carga inicial 2018 a la fecha (On Demand)",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    schedule=None,
    tags=["etl", "emim", "bootstrap", "on-demand", "inegi"],
) as dag_bootstrap:
    PythonOperator(task_id="run_bootstrap", python_callable=run_bootstrap)


with DAG(
    "etl_emim_update",
    default_args=default_args,
    description="EMIM Update — Actualización mensual (INEGI)",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    schedule="@monthly",
    tags=["etl", "emim", "update", "inegi"],
) as dag_update:
    PythonOperator(task_id="run_update", python_callable=run_update)


if __name__ == "__main__":
    run_bootstrap()
