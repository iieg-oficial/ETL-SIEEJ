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
from core.pipelines.pobreza_multidimensional.consts import DATA_YEARS
from core.pipelines.pobreza_multidimensional.stages.extract import PobrezaMultidimensionalExtract
from core.pipelines.pobreza_multidimensional.stages.load import PobrezaMultidimensionalLoad
from core.pipelines.pobreza_multidimensional.stages.transform import PobrezaMultidimensionalTransform


def run_bootstrap() -> None:
    """Ejecuta el pipeline de bootstrap para todos los años configurados."""
    for year in DATA_YEARS:
        Pipeline(
            name="pobreza_multidimensional",
            stages=[
                PobrezaMultidimensionalExtract(year=year),
                PobrezaMultidimensionalTransform(year=year),
                PobrezaMultidimensionalLoad(year=year),
            ],
        ).run(mode="bootstrap")


default_args = {
    "owner": "iieg",
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

if _AIRFLOW_AVAILABLE:
    with DAG(
        "etl_pobreza_multidimensional_bootstrap",
        default_args=default_args,
        description=("Pobreza Multidimensional Bootstrap — CONEVAL MMP 2016/2018/2020/2022 (on demand)"),
        start_date=datetime(2024, 1, 1),
        schedule=None,
        catchup=False,
        tags=["etl", "pobreza_multidimensional", "bootstrap", "on-demand", "coneval"],
    ) as dag_bootstrap:
        PythonOperator(task_id="run_bootstrap", python_callable=run_bootstrap)


if __name__ == "__main__":
    run_bootstrap()
