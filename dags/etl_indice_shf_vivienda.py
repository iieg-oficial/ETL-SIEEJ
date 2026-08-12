import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

PIPELINE_NAME = "indice_shf_vivienda"


def run(mode: str = "bootstrap") -> None:
    """Solo bootstrap: cada publicación trimestral reemite la serie completa desde 2005.

    No hay carga incremental que construir, y la URL trae el id de archivo y el
    trimestre en el nombre, así que no existe plantilla que un schedule pueda
    resolver solo. El flujo se corre a mano después de actualizar SHF_URL en el
    .env; el upsert hace que repetirlo sea inofensivo.

    Los imports viven dentro del callable a propósito: el DAG processor reparsea
    este archivo cada par de minutos y pandas y SQLAlchemy solo hacen falta
    cuando una tarea de verdad se ejecuta.
    """
    from core.pipeline import Pipeline
    from core.pipelines.indice_shf_vivienda.stages.extract import IndiceShfViviendaExtract
    from core.pipelines.indice_shf_vivienda.stages.load import IndiceShfViviendaLoad
    from core.pipelines.indice_shf_vivienda.stages.transform import IndiceShfViviendaTransform

    Pipeline(
        name=PIPELINE_NAME,
        stages=[IndiceShfViviendaExtract(), IndiceShfViviendaTransform(), IndiceShfViviendaLoad()],
    ).run(mode=mode)


def run_bootstrap() -> None:
    run(mode="bootstrap")


default_args = {
    "owner": "Alejandro Zarate",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "etl_indice_shf_vivienda_bootstrap",
    default_args=default_args,
    description="Índice SHF de Precios de la Vivienda — Carga completa 2005 a la fecha (On Demand)",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    schedule=None,
    tags=["etl", "indice_shf_vivienda", "bootstrap", "on-demand", "shf"],
) as dag_bootstrap:
    PythonOperator(task_id="run_bootstrap", python_callable=run_bootstrap)


if __name__ == "__main__":
    run_bootstrap()
