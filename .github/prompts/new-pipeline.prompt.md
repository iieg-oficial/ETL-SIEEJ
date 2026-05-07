---
description: "Use when starting a new ETL pipeline workflow and the team needs guided intake, strict planning, and missing-detail collection before implementation begins."
agent: "Data Engineer Agent"
argument-hint: "<pipeline_name> <source_urls_or_notes>"
---

# Nuevo Pipeline ETL

Este prompt debe iniciar siempre en modo planificación estricta.

## Parámetros esperados

| Parámetro | Requerido | Descripción |
|-----------|-----------|-------------|
| `flujo` | Sí | Nombre interno del pipeline en `snake_case`. |
| `fuentes` | Sí | URL(s), ruta(s) o instrucciones exactas para obtener los datos. |
| `tipo_fuente` | Sí | API, archivo descargable, scraping, base de datos externa u otro. |
| `formato_fuente` | Sí | CSV, XLSX, JSON, ZIP, HTML, endpoint, tabla, etc. |
| `frecuencia` | Sí | Mensual, trimestral, anual, semanal, diaria, on-demand u otra. |
| `tipo_update` | Sí | `solo-inserciones` o `scd`. |
| `nivel_geografico` | No | Nacional, estatal, municipal o sin componente geográfico. |
| `filtro_geografico` | No | Por ejemplo, solo Jalisco o todos los estados. |
| `tablas_destino` | No | Tabla principal esperada y catálogos conocidos. |
| `credenciales` | No | Token, API key, usuario/contraseña o ninguna. |
| `schedule_dag` | No | Cron, on-demand o decisión pendiente. |
| `reglas_negocio` | No | Transformaciones, filtros, deduplicación, vigencias, catálogos, etc. |
| `notas` | No | Restricciones, dependencias, acuerdos o riesgos conocidos. |

## Reglas de arranque

1. Antes de delegar, crear archivos o ejecutar Git, entra a Fase 0: planificación.
2. Si falta cualquier dato requerido o hay ambigüedad, lanza una sola tanda estructurada de preguntas con la herramienta de askQuestions.
3. No infieras reglas de negocio, frecuencia, estrategia de update, nivel geográfico, nombres de tablas, credenciales o decisiones operativas sin confirmación explícita.
4. Presenta un resumen de intake con datos confirmados, datos faltantes y riesgos antes de continuar.
5. Una vez aprobado el plan por el usuario, **continúa inmediatamente** con el Workflow del Data Engineer Agent (EDA → DB → ETL → DOCS → Git). No te detengas ni pidas permiso entre subfases salvo en los puntos explícitos del agente.
6. DEA mantiene la orquestación completa y ejecuta directamente Git (issue, branch, commits, PR). EDA, DB, ETL y DOCS solo ejecutan su especialidad y se invocan vía subagent.
7. El issue y el pull request deben salir de los skills `issue-template` y `pull-request-template`, cada uno usando su propio `template.md` local.
