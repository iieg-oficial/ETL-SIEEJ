---
name: eda-rules
description: Reglas para scripts de análisis exploratorio (EDA) de pipelines ETL SIEEJ.
paths:
- core/pipelines/**/eda/**/*.py
---

## Formato

- Solo scripts `.py`. Nunca notebooks `.ipynb`.
- Ubicación: `core/pipelines/{flujo}/eda/`.
- Un script por fuente o por nivel (estatal, municipal, etc.).

## Pasos obligatorios

Cada script debe ejecutar y reportar, en este orden:

1. Descarga / carga del archivo (con `requests`, `pandas`, `ZipFile` según aplique).
2. `df.shape`, `df.columns`, `df.dtypes`, `df.head()`.
3. Conteo de registros para entender escala.
4. Identificar columnas clave, columnas de fechas y columnas de georeferenciación.
5. Valores únicos por columna (para detectar catálogos).
6. Nivel geográfico (nacional / estatal / municipal / localidad).
7. Análisis de nulos: `NaN`, `NA`, `N/A`, vacíos, y todo lo que aparezca en `NULL_VALUES`.
8. Frecuencia de actualización: si hay múltiples archivos o columnas con fecha, documentar la periodicidad.

## Salida

Cada script genera un reporte JSON estandarizado siguiendo el skill `eda-reporte`. Guardar como:

```
core/pipelines/{flujo}/eda/reporte_{nombre}.json
```

El JSON es la única fuente de verdad consumida por el `db-agent` y el `etl-agent`.
