import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from core.constants.concurrency import MAX_ACTIVE_RUNS, POOL_HEAVY, PRIORITY_HEAVY
from core.pipelines.denue.constants import ENTIDADES
from core.schedules import schedule_for


def run_extract(mode: str, entidad: int):
    from core.pipelines.denue.stages.extract import DenueExtract

    DenueExtract(mode=mode, entidad=entidad).execute()


def run_transform(mode: str, entidad: int):
    from core.pipelines.denue.stages.transform import DenueTransform

    DenueTransform(mode=mode, entidad=entidad).execute()


def run_load(mode: str, entidad: int):
    from core.pipelines.denue.stages.load import DenueLoad

    DenueLoad(mode=mode, entidad=entidad).execute()


def cleanup():
    from core.utils.files import cleanup_pipeline_data

    cleanup_pipeline_data("denue")


def run_bootstrap():
    from core.pipelines.denue.constants import ENTIDADES_MEXICO

    for entidad in ENTIDADES_MEXICO:
        run_extract("bootstrap", entidad)
        run_transform("bootstrap", entidad)
        run_load("bootstrap", entidad)
    cleanup()


def run_update():
    from core.pipelines.denue.constants import ENTIDADES_MEXICO

    for entidad in ENTIDADES_MEXICO:
        run_extract("update", entidad)
        run_transform("update", entidad)
        run_load("update", entidad)
    cleanup()


def build_dag(dag_id, mode, description, schedule, tags):
    with DAG(
        dag_id,
        default_args={
            "owner": "José Velazco H.",
            "retries": 3,
            "retry_delay": timedelta(days=10),
            "priority_weight": PRIORITY_HEAVY,
            "weight_rule": "absolute",
        },
        description=description,
        start_date=datetime(year=2025, month=1, day=20),
        schedule=schedule,
        catchup=False,
        max_active_runs=MAX_ACTIVE_RUNS,
        tags=tags,
    ) as dag:
        load_tasks = []

        for entidad in ENTIDADES:
            extract = PythonOperator(
                task_id=f"extract_{entidad}",
                python_callable=run_extract,
                op_kwargs={"mode": mode, "entidad": entidad},
                pool=POOL_HEAVY,
            )

            transform = PythonOperator(
                task_id=f"transform_{entidad}",
                python_callable=run_transform,
                op_kwargs={"mode": mode, "entidad": entidad},
                pool=POOL_HEAVY,
            )

            load = PythonOperator(
                task_id=f"load_{entidad}",
                python_callable=run_load,
                op_kwargs={"mode": mode, "entidad": entidad},
                pool=POOL_HEAVY,
            )

            extract >> transform >> load
            load_tasks.append(load)

        cleanup_task = PythonOperator(
            task_id="cleanup",
            python_callable=cleanup,
            trigger_rule="all_done",
            pool=POOL_HEAVY,
        )

        load_tasks >> cleanup_task

    return dag


dag_bootstrap = build_dag(
    dag_id="etl_denue_bootstrap",
    mode="bootstrap",
    description="DENUE Bootstrap - All entidades (On Demand)",
    schedule=None,
    tags=["etl", "denue", "bootstrap", "on-demand", "inegi"],
)

dag_update = build_dag(
    dag_id="etl_denue_update",
    mode="update",
    description="DENUE Update - All entidades",
    schedule=schedule_for("etl_denue_update"),
    tags=["etl", "denue", "update", "inegi"],
)

if __name__ == "__main__":
    run_bootstrap()
