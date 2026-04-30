---
description: Crea un agent team para construir un nuevo pipeline ETL completo en 9 fases secuenciales. Tú eres el lead del equipo y coordinas a los agentes especialistas.
---

# Nuevo Pipeline ETL — Agent Team

## Paso 1: Recopilar contexto

Antes de crear el equipo, completar la siguiente tabla con el usuario (preguntar si algún campo no está definido):

| Variable               | Valor                                                          |
|------------------------|----------------------------------------------------------------|
| `{flujo}`              | Nombre interno del pipeline en `snake_case` (p.ej. `repd`)    |
| `{fuente}`             | URL de descarga o descripción de la fuente de datos            |
| `{frecuencia}`         | Mensual / Anual / Trimestral / On-demand / Otra                |
| `{tipo_update}`        | `solo-inserciones` o `scd`                                     |
| `{contexto_adicional}` | Detalles relevantes: credenciales, nivel geográfico, tablas destino esperadas, etc. |

---

## Paso 2: Crear el equipo y ejecutar las fases

Crear un agent team. Eres el **lead**. Spawnar **un teammate a la vez** en el orden de la tabla. Esperar que el teammate reporte su output completo y pedir **confirmación explícita del usuario** antes de pasar a la siguiente fase.

Al spawnar cada teammate, sustituir los valores reales de `{flujo}`, `{fuente}`, `{frecuencia}`, `{tipo_update}` y `{contexto_adicional}` en el prompt — nunca pasar variables sin resolver.

| Fase | Agente       | Prompt de spawn                                                                                                                                                           | Confirmar |
|:----:|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------:|
| 0    | `dea`        | `Fase 0. Pipeline: {flujo}. Fuente: {fuente}. Frecuencia: {frecuencia}. Tipo de update: {tipo_update}. Contexto adicional: {contexto_adicional}. Revisar si falta información, preguntar al usuario, generar esqueleto del pipeline.` | ✅ |
| 1    | `eda-agent`  | `Fase 1. Pipeline: {flujo}. Fuente: {fuente}. Formato: {formato si se conoce}. Crear eda_{flujo}.py en ./core/pipelines/{flujo}/eda/, ejecutar con conda run -n etl python, generar reporte_eda.json.` | ✅ |
| 2    | `db-agent`   | `Fase 2. Pipeline: {flujo}. Nivel geográfico: {nivel según EDA}. Leer reporte_eda.json, generar migraciones Flyway, attributes.py, schemas.py y diagrama ER.`             | ✅ |
| 3    | `dea`        | `Fase 3. Pipeline: {flujo}. Leer reporte_eda.json y las migraciones generadas. Sintetizar el plan ETL (stages, frecuencia, tipo de update, tablas). Presentar al usuario y esperar aprobación.` | ✅ |
| 4    | `git-agent`  | `Fase 4. Pipeline: {flujo}. Nombre legible: {nombre}. Crear GitHub issue con template new-pipeline y la rama {numero_issue}-pipeline-{flujo} desde develop.`             | ✅ |
| 5    | `etl-agent`  | `Fase 5. Pipeline: {flujo}. Tipo de update: {tipo_update}. Frecuencia: {frecuencia}. Implementar stages extract/transform/load, DAG de Airflow y .env.example.`           | ✅ |
| 6    | `testing-agent` | `Fase 6. Pipeline: {flujo}. Ejecutar python dags/etl_{flujo}.py en modo bootstrap con conda run -n etl, validar BD Docker, generar reporte de pruebas PASS/FAIL por stage.` | ✅ |
| 7    | `docs-agent` | `Fase 7. Pipeline: {flujo}. Generar README.md en ./core/pipelines/{flujo}/ consolidando fuente, esquema de BD, DAG y variables de entorno.`                               | ✅ |
| 8    | `git-agent`  | `Fase 8. Pipeline: {flujo}. Issue #{numero_issue}. Commits atómicos por funcionalidad y abrir Pull Request hacia develop con Closes #{numero_issue}.`                    | ✅ |

---

## Paso 3: Cleanup

Al completar la Fase 8, hacer cleanup del equipo.

---

## Reglas de coordinación

- Declarar la fase activa al inicio de cada bloque: `[Fase N — {AGENTE}]`.
- Si un teammate reporta errores (p.ej. Fase 6 falla), no avanzar: notificar al usuario y coordinar la corrección con el agente correspondiente antes de reintentar.
- Si la Fase 3 no recibe aprobación del usuario, detener el flujo y esperar instrucciones.
