import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from core.constants.concurrency import MAX_ACTIVE_RUNS, POOL_HEAVY, PRIORITY_HEAVY
from core.schedules import schedule_for


def run_bootstrap() -> None:
    from core.pipeline import Pipeline
    from core.pipelines.defunciones_inegi.stages.extract import DefuncionesInegiExtract
    from core.pipelines.defunciones_inegi.stages.load import DefuncionesInegiLoad
    from core.pipelines.defunciones_inegi.stages.transform import DefuncionesInegiTransform

    pipeline = Pipeline(
        name="defunciones_inegi",
        stages=[
            DefuncionesInegiExtract(mode="bootstrap"),
            DefuncionesInegiTransform(mode="bootstrap"),
            DefuncionesInegiLoad(mode="bootstrap"),
        ],
    )
    pipeline.run(mode="bootstrap")


def run_update() -> None:
    from sqlalchemy import func, select

    from core.db import Database
    from core.pipeline import Pipeline
    from core.pipelines.defunciones_inegi.config import settings
    from core.pipelines.defunciones_inegi.schemas import CatEdicion
    from core.pipelines.defunciones_inegi.stages.extract import DefuncionesInegiExtract
    from core.pipelines.defunciones_inegi.stages.load import DefuncionesInegiLoad
    from core.pipelines.defunciones_inegi.stages.transform import DefuncionesInegiTransform

    db = Database(settings.DB_NAME, settings.database_url)
    db.connect()
    with db.get_session() as session:
        last_year = session.execute(select(func.max(CatEdicion.anio))).scalar()
    db.disconnect()

    # La edición ya cargada no se vuelve a bajar: se arranca en la siguiente.
    since_year = (last_year + 1) if last_year else settings.BACKFILL_MIN_YEAR

    pipeline = Pipeline(
        name="defunciones_inegi",
        stages=[
            DefuncionesInegiExtract(mode="update", since_year=since_year),
            DefuncionesInegiTransform(mode="update"),
            DefuncionesInegiLoad(mode="update"),
        ],
    )
    pipeline.run(mode="update")


default_args_bootstrap = {
    "owner": "Jose Velazco",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "priority_weight": PRIORITY_HEAVY,
    "weight_rule": "absolute",
}

default_args_update = {
    "owner": "Jose Velazco",
    "retries": 3,
    "retry_delay": timedelta(days=2),
    "priority_weight": PRIORITY_HEAVY,
    "weight_rule": "absolute",
}

with DAG(
    "etl_defunciones_inegi_bootstrap",
    default_args=default_args_bootstrap,
    description="Defunciones INEGI Bootstrap - carga inicial de todas las ediciones EDR (on demand)",
    start_date=datetime(year=2026, month=1, day=1),
    schedule=None,
    catchup=False,
    max_active_runs=MAX_ACTIVE_RUNS,
    tags=["etl", "defunciones_inegi", "bootstrap", "on-demand"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
        pool=POOL_HEAVY,
    )

with DAG(
    "etl_defunciones_inegi_update",
    default_args=default_args_update,
    description="Defunciones INEGI Update - carga anual de la ultima edicion EDR publicada",
    schedule=schedule_for("etl_defunciones_inegi_update"),
    start_date=datetime(year=2026, month=12, day=1),
    catchup=False,
    max_active_runs=MAX_ACTIVE_RUNS,
    tags=["etl", "defunciones_inegi", "update"],
) as dag_update:
    update_task = PythonOperator(
        task_id="run_update",
        python_callable=run_update,
        pool=POOL_HEAVY,
    )


if __name__ == "__main__":
    run_bootstrap()
