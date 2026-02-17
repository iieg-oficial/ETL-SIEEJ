import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

from core.pipeline import Pipeline
from core.pipelines.fiscalia.stages.extract import FiscaliaExtract
from core.pipelines.fiscalia.stages.transform import FiscaliaTransform
from core.pipelines.fiscalia.stages.load import FiscaliaLoad


def run_bootstrap():
    """Executes initial load of the Fiscalía database"""
    pipeline = Pipeline(
        name='fiscalia',
        stages=[
            FiscaliaExtract(mode='bootstrap'),
            FiscaliaTransform(mode='bootstrap'),
            FiscaliaLoad(mode='bootstrap'),
        ],
    )
    pipeline.run(mode='bootstrap')


default_args_bootstrap = {
    'owner': 'José Velazco H.',
    'retries': 1,
    'retry_delay': timedelta(minutes=40),
}

with DAG(
    'etl_fiscalia_bootstrap',
    default_args=default_args_bootstrap,
    description='Fiscalia Bootstrap - Initial full load (On Demand)',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['etl', 'fiscalia', 'bootstrap', 'on-demand'],
) as dag_bootstrap:

    bootstrap_task = PythonOperator(
        task_id='run_bootstrap',
        python_callable=run_bootstrap
    )


def run_update():
    """Performs monthly update of the Prosecutor's Office"""
    pipeline = Pipeline(
        name='fiscalia',
        stages=[
            FiscaliaExtract(mode='update'),
            FiscaliaTransform(mode='update'),
            FiscaliaLoad(mode='update'),
        ],
    )
    pipeline.run(mode='update')

default_args_update = {
    'owner': 'José Velazco H.',
    'retries': 3,
    'retry_delay': timedelta(days=7),
}

with DAG(
    'etl_fiscalia_update',
    default_args=default_args_update,
    description='Fiscalia Update - Monthly incremental load',
    schedule='@monthly',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['etl', 'fiscalia', 'update', 'monthly'],
) as dag_update:

    update_task = PythonOperator(
        task_id='run_update',
        python_callable=run_update
    )


if __name__ == "__main__":
    run_bootstrap()
    run_update()
