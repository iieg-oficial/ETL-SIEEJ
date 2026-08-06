import importlib
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# Must run before any `airflow` or `dags.*` import.
os.environ.setdefault("AIRFLOW_HOME", str(REPO_ROOT))
os.environ.setdefault("AIRFLOW__CORE__UNIT_TEST_MODE", "True")
os.environ.setdefault("AIRFLOW__CORE__LOAD_EXAMPLES", "False")
for name, value in {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "test",
    "DB_USER": "test",
    "DB_PASSWORD": "test",
    # Required (no default) pydantic-settings fields on pipelines whose
    # config module gets imported at DAG module import time, directly or
    # transitively. Values are unused during static import — they only
    # need to satisfy required-field validation.
    "GDRIVE_CLIENT_EMAIL": "test@test.iam.gserviceaccount.com",
    "GDRIVE_PRIVATE_KEY": "test",
    "GDRIVE_FOLDER_ID": "test",
    "GDRIVE_FILE_ID": "test",
    "HISTORICAL_FILENAME": "test.csv",
    "ESTABLECIMIENTOS_URL": "https://example.test",
    "INPC_BASE_URL": "https://example.test",
    "INPC_URL_NODOS": "https://example.test",
    "URL_MUNICIPAL": "https://example.test",
    "URL_LOCALIDAD": "https://example.test",
}.items():
    os.environ.setdefault(name, value)

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture(scope="session")
def dag_files():
    return sorted((REPO_ROOT / "dags").glob("etl_*.py"))


@pytest.fixture(scope="session")
def all_dags(dag_files):
    from airflow import DAG

    dags = {}
    for path in dag_files:
        module = importlib.import_module(f"dags.{path.stem}")
        for obj in vars(module).values():
            if isinstance(obj, DAG):
                dags[obj.dag_id] = obj
    return dags
