from typing import Final

# Self-overlap policy. Declared per DAG as a literal; this constant is the
# policy of record that tests assert against. See docs/airflow.md.
MAX_ACTIVE_RUNS: Final[int] = 1

# Single cross-DAG semaphore. One slot means at most one heavy task runs
# anywhere in the cluster at a time, leaving the second parallelism slot
# free for light pipelines.
POOL_HEAVY: Final[str] = "heavy_pipeline"

# Source of truth for `just airflow-pools`, for the DAGs and for the tests.
# Shape matches the `airflow pools import` JSON contract exactly.
POOLS: Final[dict[str, dict[str, object]]] = {
    POOL_HEAVY: {
        "slots": 1,
        "description": "Serializes heavy pipelines across DAGs. See docs/airflow.md.",
    },
}

# Airflow's implicit default is 1. Heavy tasks go below it so that light work
# drains first when a parallelism slot frees up. Light DAGs declare nothing.
PRIORITY_LIGHT_DEFAULT: Final[int] = 1
PRIORITY_HEAVY: Final[int] = -10

# Classification per the criterion in docs/airflow.md. Adding a pipeline here
# is a reviewable decision, not a config tweak.
HEAVY_PIPELINES: Final[frozenset[str]] = frozenset({"defunciones_inegi", "denue", "nacimientos_dgis"})
