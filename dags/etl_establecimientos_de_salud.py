import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

from core.pipeline import Pipeline
from core.pipelines.establecimientos_de_salud.stages.extract import EstablecimientosExtract
from core.pipelines.establecimientos_de_salud.stages.transform import EstablecimientosTransform
from core.pipelines.establecimientos_de_salud.stages.load import EstablecimientosLoad


def run_bootstrap():
    pipeline = Pipeline(
        name='establecimientos_de_salud',
        stages=[
            EstablecimientosExtract(mode='bootstrap'),
            EstablecimientosTransform(mode='bootstrap'),
            EstablecimientosLoad(mode='bootstrap'),
        ],
    )
    pipeline.run(mode='bootstrap')


default_args_bootstrap = {
    'owner': 'José Velazco H.',
    'retries': 1,
    'retry_delay': timedelta(minutes=40),
}

with DAG(
    'etl_establecimientos_de_salud_bootstrap',
    default_args=default_args_bootstrap,
    description='Establecimientos de Salud Bootstrap - Initial full load (On Demand)',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['etl', 'establecimientos_de_salud', 'bootstrap', 'on-demand'],
) as dag_bootstrap:

    bootstrap_task = PythonOperator(
        task_id='run_bootstrap',
        python_callable=run_bootstrap,
    )


if __name__ == "__main__":
    run_bootstrap()
