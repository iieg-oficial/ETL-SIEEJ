---
name: docs-pipeline
description: Genera el README interno del pipeline con toda la información de implementación.
---

# Skill: Documentación de Pipeline

## Purpose
Invocar en la Fase 7 para generar el `README.md` que documenta el pipeline para futuros desarrolladores.

## Steps

1. Leer `./core/pipelines/{flujo}/eda/reporte_eda.json` para extraer información de la fuente (URL, formato, frecuencia).
2. Leer las migraciones `V1`–`V4` en `./migrations/{flujo}/sql/` para documentar el esquema de BD y las tablas.
3. Leer `./dags/etl_{flujo}.py` para documentar el nombre del DAG, el `schedule_interval` y el orden de stages.
4. Leer `./core/pipelines/{flujo}/.env.example` para listar las variables de entorno requeridas.
5. Incluir el diagrama ER desde `./core/pipelines/{flujo}/assets/er_{flujo}.png` si existe.
6. Construir el README siguiendo `template.md` de esta carpeta.
7. Guardar en `./core/pipelines/{flujo}/README.md`.

## Template

→ Ver `template.md` en esta carpeta.
