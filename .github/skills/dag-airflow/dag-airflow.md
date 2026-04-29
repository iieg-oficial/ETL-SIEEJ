---
name: dag-airflow
description: Genera el DAG de Airflow del pipeline con sus operadores bootstrap y update.
---

# Skill: DAG Airflow

## Purpose
Invocar en la Fase 5 para generar el archivo DAG que orquesta los stages del pipeline en Airflow 3.x.

## Steps

1. Definir el `dag_id` con el formato `etl_{flujo}_bootstrap` y `etl_{flujo}_update`.
2. Configurar `schedule_interval` según la frecuencia del pipeline (`None` para bootstrap, cron para update).
3. Definir `default_args` con `owner`, `retries` y `retry_delay` por separado para bootstrap y update.
4. Crear las funciones `run_bootstrap()` y `run_update()` que instancian `Pipeline` con sus stages correspondientes.
5. Encadenar los stages con `>>` en el orden: `extract >> transform >> load`.
6. Agregar la función `main()` al final para ejecución local en modo bootstrap sin Airflow.
7. Usar el patrón `sys.path.append` al inicio para resolver imports del proyecto.
8. Guardar en `./dags/etl_{flujo}.py`.

## Template

→ Ver `template.py` en esta carpeta.
