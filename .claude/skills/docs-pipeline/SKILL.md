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
6. Construir el README siguiendo el template de abajo.
7. Guardar en `./core/pipelines/{flujo}/README.md`.

## Template

```markdown
# {Nombre del Pipeline}

> {Descripción en una línea de qué datos procesa y para qué sirve.}

## Fuente

| Campo       | Valor                        |
|-------------|------------------------------|
| Proveedor   | {nombre del proveedor}       |
| URL         | {url de descarga}            |
| Formato     | {csv/xlsx/json/...}          |
| Frecuencia  | {mensual/anual/...}          |
| Último dato | {año o fecha del último dato conocido} |

## Esquema de Base de Datos

![Diagrama ER](assets/er_{flujo}.png)

### Tablas catálogo
- **`cat_{nombre}`** — {descripción breve de qué contiene}

### Tabla principal
- **`stg_{flujo}`** — {descripción de qué registra, granularidad, período cubierto}

### Vista de integración
- **`v_{flujo}`** — {qué desnormaliza y para qué se usa}

## Implementación ETL

| Modo      | DAG                       | Schedule       |
|-----------|---------------------------|----------------|
| Bootstrap | `etl_{flujo}_bootstrap`   | On Demand      |
| Update    | `etl_{flujo}_update`      | `{cron expr}`  |

**Tipo de update:** {solo-inserciones / SCD}

## Árbol de archivos

\`\`\`
core/pipelines/{flujo}/
├── ...
\`\`\`

## Metodología ETL

**Extract:** {descripción de cómo se descargan los datos}

**Transform:** {descripción de las transformaciones aplicadas}

**Load:** {descripción del método de carga y manejo de duplicados/cambios}

## Variables de Entorno

| Variable | Descripción |
|----------|-------------|
| `VAR_1`  | {descripción} |

## Pasos Manuales

1. {Paso manual requerido, si aplica}
```
