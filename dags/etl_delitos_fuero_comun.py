import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

try:
    from airflow import DAG
    from airflow.providers.standard.operators.python import PythonOperator

    _AIRFLOW_AVAILABLE = True
except ImportError:
    _AIRFLOW_AVAILABLE = False

from core.pipeline import Pipeline
from core.pipelines.delitos_fuero_comun.stages.extract import DelitosExtract
from core.pipelines.delitos_fuero_comun.constants.load import DelitosLoad
from core.pipelines.delitos_fuero_comun.constants.transform import DelitosTransform


def run_bootstrap() -> None:
    Pipeline(
        name="delitos_fuero_comun",
        stages=[
            DelitosExtract(mode="bootstrap"),
            DelitosTransform(mode="bootstrap"),
            DelitosLoad(mode="bootstrap"),
        ],
    ).run(mode="bootstrap")


def run_update() -> None:
    Pipeline(
        name="delitos_fuero_comun",
        stages=[
            DelitosExtract(mode="update"),
            DelitosTransform(mode="update"),
            DelitosLoad(mode="update"),
        ],
    ).run(mode="update")


_default_args_bootstrap = {
    "owner": "iieg",
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

_default_args_update = {
    "owner": "iieg",
    "retries": 2,
    "retry_delay": timedelta(minutes=10),
}

if _AIRFLOW_AVAILABLE:
    with DAG(
        "etl_delitos_fuero_comun_bootstrap",
        default_args=_default_args_bootstrap,
        description="Delitos Fuero Común Bootstrap — SSPC histórico 2015-2025 (on demand)",
        start_date=datetime(2024, 1, 1),
        schedule=None,
        catchup=False,
        tags=["etl", "delitos_fuero_comun", "sspc", "bootstrap"],
    ) as dag_bootstrap:
        PythonOperator(task_id="run_bootstrap", python_callable=run_bootstrap)

    with DAG(
        "etl_delitos_fuero_comun_update",
        default_args=_default_args_update,
        description="Delitos Fuero Común Update — SSPC datos 2026 (mensual)",
        start_date=datetime(2024, 1, 1),
        schedule="0 12 1 * *",
        catchup=False,
        tags=["etl", "delitos_fuero_comun", "sspc", "update"],
    ) as dag_update:
        PythonOperator(task_id="run_update", python_callable=run_update)


if __name__ == "__main__":
    run_bootstrap()
