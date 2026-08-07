import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

from core.pipeline import Pipeline
from core.pipelines.intensidad_migratoria.stages.extract import IntensidadMigratoriaExtract
from core.pipelines.intensidad_migratoria.stages.transform import IntensidadMigratoriaTransform
from core.pipelines.intensidad_migratoria.stages.load import IntensidadMigratoriaLoad


def run_bootstrap():
    pipeline = Pipeline(
        name="intensidad_migratoria",
        stages=[
            IntensidadMigratoriaExtract(),
            IntensidadMigratoriaTransform(),
            IntensidadMigratoriaLoad(),
        ],
    )
    pipeline.run(mode="bootstrap")


default_args = {
    "owner": "José Velazco H.",
    "retries": 3,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    "etl_intensidad_migratoria_bootstrap",
    default_args=default_args,
    description="Intensidad Migratoria Bootstrap - CONAPO 2010 y 2020 (On Demand)",
    start_date=datetime(year=2024, month=1, day=1),
    catchup=False,
    max_active_runs=1,
    tags=["etl", "intensidad_migratoria", "bootstrap", "on-demand", "conapo"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )

if __name__ == "__main__":
    run_bootstrap()
