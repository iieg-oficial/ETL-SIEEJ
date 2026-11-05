import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

PIPELINE_NAME = "{{cookiecutter.pipeline}}"


def run_bootstrap() -> None:
    from core.pipeline import Pipeline
    from core.pipelines.{{cookiecutter.pipeline}}.stages.extract import {{cookiecutter.__class_prefix}}Extract
    from core.pipelines.{{cookiecutter.pipeline}}.stages.load import {{cookiecutter.__class_prefix}}Load
    from core.pipelines.{{cookiecutter.pipeline}}.stages.transform import {{cookiecutter.__class_prefix}}Transform

    Pipeline(
        name=PIPELINE_NAME,
        stages=[{{cookiecutter.__class_prefix}}Extract(), {{cookiecutter.__class_prefix}}Transform(), {{cookiecutter.__class_prefix}}Load()],
    ).run(mode="bootstrap")


default_args = {
    "owner": "{{cookiecutter.owner}}",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "etl_{{cookiecutter.pipeline}}_bootstrap",
    default_args=default_args,
    description="{{cookiecutter.pipeline}} Bootstrap (On Demand)",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    schedule=None,
    tags=["etl", "{{cookiecutter.pipeline}}", "bootstrap", "on-demand"],
) as dag_bootstrap:
    PythonOperator(task_id="run_bootstrap", python_callable=run_bootstrap)


if __name__ == "__main__":
    run_bootstrap()
