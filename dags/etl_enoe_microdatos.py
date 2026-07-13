import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

from core.pipeline import Pipeline
from core.pipelines.enoe_microdatos.stages.extract import EnoeMicrodatosExtract
from core.pipelines.enoe_microdatos.stages.transform import EnoeMicrodatosTransform
from core.pipelines.enoe_microdatos.stages.load import EnoeMicrodatosLoad


def run_bootstrap():
    pipeline = Pipeline(
        name="enoe_microdatos",
        stages=[
            EnoeMicrodatosExtract(mode="bootstrap"),
            EnoeMicrodatosTransform(mode="bootstrap"),
            EnoeMicrodatosLoad(mode="bootstrap"),
        ],
    )
    pipeline.run(mode="bootstrap")


def run_incremental():
    pipeline = Pipeline(
        name="enoe_microdatos",
        stages=[
            EnoeMicrodatosExtract(mode="incremental"),
            EnoeMicrodatosTransform(mode="incremental"),
            EnoeMicrodatosLoad(mode="incremental"),
        ],
    )
    pipeline.run(mode="incremental")


default_args = {
    "owner": "Hector Moreno",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "etl_enoe_microdatos_bootstrap",
    default_args=default_args,
    description="ENOE Microdatos Bootstrap — SDEM+COE1+COE2 Jalisco desde 2005 T1 (On Demand)",
    start_date=datetime(year=2005, month=1, day=1),
    schedule=None,
    catchup=False,
    tags=["etl", "enoe_microdatos", "bootstrap", "on-demand", "inegi"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )

with DAG(
    "etl_enoe_microdatos_incremental",
    default_args=default_args,
    description="ENOE Microdatos Incremental — nuevo trimestre ~70 días después del cierre",
    start_date=datetime(year=2026, month=1, day=1),
    schedule="0 0 10 3,6,9,12 *",
    catchup=False,
    tags=["etl", "enoe_microdatos", "incremental", "trimestral", "inegi"],
) as dag_incremental:
    incremental_task = PythonOperator(
        task_id="run_incremental",
        python_callable=run_incremental,
    )

if __name__ == "__main__":
    run_bootstrap()
