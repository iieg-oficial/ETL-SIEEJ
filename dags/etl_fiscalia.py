import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

from core.pipeline import Pipeline
from core.pipelines.fiscalia.stages.extract_bootstrap import FiscaliaExtractBootstrap
from core.pipelines.fiscalia.stages.transform_bootstrap import FiscaliaTransformBootstrap
from core.pipelines.fiscalia.stages.load_bootstrap import FiscaliaLoadBootstrap


def run_bootstrap():
    """Ejecuta carga inicial de Fiscalia"""
    pipeline = Pipeline(
        name='fiscalia',
        stages=[
            FiscaliaExtractBootstrap(mode='bootstrap'),
            FiscaliaTransformBootstrap(mode='bootstrap'),
            FiscaliaLoadBootstrap(mode='bootstrap')
        ],

    )
    pipeline.run(mode='bootstrap')


# ============================================================================
# DAG 1: BOOTSTRAP (Carga Inicial - On Demand)
# ============================================================================

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


if __name__ == "__main__":
    run_bootstrap()
    # run_update()
