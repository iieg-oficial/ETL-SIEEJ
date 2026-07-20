import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator


def run_bootstrap() -> None:
    from core.pipeline import Pipeline
    from core.pipelines.defunciones.stages.extract import DefuncionesExtract
    from core.pipelines.defunciones.stages.load import DefuncionesLoad
    from core.pipelines.defunciones.stages.transform import DefuncionesTransform

    pipeline = Pipeline(
        name="defunciones",
        stages=[
            DefuncionesExtract(mode="bootstrap"),
            DefuncionesTransform(mode="bootstrap"),
            DefuncionesLoad(mode="bootstrap"),
        ],
    )
    pipeline.run(mode="bootstrap")


def run_update() -> None:
    from sqlalchemy import func, select

    from core.db import Database
    from core.pipeline import Pipeline
    from core.pipelines.defunciones.config import settings
    from core.pipelines.defunciones.schemas import CatEdicion
    from core.pipelines.defunciones.stages.extract import DefuncionesExtract
    from core.pipelines.defunciones.stages.load import DefuncionesLoad
    from core.pipelines.defunciones.stages.transform import DefuncionesTransform

    db = Database(settings.DB_NAME, settings.database_url)
    db.connect()
    with db.get_session() as session:
        last_year = session.execute(select(func.max(CatEdicion.anio))).scalar()
    db.disconnect()
    since_year = last_year or settings.BACKFILL_MIN_YEAR

    pipeline = Pipeline(
        name="defunciones",
        stages=[
            DefuncionesExtract(mode="update", since_year=since_year),
            DefuncionesTransform(mode="update"),
            DefuncionesLoad(mode="update"),
        ],
    )
    pipeline.run(mode="update")


default_args_bootstrap = {
    "owner": "Jose Velazco",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

default_args_update = {
    "owner": "Jose Velazco",
    "retries": 3,
    "retry_delay": timedelta(days=2),
}

with DAG(
    "etl_defunciones_bootstrap",
    default_args=default_args_bootstrap,
    description="Defunciones Bootstrap - carga inicial de todas las ediciones (on demand)",
    start_date=datetime(year=2026, month=1, day=1),
    schedule=None,
    catchup=False,
    tags=["etl", "defunciones", "bootstrap", "on-demand"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )

with DAG(
    "etl_defunciones_update",
    default_args=default_args_update,
    description="Defunciones Update - carga anual de la ultima edicion publicada por DGIS",
    schedule="0 4 1 7 *",
    start_date=datetime(year=2026, month=7, day=1),
    catchup=False,
    tags=["etl", "defunciones", "update"],
) as dag_update:
    update_task = PythonOperator(
        task_id="run_update",
        python_callable=run_update,
    )


if __name__ == "__main__":
    run_bootstrap()
