"""On-demand DAG for the productive Pendientes raster pipeline."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator


def run_bootstrap() -> None:
    """Run exactly Extract, Transform and Load; experimental phases are not DAG stages."""
    from core.pipeline import Pipeline
    from core.pipelines.pendientes.constants import PIPELINE_NAME
    from core.pipelines.pendientes.stages.extract import PendientesExtract
    from core.pipelines.pendientes.stages.load import PendientesLoad
    from core.pipelines.pendientes.stages.transform import PendientesTransform

    Pipeline(
        name=PIPELINE_NAME,
        stages=[PendientesExtract(), PendientesTransform(), PendientesLoad()],
    ).run(mode="bootstrap")


def main() -> None:
    run_bootstrap()


def run_extract() -> None:
    from core.pipelines.pendientes.stages.extract import PendientesExtract

    PendientesExtract().execute()


def run_transform() -> None:
    from core.pipelines.pendientes.stages.transform import PendientesTransform

    PendientesTransform().execute()


def run_load() -> None:
    from core.pipelines.pendientes.stages.load import PendientesLoad

    PendientesLoad().execute()


default_args = {
    "owner": "Gerardo Rubalcava",
    "retries": 1,
    "retry_delay": timedelta(minutes=20),
}

with DAG(
    "etl_pendientes_bootstrap",
    default_args=default_args,
    description="Pendientes: CEM 4.0, COG locales y estadisticas municipales (bajo demanda)",
    start_date=datetime(year=2026, month=1, day=1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    tags=["etl", "pendientes", "raster", "bootstrap", "on-demand"],
) as dag:
    extract_task = PythonOperator(task_id="extract", python_callable=run_extract)
    transform_task = PythonOperator(task_id="transform", python_callable=run_transform)
    load_task = PythonOperator(task_id="load", python_callable=run_load)

    extract_task >> transform_task >> load_task


if __name__ == "__main__":
    main()
