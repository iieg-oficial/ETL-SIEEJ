import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

from core.pipeline import Pipeline
from core.pipelines.centros_educativos.stages.extract import CentrosExtractor
from core.pipelines.centros_educativos.stages.transform import CentrosEducativosTransform
from core.pipelines.centros_educativos.stages.load import CentrosEducativosLoad
from core.pipelines.centros_educativos.constants import ENTIDADES_MEXICO


def run_bootstrap():
    for entidad in ENTIDADES_MEXICO:
        pipeline = Pipeline(
            name="centros_educativos",
            stages=[
                CentrosExtractor(mode="bootstrap", entidad=entidad),
                CentrosEducativosTransform(mode="bootstrap", entidad=entidad),
                CentrosEducativosLoad(mode="bootstrap", entidad=entidad),
            ],
        )
        pipeline.run(mode="bootstrap")


default_args_bootstrap = {
    "owner": "José Velazco H.",
    "retries": 1,
    "retry_delay": timedelta(minutes=15),
}

with DAG(
    "etl_centros_educativos_bootstrap",
    default_args=default_args_bootstrap,
    description="Centros Educativos Bootstrap - All entidades sequential (On Demand)",
    start_date=datetime(year=2024, month=1, day=1, hour=3),
    catchup=False,
    max_active_runs=1,
    tags=["etl", "centros_educativos", "bootstrap", "on-demand", "escuelas"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )

if __name__ == "__main__":
    run_bootstrap()
