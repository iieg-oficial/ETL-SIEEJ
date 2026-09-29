import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from core.constants.concurrency import MAX_ACTIVE_RUNS
from core.schedules import schedule_for


def get_last_cutoff():
    from core.db import Database
    from core.pipelines.fosas_clandestinas.config import settings
    from core.pipelines.fosas_clandestinas.schemas import CatPublicaciones
    from core.utils.bulk_ops import get_last_update

    db = Database(settings.DB_NAME, settings.database_url)
    db.connect()
    try:
        with db.get_session() as session:
            return get_last_update(session, CatPublicaciones, CatPublicaciones.fecha_corte.key)
    finally:
        db.disconnect()


def run_extract(mode: str):
    from core.pipelines.fosas_clandestinas.stages.extract import FosasClandestinasExtract

    since = get_last_cutoff() if mode == "update" else None
    FosasClandestinasExtract(since=since).execute()


def run_transform():
    from core.pipelines.fosas_clandestinas.stages.transform import FosasClandestinasTransform

    FosasClandestinasTransform().execute()


def run_load(mode: str):
    from core.pipelines.fosas_clandestinas.stages.load import FosasClandestinasLoad

    FosasClandestinasLoad(mode=mode).execute()


def run_bootstrap():
    run_extract("bootstrap")
    run_transform()
    run_load("bootstrap")


def run_update():
    run_extract("update")
    run_transform()
    run_load("update")


def build_dag(dag_id, mode, description, schedule, tags):
    with DAG(
        dag_id,
        default_args={
            "owner": "Jose Velazco H.",
            "retries": 3,
            "retry_delay": timedelta(minutes=1),
        },
        description=description,
        start_date=datetime(year=2024, month=1, day=1),
        catchup=False,
        schedule=schedule,
        max_active_runs=MAX_ACTIVE_RUNS,
        tags=tags,
    ) as dag:
        extract_task = PythonOperator(
            task_id="extract",
            python_callable=run_extract,
            op_kwargs={"mode": mode},
        )

        transform_task = PythonOperator(
            task_id="transform",
            python_callable=run_transform,
        )

        load_task = PythonOperator(
            task_id="load",
            python_callable=run_load,
            op_kwargs={"mode": mode},
        )

        extract_task >> transform_task >> load_task

    return dag


dag_bootstrap = build_dag(
    dag_id="etl_fosas_clandestinas_bootstrap",
    mode="bootstrap",
    description="Fosas Clandestinas Bootstrap - On Demand",
    schedule=None,
    tags=["etl", "fosas_clandestinas", "bootstrap", "on-demand", "seguridad"],
)

dag_update = build_dag(
    dag_id="etl_fosas_clandestinas_update",
    mode="update",
    description="Fosas Clandestinas Update - Monthly",
    schedule=schedule_for("etl_fosas_clandestinas_update"),
    tags=["etl", "fosas_clandestinas", "update", "monthly", "seguridad"],
)

if __name__ == "__main__":
    run_bootstrap()
