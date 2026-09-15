"""DAG de sincronización de layers de GeoServer.

No corre por cron ni bajo demanda directa: se dispara vía TriggerDagRunOperator
desde el DAG de bootstrap/update de cada pipeline geo, una vez que terminó de
cargar/actualizar sus datos. Recibe el nombre del pipeline por `dag_run.conf`
y publica/actualiza sus vistas materializadas con geometría en GeoServer,
incluyendo la limpieza de layers huérfanas (ver scripts/create_geoserver_layers.py).
"""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from scripts.create_geoserver_layers import build_geoserver_client, process_pipeline


def run_geoserver_sync(**context) -> None:
    pipeline_name = (context["dag_run"].conf or {}).get("pipeline")
    if not pipeline_name:
        raise ValueError("Falta 'pipeline' en dag_run.conf")

    gs = build_geoserver_client()
    process_pipeline(gs, pipeline_name, dry_run=False)


default_args = {
    "owner": "Hector Moreno",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    "etl_geoserver_sync",
    default_args=default_args,
    description="Publica/actualiza layers de GeoServer para un pipeline (disparado por su bootstrap/update)",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    max_active_runs=3,
    tags=["etl", "geoserver", "on-demand"],
) as dag:
    sync_task = PythonOperator(
        task_id="sync_geoserver_layers",
        python_callable=run_geoserver_sync,
    )
