"""DAGs Airflow del pipeline asg_imss.

Define dos DAGs por flujo:

  * `etl_asg_imss_bootstrap` — schedule=None (carga inicial bajo demanda):
      task `bootstrap_catalogos` → `bootstrap_datos`.
  * `etl_asg_imss_update` — cron `"0 12 10 * *"` (día 10 de cada mes 12:00):
      task `update_catalogos` → `update_datos`.

Para el flujo de datos se itera mes a mes (último día de mes). Si un mes
falla, se loggea ERROR y se continúa con el siguiente; el DAG no aborta.
"""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from core.pipeline import Pipeline
from core.pipelines.asg_imss.stages.extract import (
    AsgImssCatalogExtractor,
    AsgImssDataExtractor,
    compute_target_dates,
)
from core.pipelines.asg_imss.stages.load import (
    AsgImssCatalogLoader,
    AsgImssDataLoader,
)
from core.pipelines.asg_imss.stages.transform import (
    AsgImssCatalogTransformer,
    AsgImssDataTransformer,
)
from core.schedules import schedule_for
from core.utils.logger import get_logger


_LOGGER = get_logger("asg_imss.dag")


def _run_catalogos(mode: str) -> None:
    """Descarga el XLSX, parsea y carga los 12 catálogos."""
    pipeline = Pipeline(
        name="asg_imss",
        stages=[
            AsgImssCatalogExtractor(mode=mode),
            AsgImssCatalogTransformer(mode=mode),
            AsgImssCatalogLoader(mode=mode),
        ],
    )
    pipeline.run(mode=mode)


def _run_datos(mode: str) -> None:
    """Itera por mes y carga CSV → stg_asg_imss. Continúa ante errores por mes."""
    dates = compute_target_dates(mode)
    _LOGGER.info(f"asg_imss datos {mode}: {len(dates)} fecha(s) — {dates[:3]}…{dates[-1:]}")

    extractor = AsgImssDataExtractor(mode=mode)
    transformer = AsgImssDataTransformer(mode=mode)
    loader = AsgImssDataLoader(mode=mode)
    loader.setup()

    results: dict[str, int] = {"ok": 0, "fail": 0, "rows": 0}
    try:
        for target_date in dates:
            try:
                ext = extractor.execute({"target_date": target_date})
                tr = transformer.execute(ext)
                ld = loader.execute(tr)
                results["ok"] += 1
                results["rows"] += int(ld.get("rows_inserted", 0))
            except Exception as exc:
                results["fail"] += 1
                _LOGGER.error(f"❌ Mes {target_date} falló: {exc}", exc_info=True)
                continue
    finally:
        loader.teardown()

    _LOGGER.info(
        f"asg_imss datos {mode} resumen: ok={results['ok']} fail={results['fail']} filas_insertadas={results['rows']:,}"
    )


def run_bootstrap_catalogos() -> None:
    _run_catalogos(mode="bootstrap")


def run_bootstrap_datos() -> None:
    _run_datos(mode="bootstrap")


def run_update_catalogos() -> None:
    _run_catalogos(mode="update")


def run_update_datos() -> None:
    _run_datos(mode="update")


# ============================================================================
# DAG 1: BOOTSTRAP (carga inicial bajo demanda)
# ============================================================================

default_args_bootstrap = {
    "owner": "Alejandro Zarate",
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    "etl_asg_imss_bootstrap",
    default_args=default_args_bootstrap,
    description="ASG IMSS Bootstrap - Catálogos XLSX + datos CSV mensuales (On Demand)",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    schedule=None,
    tags=["etl", "asg_imss", "bootstrap", "on-demand", "imss", "empleo"],
) as dag_bootstrap:
    task_bootstrap_catalogos = PythonOperator(
        task_id="bootstrap_catalogos",
        python_callable=run_bootstrap_catalogos,
    )
    task_bootstrap_datos = PythonOperator(
        task_id="bootstrap_datos",
        python_callable=run_bootstrap_datos,
    )
    task_bootstrap_catalogos >> task_bootstrap_datos


# ============================================================================
# DAG 2: UPDATE (mensual — día 10 de cada mes a las 12:00)
# ============================================================================

default_args_update = {
    "owner": "Alejandro Zarate",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "etl_asg_imss_update",
    default_args=default_args_update,
    description="ASG IMSS Update - Re-sincroniza catálogos y carga el mes cerrado anterior",
    schedule=schedule_for("etl_asg_imss_update"),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["etl", "asg_imss", "update", "monthly", "imss", "empleo"],
) as dag_update:
    task_update_catalogos = PythonOperator(
        task_id="update_catalogos",
        python_callable=run_update_catalogos,
    )
    task_update_datos = PythonOperator(
        task_id="update_datos",
        python_callable=run_update_datos,
    )
    task_update_catalogos >> task_update_datos


if __name__ == "__main__":
    run_bootstrap_catalogos()
    run_bootstrap_datos()
