---
name: testing-rules
description: Reglas para pruebas end-to-end de pipelines ETL en entorno docker local.
applyTo: "dags/**/*.py,core/pipelines/**"
---

## Ejecución

- Correr el pipeline desde la función `main` del DAG en modo `bootstrap`.
- Usar BD docker local (`just up-database` previo).
- No tocar BD de producción.

## Validaciones mínimas

1. El pipeline ejecuta sin excepciones.
2. Logs de cada stage (`extract`, `transform`, `load`) generados y sin errores.
3. La BD se pobla con el conteo esperado en cada tabla (catálogos primero, principales después).
4. FKs sin huérfanos.
5. Columnas no nulas no contienen `NULL`.
6. Columnas con `TITLE_COLS`/`CAPITALIZE_COLS` lucen normalizadas.
7. Geo keys (`cve_geo_id`) existen en `cvegeo.municipios` o `cvegeo.localidades`.
8. La vista de integración (V4) devuelve filas y aplica el filtro Jalisco si corresponde.

## Update (segunda ejecución)

- Re-correr el DAG en modo `update`.
- Verificar que **no** se dupliquen registros.
- Si el pipeline usa SCD (ver `bootstrap-update-rules`): validar `valid_from`, `valid_to`, `is_current`.

## Reporte

Si hay incidencias, generar un reporte estructurado con:

- Pipeline, etapa, archivo, línea (cuando aplique).
- Conteos source vs DB.
- Listado de problemas detectados con sample de filas afectadas.
- Sugerencia de corrección.

El agente de validación profunda es `loofy-agent`.
