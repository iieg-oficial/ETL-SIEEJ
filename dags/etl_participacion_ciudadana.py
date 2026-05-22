import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from core.pipeline import Pipeline
from core.pipelines.participacion_ciudadana.stages.extract import ParticipacionCiudadanaExtract
from core.pipelines.participacion_ciudadana.stages.transform import ParticipacionCiudadanaTransform
from core.pipelines.participacion_ciudadana.stages.load import ParticipacionCiudadanaLoad


def run_bootstrap():
    pipeline = Pipeline(
        name="participacion_ciudadana",
        stages=[
            ParticipacionCiudadanaExtract(),
            ParticipacionCiudadanaTransform(),
            ParticipacionCiudadanaLoad(),
        ],
    )
    pipeline.run(mode="bootstrap")


default_args = {
    "owner": "Jose Velazco H.",
    "retries": 3,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    "etl_participacion_ciudadana_bootstrap",
    default_args=default_args,
    description="Participacion Ciudadana Bootstrap (On Demand)",
    start_date=datetime(year=2024, month=1, day=1),
    schedule=None,
    catchup=False,
    tags=["etl", "participacion_ciudadana", "bootstrap", "on-demand"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )

if __name__ == "__main__":
    run_bootstrap()
