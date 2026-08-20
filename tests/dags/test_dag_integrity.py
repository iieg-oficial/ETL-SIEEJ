from pathlib import Path

from airflow.task.priority_strategy import _AbsolutePriorityWeightStrategy

from core.constants.concurrency import (
    HEAVY_PIPELINES,
    MAX_ACTIVE_RUNS,
    POOL_HEAVY,
    POOLS,
    PRIORITY_HEAVY,
)


def heavy_dag_ids():
    return {f"etl_{p}_{flow}" for p in HEAVY_PIPELINES for flow in ("bootstrap", "update")}


def test_every_dag_file_produces_at_least_one_dag(dags_by_file):  # AC7
    empty = [name for name, dags in dags_by_file.items() if not dags]
    assert not empty, f"archivos sin objetos DAG: {empty}"


def test_dag_ids_are_unique(dags_by_file):  # AC7
    ids = [dag.dag_id for dags in dags_by_file.values() for dag in dags]
    duplicates = {dag_id for dag_id in ids if ids.count(dag_id) > 1}
    assert not duplicates, f"dag_id declarado en más de un archivo: {duplicates}"


def test_every_dag_declares_max_active_runs(all_dags):  # AC1
    offenders = [d for d, dag in all_dags.items() if dag.max_active_runs != MAX_ACTIVE_RUNS]
    assert not offenders


def test_no_dag_overrides_max_active_tasks(all_dags):  # AC2
    from airflow.configuration import conf

    default = conf.getint("core", "max_active_tasks_per_dag")
    offenders = [d for d, dag in all_dags.items() if dag.max_active_tasks != default]
    assert not offenders


def test_every_pool_reference_is_provisioned(all_dags):  # AC3
    unknown = {
        t.pool for dag in all_dags.values() for t in dag.tasks if t.pool != "default_pool" and t.pool not in POOLS
    }
    assert not unknown


def test_heavy_dags_hold_the_heavy_pool(all_dags):  # AC5
    for dag_id in heavy_dag_ids():
        assert all(t.pool == POOL_HEAVY for t in all_dags[dag_id].tasks)


def test_light_tasks_outrank_heavy_tasks(all_dags):  # AC6
    heavy = heavy_dag_ids()
    light_min = min(t.priority_weight for d, dag in all_dags.items() if d not in heavy for t in dag.tasks)
    heavy_max = max(t.priority_weight for d in heavy for t in all_dags[d].tasks)
    assert heavy_max == PRIORITY_HEAVY
    assert light_min > heavy_max


def test_heavy_dags_use_absolute_weight_rule(all_dags):  # AC6
    for dag_id in heavy_dag_ids():
        offenders = [
            t.task_id for t in all_dags[dag_id].tasks if not isinstance(t.weight_rule, _AbsolutePriorityWeightStrategy)
        ]
        assert not offenders, f"{dag_id}: tasks without weight_rule='absolute': {offenders}"


def test_pool_names_are_defined_once():  # AC4
    redefinitions = [
        p
        for p in (Path(__file__).resolve().parents[2] / "core" / "pipelines").rglob("constants.py")
        if POOL_HEAVY in p.read_text() or "_POOL" in p.read_text()
    ]
    assert not redefinitions
