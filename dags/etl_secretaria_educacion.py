import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from core.constants.concurrency import MAX_ACTIVE_RUNS
from core.schedules import schedule_for

# Los stages se importan dentro de cada tarea: Airflow reparsea este archivo cada
# pocos segundos y un import de nivel módulo arrastraría pandas, boto3 y el
# Settings del pipeline en cada pasada.


def get_watermark():
    """Último envío procesado y etags ya cargados, para no repetir trabajo.

    Vive en el DAG y no en el stage porque el extract no necesita base de datos:
    solo el corte contra el que filtrar.
    """
    from core.db import Database
    from core.pipelines.secretaria_educacion.config import settings
    from core.pipelines.secretaria_educacion.schemas import CargasAcervo
    from core.utils.bulk_ops import get_last_update

    db = Database(settings.PIPELINE_NAME, settings.database_url)
    db.connect()
    try:
        with db.get_session() as session:
            since = get_last_update(session, CargasAcervo, CargasAcervo.actualizado_en.key)
            etags = [row[0] for row in session.query(CargasAcervo.etag).all() if row[0]]
    finally:
        db.disconnect()

    return (str(since) if since else None), etags


def run_extract(mode: str):
    from core.pipelines.secretaria_educacion.stages.extract import SecretariaEducacionExtract

    since, etags = get_watermark() if mode == "update" else (None, ())
    SecretariaEducacionExtract(mode=mode, since=since, processed_etags=etags).execute()


def run_transform(mode: str):
    from core.pipelines.secretaria_educacion.stages.transform import SecretariaEducacionTransform

    SecretariaEducacionTransform(mode=mode).execute()


def run_load(mode: str):
    from core.pipelines.secretaria_educacion.stages.load import SecretariaEducacionLoad

    SecretariaEducacionLoad(mode=mode).execute()


def run_bootstrap():
    run_extract("bootstrap")
    run_transform("bootstrap")
    run_load("bootstrap")


def run_update():
    run_extract("update")
    run_transform("update")
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
        start_date=datetime(year=2026, month=1, day=1),
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
            op_kwargs={"mode": mode},
        )

        load_task = PythonOperator(
            task_id="load",
            python_callable=run_load,
            op_kwargs={"mode": mode},
        )

        # Cada stage lee de disco lo que dejó el anterior, así que se puede
        # reintentar una sola tarea sin repetir las previas.
        extract_task >> transform_task >> load_task

    return dag


dag_bootstrap = build_dag(
    dag_id="etl_secretaria_educacion_bootstrap",
    mode="bootstrap",
    description="Secretaría de Educación Bootstrap - On Demand",
    schedule=None,
    tags=["etl", "secretaria_educacion", "bootstrap", "on-demand", "educación"],
)

dag_update = build_dag(
    dag_id="etl_secretaria_educacion_update",
    mode="update",
    description="Secretaría de Educación Update - Biweekly",
    schedule=schedule_for("etl_secretaria_educacion_update"),
    tags=["etl", "secretaria_educacion", "update", "biweekly", "educación"],
)

if __name__ == "__main__":
    run_bootstrap()
# run_update()
