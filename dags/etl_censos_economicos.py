import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from core.pipeline import Pipeline
from core.pipelines.censos_economicos.stages.extract import CEExtractor
from core.pipelines.censos_economicos.stages.load import CELoader
from core.pipelines.censos_economicos.stages.transform import CETransformer


def run_bootstrap():
    """Ejecuta la carga inicial completa de Censos Economicos"""
    pipeline = Pipeline(
        name="censos_economicos",
        stages=[
            CEExtractor(mode="bootstrap"),
            CETransformer(mode="bootstrap"),
            CELoader(mode="bootstrap"),
        ],
    )
    pipeline.run(mode="bootstrap")


def run_update():
    """Ejecuta carga incremental de Censos Economicos"""
    pipeline = Pipeline(
        name="censos_economicos",
        stages=[
            CEExtractor(mode="update"),
            CETransformer(mode="update"),
            CELoader(mode="update"),
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
    "etl_censos_economicos_bootstrap",
    default_args=default_args_bootstrap,
    description="Censos Economicos Bootstrap - Carga inicial completa (On Demand)",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["etl", "censos_economicos", "bootstrap", "on-demand", "inegi"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )


# ============================================================================
# DAG 2: UPDATE (Carga incremental - Anual)
# ============================================================================

default_args_update = {
    "owner": "Alejandro Zarate",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "etl_censos_economicos_update",
    default_args=default_args_update,
    description="Censos Economicos Update - Carga incremental anual",
    schedule="0 3 1 3 *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["etl", "censos_economicos", "update", "yearly", "inegi"],
) as dag_update:
    update_task = PythonOperator(
        task_id="run_update",
        python_callable=run_update,
    )


if __name__ == "__main__":
    run_bootstrap()
