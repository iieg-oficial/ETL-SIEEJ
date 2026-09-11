import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from core.constants.concurrency import MAX_ACTIVE_RUNS, POOL_HEAVY, PRIORITY_HEAVY
from core.schedules import schedule_for


def run_extract(year: int):
    from core.pipelines.nacimientos_dgis.stages.extract import NacimientosDgisExtract

    NacimientosDgisExtract(year=year).execute()


def run_transform():
    from core.pipelines.nacimientos_dgis.stages.transform import NacimientosDgisTransform

    NacimientosDgisTransform().execute()


def run_load(mode: str):
    from core.pipelines.nacimientos_dgis.stages.load import NacimientosDgisLoad

    NacimientosDgisLoad(mode=mode).execute()


def get_years(start_year: int):
    from datetime import date

    return list(range(start_year, date.today().year + 1))


def get_update_years():
    from core.db import Database
    from core.pipelines.nacimientos_dgis.config import settings
    from core.pipelines.nacimientos_dgis.schemas import StgNacimientosEdadMadre
    from core.utils.bulk_ops import get_last_update

    db = Database(settings.DB_NAME, settings.database_url)
    db.connect()
    try:
        with db.get_session() as session:
            last_year = get_last_update(session, StgNacimientosEdadMadre, StgNacimientosEdadMadre.anio.key)
    finally:
        db.disconnect()

    if not last_year:
        return []

    return get_years(last_year + 1)


def run_bootstrap():
    from core.pipelines.nacimientos_dgis.config import settings

    for year in get_years(settings.START_YEAR):
        run_extract(year)
    run_transform()
    run_load("bootstrap")


def run_update():
    years = get_update_years()
    if not years:
        return
    for year in years:
        run_extract(year)
    run_transform()
    run_load("update")


def build_dag(dag_id, mode, description, schedule, tags):
    from core.pipelines.nacimientos_dgis.config import settings

    years = get_years(settings.START_YEAR)

    with DAG(
        dag_id,
        default_args={
            "owner": "Jose Velazco H.",
            "retries": 3,
            "retry_delay": timedelta(minutes=1),
            "priority_weight": PRIORITY_HEAVY,
            "weight_rule": "absolute",
        },
        description=description,
        start_date=datetime(year=2024, month=1, day=1),
        catchup=False,
        schedule=schedule,
        max_active_runs=MAX_ACTIVE_RUNS,
        tags=tags,
    ) as dag:
        extract_tasks = []

        for year in years:
            extract = PythonOperator(
                task_id=f"extract_{year}",
                python_callable=run_extract,
                op_kwargs={"year": year},
                pool=POOL_HEAVY,
            )
            extract_tasks.append(extract)

        transform_task = PythonOperator(
            task_id="transform",
            python_callable=run_transform,
            pool=POOL_HEAVY,
        )

        load_task = PythonOperator(
            task_id="load",
            python_callable=run_load,
            op_kwargs={"mode": mode},
            pool=POOL_HEAVY,
        )

        extract_tasks >> transform_task >> load_task

    return dag


dag_bootstrap = build_dag(
    dag_id="etl_nacimientos_dgis_bootstrap",
    mode="bootstrap",
    description="Nacimientos DGIS Bootstrap - On Demand",
    schedule=None,
    tags=["etl", "nacimientos_dgis", "bootstrap", "on-demand", "demografía"],
)

dag_update = build_dag(
    dag_id="etl_nacimientos_dgis_update",
    mode="update",
    description="Nacimientos DGIS Update - Yearly",
    schedule=schedule_for("etl_nacimientos_dgis_update"),
    tags=["etl", "nacimientos_dgis", "update", "yearly", "demografía"],
)

if __name__ == "__main__":
    run_bootstrap()
