---
name: create-pipeline
description: Crea un pipeline ETL completo para el proyecto SIEEJ — desde EDA hasta commits. Orquestado por el agente `data-engineer`.
argument-hint: <nombre_pipeline> <descripción_fuente>
agent: data-engineer
---

# Crear Pipeline ETL — SIEEJ

Esta orden produce un pipeline ETL completo para el proyecto SIEEJ: análisis de la fuente, esquema de BD, migraciones Flyway, stages, DAG, documentación y commits atómicos listos para PR.

El agente `data-engineer` coordinará el flujo en 7 fases, delegando en los agentes especializados (`eda`, `db`, `just`, `etl`, `docs`, `git`).

---

## Información requerida

Completa los siguientes campos. Si tienes los archivos de la fuente, adjúntalos directamente al chat (Excel, CSV, diccionarios, catálogos).

### 1. Nombre del pipeline (`snake_case`)

Ejemplo: `empleo_formal`, `accidentes_viales`, `rezago_educativo`.

**Nombre:** `{pipeline_name}`

### 2. Descripción de la fuente

¿Qué datos contiene? ¿De qué dependencia o sistema provienen?

**Descripción:** `{source_description}`

### 3. Formato y origen

| Formato | Origen |
|---|---|
| Excel / CSV | Archivo descargado manualmente o URL directa |
| API REST | Endpoint HTTP (JSON/XML/Excel) |
| Google Drive | Carpeta compartida |

**Formato:** `{format}`
**URL / path:** `{url_or_path}`

### 4. Frecuencia de actualización

`diaria` · `semanal` · `mensual` · `trimestral` · `semestral` · `anual` · `única`

> El sistema determina automáticamente:
> - ≤ 3 meses → DAG bootstrap **+** update.
> - > 3 meses o única → solo DAG bootstrap.

**Frecuencia:** `{frequency}`

### 5. Comportamiento al actualizarse

Cuando llega una nueva versión de la fuente:

| Valor | Significado |
|---|---|
| `sobreescribe` | El archivo reemplaza a la versión anterior (contiene todo). |
| `solo_nuevos` | El archivo solo trae datos nuevos del período. |
| `mixto` | El archivo sobreescribe registros existentes **y** agrega nuevos. |

> Determina la estrategia de update:
> - `sobreescribe` → re-ingestión completa (bootstrap_only).
> - `solo_nuevos` + llave natural clara → upsert.
> - `mixto` con cambios en registros existentes → SCD2 (ver skill `scd2-pattern`).

**Comportamiento:** `{source_behavior}`

### 6. ¿Requiere georreferencia contra `cvegeo`?

Los datos de municipios/entidades se resuelven vía FDW a la BD `cvegeo` del IIEG.

**¿Requiere cvegeo?** `{requires_cvegeo}` (sí / no)

### 7. Cron expression (opcional)

Si ya tienes un cron definido, indícalo. Si lo dejas vacío, el sistema lo sugerirá según la frecuencia.

**Cron:** `{cron_expression}`

---

## Instrucciones para el agente `data-engineer`

1. Ejecutar las 7 fases descritas en `.github/agents/data-engineer.agent.md` en orden estricto.
2. Presentar el resumen del EDA al usuario **antes** de continuar con la fase 2 y esperar confirmación.
3. Detener el flujo y reportar si cualquier fase falla; no commitear si la prueba local (fase 5) no pasó.
4. Al finalizar, entregar el reporte final con archivos creados, rama, número de commits y próximos pasos manuales.
