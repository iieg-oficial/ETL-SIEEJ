# dags/etl_repd.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

from core.pipeline import Pipeline

from core.pipelines.repd.stages.extract import REPDExtractor
from core.pipelines.repd.stages.transform import REPDTransformer
from core.pipelines.repd.stages.load import REPDLoader

def run_bootstrap():
    """Ejecuta carga inicial de REPD"""
    pipeline = Pipeline(
        name='repd',
        stages=[
            REPDExtractor(mode='bootstrap'),
            REPDTransformer(mode='bootstrap'),
            REPDLoader(mode='bootstrap')
        ],
        
    )
    pipeline.run(mode='bootstrap')


def run_update():
    """Ejecuta carga incremental de REPD"""
    pipeline = Pipeline(
        name='repd',
        stages=[
            REPDExtractor(mode='update'),
            REPDTransformer(mode='update'),
            REPDLoader(mode='update')
        ],
        
    )
    pipeline.run(mode='update')


# ============================================================================
# DAG 1: BOOTSTRAP (Carga Inicial - On Demand)
# ============================================================================

default_args_bootstrap = {
    'owner': 'Alejandro Zarate',
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}

with DAG(
    'etl_repd_bootstrap',
    default_args=default_args_bootstrap,
    description='REPD Bootstrap - Initial full load (On Demand)',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['etl', 'repd', 'bootstrap', 'on-demand'],
) as dag_bootstrap:
    
    bootstrap_task = PythonOperator(
        task_id='run_bootstrap',
        python_callable=run_bootstrap
    )


# ============================================================================
# DAG 2: UPDATE (Carga Incremental - Mensual)
# ============================================================================

default_args_update = {
    'owner': 'Alejandro Zarate',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'etl_repd_update',
    default_args=default_args_update,
    description='REPD Update - Incremental monthly load',
    schedule='0 2 1 * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['etl', 'repd', 'update', 'monthly'],
) as dag_update:
    
    update_task = PythonOperator(
        task_id='run_update',
        python_callable=run_update
    )
    
    
if __name__ == "__main__":
    run_bootstrap()
    # run_update()
    