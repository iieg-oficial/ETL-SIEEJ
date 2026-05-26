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
    """Ejecuta la carga inicial completa de EFIPEM municipal anual (Jalisco, 1989-presente)."""
    pipeline = Pipeline(
        name="efipem",
        stages=[
            EfipemExtractor(mode="bootstrap"),
            EfipemTransformer(mode="bootstrap"),
            EfipemLoader(mode="bootstrap"),
        ],
    )
    pipeline.run(mode="bootstrap")


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
    description="EFIPEM Bootstrap - Carga inicial municipal anual Jalisco (On Demand)",
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
# DAG 2: UPDATE — no implementado (dataset anual, solo bootstrap por ahora)
# ============================================================================


if __name__ == "__main__":
    run_bootstrap()
