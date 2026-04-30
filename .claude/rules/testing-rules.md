---
description: Testing rules for end-to-end pipeline validation. Applies to all files.
---

# Testing Rules

> Aplican a: TEST

## Rules

- Ejecutar el flujo completo usando la función `main()` del DAG directamente como script (`python dags/etl_{flujo}.py`) para simular la ejecución sin Airflow.
- Probar primero en modo `bootstrap`: valida que el pipeline procese todos los datos históricos sin errores.
- Revisar la BD de Docker para confirmar que las tablas estén pobladas con datos correctos.
- Verificar que los tipos de datos en BD coincidan con los definidos en las migraciones Flyway y en `schemas.py`.
- Si un stage falla, registrar: nombre del stage, traceback completo, causa probable, corrección sugerida.
- Generar un reporte de pruebas con resultado por stage (`PASS` / `FAIL`) antes de notificar al DEA.
- Si todos los stages pasan, confirmar con el número de registros insertados por tabla.
- No modificar el código fuente durante las pruebas. Documentar las incidencias en el reporte y delegarlas al agente ETL o DB para corrección.
