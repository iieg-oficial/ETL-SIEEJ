import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from core.pipeline import Pipeline
from core.pipelines.censos_economicos.stages.extract import CensosEconomicosExtractor
from core.pipelines.censos_economicos.stages.load import CensosEconomicosLoader
from core.pipelines.censos_economicos.stages.transform import CensosEconomicosTransformer


def run_bootstrap() -> None:
    """Run full bootstrap load of Censos Economicos (CE 2019 + CE 2024)."""
    pipeline = Pipeline(
        name="censos_economicos",
        stages=[
            CensosEconomicosExtractor(mode="bootstrap"),
            CensosEconomicosTransformer(mode="bootstrap"),
            CensosEconomicosLoader(mode="bootstrap"),
        ],
    )
    pipeline.run(mode="bootstrap")


default_args_bootstrap = {
    "owner": "Alejandro Zarate",
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    "etl_censos_economicos_bootstrap",
    default_args=default_args_bootstrap,
    description="Censos Economicos Bootstrap - carga unica (On Demand)",
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["etl", "censos_economicos", "bootstrap", "on-demand", "inegi"],
) as dag_bootstrap:
    bootstrap_task = PythonOperator(
        task_id="run_bootstrap",
        python_callable=run_bootstrap,
    )


if __name__ == "__main__":
    run_bootstrap()
