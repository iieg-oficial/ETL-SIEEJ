---
applyTo: "**/dags/*.py,**/stages/*.py"
---

# Bootstrap & Update Instructions

> Aplican a: DEA, ETL

## Rules

- **Bootstrap**: primera ejecución del pipeline. Procesa la totalidad de los datos históricos disponibles desde la fuente. El DAG correspondiente lleva el sufijo `_bootstrap` y se ejecuta `On Demand`.
- **Update**: ejecuciones subsecuentes. Solo procesa registros nuevos o modificados desde la última ejecución exitosa. El DAG correspondiente lleva el sufijo `_update` y tiene un `schedule_interval` definido.
- Cada `Stage` debe aceptar el parámetro `mode: str` (`"bootstrap"` o `"update"`) y ramificar su lógica según corresponda.
- **Update tipo solo-inserciones**: la fuente solo agrega datos nuevos. Implementar con `INSERT ... ON CONFLICT DO NOTHING` a través de `bulk_ops.insert_records` o `bulk_ops.bulk_insert`.
- **Update tipo SCD (Slowly Changing Dimension)**: la fuente puede mezclar registros nuevos con actualizaciones a registros existentes.
  - Generar un hash de las columnas monitoreadas (todas las columnas significativas, excluir `id` y timestamps).
  - Comparar el hash con el hash almacenado en BD para detectar cambios.
  - Al detectar un cambio: marcar el registro vigente con `valid_to = fecha_actual` e `is_current = False`, insertar el nuevo registro con `valid_from = fecha_actual`, `valid_to = NULL` e `is_current = True`.
  - La vista de integración (`V4`) filtra siempre por `is_current = True`.
- Definir dos `DAG` distintos en el mismo archivo: uno para bootstrap y otro para update. Cada uno con sus propios `default_args`.
- La función `main()` al final del archivo ejecuta el modo `bootstrap` completo para pruebas locales sin Airflow.
