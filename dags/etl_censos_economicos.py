import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from core.pipeline import Pipeline
from core.pipelines.censos_economicos.constants import ENTITY_CHUNK_SIZE, INEGI_STATE_SLUGS
from core.pipelines.censos_economicos.stages.extract import CensosEconomicosExtractor
from core.pipelines.censos_economicos.stages.load import CensosEconomicosLoader
from core.pipelines.censos_economicos.stages.transform import CensosEconomicosTransformer


def run_bootstrap() -> None:
    """Run full bootstrap load of Censos Economicos (CE 2019 + CE 2024).

    Processes slugs in batches of ENTITY_CHUNK_SIZE to limit peak memory usage.
    Each batch runs the full extract → transform → load cycle before moving on.
    """
    all_slugs = list(INEGI_STATE_SLUGS.values())
    batches = [all_slugs[i : i + ENTITY_CHUNK_SIZE] for i in range(0, len(all_slugs), ENTITY_CHUNK_SIZE)]
    total = len(batches)

    for batch_num, slug_batch in enumerate(batches, 1):
        is_last = batch_num == total
        pipeline = Pipeline(
            name=f"censos_economicos_batch_{batch_num}of{total}",
            stages=[
                CensosEconomicosExtractor(mode="bootstrap", slugs=slug_batch),
                CensosEconomicosTransformer(mode="bootstrap"),
                CensosEconomicosLoader(mode="bootstrap", skip_cleanup=not is_last),
            ],
        )
        pipeline.run(mode="bootstrap")


default_args_bootstrap = {
    "owner": "José Velazco H.",
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    "etl_censos_economicos_bootstrap",
    default_args=default_args_bootstrap,
    description="Censos Economicos Bootstrap - carga unica (On Demand)",
    schedule=None,
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
