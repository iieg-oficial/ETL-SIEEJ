import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
from core.pipeline import Pipeline
from core.pipelines.datamexico.helpers.quarters import get_start_quarter
from core.pipelines.datamexico.stages.extract import DataMexicoExtract
from core.pipelines.datamexico.stages.transform import DataMexicoTransform
from core.pipelines.datamexico.stages.load import DataMexicoLoad


def run():
    pipeline = Pipeline(
        name="datamexico",
        stages=[
            DataMexicoExtract(start_quarter=get_start_quarter()),
            DataMexicoTransform(),
            DataMexicoLoad(),
        ],
    )
    pipeline.run()


default_arg = {
    "owner": "José Velazco H.",
    "retries": 3,
    "retry_delay": timedelta(days=2),
}


with DAG(
    "etl_datamexico_update",
    default_args=default_arg,
    description="DataMexico Update - Quarterly update",
    schedule="0 8 1 */3 *",
    start_date=datetime(year=2026, month=1, day=1, hour=4),
    catchup=False,
    tags=["etl", "datamexico", "update", "bootstrap", "comercio-exterior"],
) as dag_update:
    update_task = PythonOperator(
        task_id="run",
        python_callable=run,
    )


if __name__ == "__main__":
    run()
