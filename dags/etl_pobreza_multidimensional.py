import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

try:
    from airflow import DAG
    from airflow.providers.standard.operators.python import PythonOperator
    from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator

    _AIRFLOW_AVAILABLE = True
except ImportError:
    _AIRFLOW_AVAILABLE = False

from core.pipeline import Pipeline
from core.pipelines.pobreza_multidimensional.stages.extract import PobrezaMultidimensionalExtract
from core.pipelines.pobreza_multidimensional.stages.load import PobrezaMultidimensionalLoad
from core.pipelines.pobreza_multidimensional.stages.transform import PobrezaMultidimensionalTransform


def run_bootstrap() -> None:
    """Ejecuta la ingestión completa de indicadores de pobreza municipal CONEVAL 2010/2015/2020."""
    Pipeline(
        name="pobreza_multidimensional",
        stages=[
            PobrezaMultidimensionalExtract(mode="bootstrap"),
            PobrezaMultidimensionalTransform(mode="bootstrap"),
            PobrezaMultidimensionalLoad(mode="bootstrap"),
        ],
    ).run(mode="bootstrap")


default_args = {
    "owner": "Héctor Moreno",
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

if _AIRFLOW_AVAILABLE:
    with DAG(
        "etl_pobreza_multidimensional_bootstrap",
        default_args=default_args,
        description=(
            "Pobreza Multidimensional Bootstrap — CONEVAL indicadores municipales "
            "2010/2015/2020 (on demand, cada ~2 años)"
        ),
        start_date=datetime(2024, 1, 1),
        schedule=None,
        catchup=False,
        max_active_runs=1,
        tags=["etl", "pobreza_multidimensional", "bootstrap", "on-demand", "coneval"],
    ) as dag_bootstrap:
        bootstrap_task = PythonOperator(task_id="run_bootstrap", python_callable=run_bootstrap)
        trigger_geoserver_sync = TriggerDagRunOperator(
            task_id="trigger_geoserver_sync",
            trigger_dag_id="etl_geoserver_sync",
            conf={"pipeline": "pobreza_multidimensional"},
            wait_for_completion=False,
        )
        bootstrap_task >> trigger_geoserver_sync


if __name__ == "__main__":
    run_bootstrap()
