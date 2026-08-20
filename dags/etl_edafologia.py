"""Airflow DAG for the Edafologia Serie III on-demand bootstrap pipeline."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator


def run_bootstrap() -> None:
    """Run the complete Edafologia bootstrap flow from source acquisition to municipal fragments."""
    from core.pipeline import Pipeline
    from core.pipelines.edafologia.constants import BOOTSTRAP_MODE, PIPELINE_NAME
    from core.pipelines.edafologia.stages.extract import EdafologiaExtract
    from core.pipelines.edafologia.stages.load import EdafologiaLoad
    from core.pipelines.edafologia.stages.transform import EdafologiaTransform

    pipeline = Pipeline(
        name=PIPELINE_NAME,
        stages=[
            EdafologiaExtract(mode=BOOTSTRAP_MODE),
            EdafologiaTransform(mode=BOOTSTRAP_MODE),
            EdafologiaLoad(mode=BOOTSTRAP_MODE),
        ],
    )
    pipeline.run(mode=BOOTSTRAP_MODE)


def main() -> None:
    """Run the local bootstrap entrypoint without starting an Airflow scheduler."""
    run_bootstrap()


default_args_bootstrap = {
    "owner": "Gerardo Rubalcava",
    "retries": 2,
    "retry_delay": timedelta(minutes=20),
}

with DAG(
    "etl_edafologia_bootstrap",
    default_args=default_args_bootstrap,
    description=("Edafologia Bootstrap - INEGI Serie III canonical load and IIEG/INEGI municipal overlay (on demand)"),
    start_date=datetime(year=2026, month=1, day=1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    tags=["etl", "edafologia", "geografico", "bootstrap", "on-demand"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )


if __name__ == "__main__":
    main()
