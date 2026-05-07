---
applyTo: "**/dags/*.py,**/stages/*.py"
---

# Bootstrap & Update Instructions

> Applies to: DEA and ETL work on DAG and stage files

## Rules

- **Bootstrap**: the first pipeline execution. It processes the full historical dataset available from the source. The corresponding DAG uses the `_bootstrap` suffix and runs on demand.
- **Update**: subsequent executions. It processes only new or changed records since the last successful run. The corresponding DAG uses the `_update` suffix and has a defined `schedule_interval`.
- Every `Stage` must accept `mode: str` with `"bootstrap"` or `"update"` and branch its logic accordingly.
- **Append-only update**: when the source only adds new rows, implement it with `INSERT ... ON CONFLICT DO NOTHING` through `bulk_ops.insert_records` or `bulk_ops.bulk_insert`.
- **SCD update**: when the source can contain both new rows and updates to existing rows:
  - Generate a hash for the monitored columns, excluding `id` and timestamps.
  - Compare the incoming hash with the stored database hash to detect changes.
  - When a change is detected, close the current row with `valid_to = current_date` and `is_current = False`, then insert the new row with `valid_from = current_date`, `valid_to = NULL`, and `is_current = True`.
  - The integration view (`V4`) must always filter on `is_current = True`.
- Define two DAGs in the same file: one for bootstrap and one for update. Each DAG must have its own `default_args`.
- The `main()` function at the end of the file must execute the full bootstrap flow for local testing without Airflow.
