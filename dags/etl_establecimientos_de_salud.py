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
from core.pipelines.establecimientos_de_salud.config import settings


def run_bootstrap():
    end_year = datetime.today().year
    for year in range(settings.BOOTSTRAP_START_YEAR, end_year + 1):
        month = settings.BOOTSTRAP_START_MONTH if year == settings.BOOTSTRAP_START_YEAR else 1
        pipeline = Pipeline(
            name='establecimientos_de_salud',
            stages=[
                EstablecimientosExtract(mode='bootstrap', year=year, month=month),
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
