import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from core.pipeline import Pipeline
from core.pipelines.efipem.stages.extract import EfipemExtractor
from core.pipelines.efipem.stages.load import EfipemLoader
from core.pipelines.efipem.stages.transform import EfipemTransformer


def run_bootstrap():
    """Ejecuta la carga inicial completa de EFIPEM (cobertura nacional)."""
    pipeline = Pipeline(
        name="efipem",
        stages=[
            EfipemExtractor(mode="bootstrap"),
            EfipemTransformer(mode="bootstrap"),
            EfipemLoader(mode="bootstrap"),
        ],
    )
    pipeline.run(mode="bootstrap")


def run_update():
    """Ejecuta carga incremental SCD2: cierra versiones modificadas e inserta nuevas."""
    pipeline = Pipeline(
        name="efipem",
        stages=[
            EfipemExtractor(mode="update"),
            EfipemTransformer(mode="update"),
            EfipemLoader(mode="update"),
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
    "etl_efipem_bootstrap",
    default_args=default_args_bootstrap,
    description="EFIPEM Bootstrap - Carga inicial nacional (On Demand)",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    schedule=None,
    tags=["etl", "efipem", "bootstrap", "on-demand", "inegi", "finanzas-publicas"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )


# ============================================================================
# DAG 2: UPDATE (Carga incremental - Trimestral)
# Cron: dia 15 del 2do mes de cada trimestre (feb, may, ago, nov) a las 02:00
# ============================================================================

default_args_update = {
    "owner": "Alejandro Zarate",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "etl_efipem_update",
    default_args=default_args_update,
    description="EFIPEM Update - Re-ingesta trimestral SCD2",
    schedule="0 2 15 2,5,8,11 *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["etl", "efipem", "update", "quarterly", "inegi", "finanzas-publicas"],
) as dag_update:
    update_task = PythonOperator(
        task_id="run_update",
        python_callable=run_update,
    )


if __name__ == "__main__":
    run_bootstrap()
