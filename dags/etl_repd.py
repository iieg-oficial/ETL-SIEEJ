import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator

from core.pipeline import Pipeline
from core.pipelines.repd.stages.extract import REPDExtractor
from core.pipelines.repd.stages.load import REPDLoader
from core.pipelines.repd.stages.transform import REPDTransformer
from core.schedules import schedule_for


def run_bootstrap():
    """Ejecuta la carga inicial completa del REPD"""
    pipeline = Pipeline(
        name="repd",
        stages=[
            REPDExtractor(mode="bootstrap"),
            REPDTransformer(mode="bootstrap"),
            REPDLoader(mode="bootstrap"),
        ],
    )
    pipeline.run(mode="bootstrap")


def run_update():
    """Ejecuta carga incremental del REPD"""
    pipeline = Pipeline(
        name="repd",
        stages=[
            REPDExtractor(mode="update"),
            REPDTransformer(mode="update"),
            REPDLoader(mode="update"),
        ],
    )
    pipeline.run(mode="update")


# ============================================================================
# DAG 1: BOOTSTRAP (Carga inicial - Bajo demanda)
# ============================================================================

default_args_bootstrap = {
    "owner": "Alejandro Zarate",
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    "etl_repd_bootstrap",
    default_args=default_args_bootstrap,
    description="REPD Bootstrap - Carga inicial completa (On Demand)",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    schedule=None,
    tags=["etl", "repd", "bootstrap", "on-demand", "personas-desaparecidas"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )
    trigger_geoserver_sync = TriggerDagRunOperator(
        task_id="trigger_geoserver_sync",
        trigger_dag_id="etl_geoserver_sync",
        conf={"pipeline": "repd"},
        wait_for_completion=False,
    )
    bootstrap_task >> trigger_geoserver_sync


# ============================================================================
# DAG 2: UPDATE (Carga incremental - Mensual)
# ============================================================================

default_args_update = {
    "owner": "Alejandro Zarate",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "etl_repd_update",
    default_args=default_args_update,
    description="REPD Update - Carga incremental mensual",
    schedule=schedule_for("etl_repd_update"),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["etl", "repd", "update", "monthly", "personas-desaparecidas"],
) as dag_update:
    update_task = PythonOperator(
        task_id="run_update",
        python_callable=run_update,
    )
    trigger_geoserver_sync = TriggerDagRunOperator(
        task_id="trigger_geoserver_sync",
        trigger_dag_id="etl_geoserver_sync",
        conf={"pipeline": "repd"},
        wait_for_completion=False,
    )
    update_task >> trigger_geoserver_sync


if __name__ == "__main__":
    run_bootstrap()
