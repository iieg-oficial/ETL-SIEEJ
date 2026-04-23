import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from core.pipeline import Pipeline
from core.pipelines.etef.stages.extract import EtefExtractor
from core.pipelines.etef.stages.transform import EtefTransformer
from core.pipelines.etef.stages.load import EtefLoader


def run_bootstrap():
    Pipeline(
        name="etef",
        stages=[
            EtefExtractor(mode="bootstrap"),
            EtefTransformer(mode="bootstrap"),
            EtefLoader(mode="bootstrap"),
        ],
    ).run(mode="bootstrap")


def run_update():
    Pipeline(
        name="etef",
        stages=[
            EtefExtractor(mode="update"),
            EtefTransformer(mode="update"),
            EtefLoader(mode="update"),
        ],
    ).run(mode="update")


with DAG(
    "etl_etef_bootstrap",
    default_args={
        "owner": "iieg",
        "retries": 1,
        "retry_delay": timedelta(minutes=10),
    },
    description="ETEF Bootstrap — Carga inicial completa (on demand)",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    schedule=None,
    tags=["etl", "etef", "bootstrap", "on-demand"],
) as dag_bootstrap:
    PythonOperator(task_id="run_bootstrap", python_callable=run_bootstrap)


with DAG(
    "etl_etef_update",
    default_args={
        "owner": "iieg",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    description="ETEF Update — Carga trimestral de nuevos datos",
    schedule="0 0 1 */3 *",  # 1er día de cada trimestre (1 ene, 1 abr, 1 jul, 1 oct)
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["etl", "etef", "update"],
) as dag_update:
    PythonOperator(task_id="run_update", python_callable=run_update)


if __name__ == "__main__":
    run_bootstrap()
