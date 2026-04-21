import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from core.pipeline import Pipeline
from core.pipelines.asg_imms.stages.extract import AsgImmsExtractor
from core.pipelines.asg_imms.stages.load import AsgImmsLoader
from core.pipelines.asg_imms.stages.transform import AsgImmsTransformer


def run_bootstrap():
    """Ejecuta la carga inicial completa de asg_imms (desde 2015-01-31)"""
    Pipeline(
        name="asg_imms",
        stages=[
            AsgImmsExtractor(mode="bootstrap"),
            AsgImmsTransformer(mode="bootstrap"),
            AsgImmsLoader(mode="bootstrap"),
        ],
    ).run(mode="bootstrap")


def run_update():
    """Ejecuta carga incremental de asg_imms (mes anterior)"""
    Pipeline(
        name="asg_imms",
        stages=[
            AsgImmsExtractor(mode="update"),
            AsgImmsTransformer(mode="update"),
            AsgImmsLoader(mode="update"),
        ],
    ).run(mode="update")


# ============================================================================
# DAG 1: BOOTSTRAP (Carga inicial — Bajo demanda)
# ============================================================================

with DAG(
    "etl_asg_imms_bootstrap",
    default_args={
        "owner": "iieg",
        "retries": 1,
        "retry_delay": timedelta(minutes=10),
    },
    description="ASG IMSS Bootstrap — Carga inicial completa desde 2015 (On Demand)",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    schedule=None,
    tags=["etl", "asg_imms", "bootstrap", "on-demand"],
) as dag_bootstrap:
    PythonOperator(task_id="run_bootstrap", python_callable=run_bootstrap)


# ============================================================================
# DAG 2: UPDATE (Carga incremental — Mensual)
# ============================================================================

with DAG(
    "etl_asg_imms_update",
    default_args={
        "owner": "Alejandro Zarate Macias",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    description="ASG IMSS Update — Carga incremental mensual (mes anterior)",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    schedule="0 6 1 * *",
    tags=["etl", "asg_imms", "update"],
) as dag_update:
    PythonOperator(task_id="run_update", python_callable=run_update)


if __name__ == "__main__":
    run_bootstrap()
