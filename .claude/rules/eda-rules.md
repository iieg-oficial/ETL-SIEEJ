---
description: EDA script requirements. Applies to eda/*.py files.
---

# EDA Rules

> Aplican a: EDA

## Rules

- Escribir los scripts de EDA como archivos `.py`, no notebooks. Los notebooks dificultan la revisión en Git.
- Guardar todos los scripts en `./core/pipelines/{flujo}/eda/`. Nombre de archivo: `eda_{flujo}.py`.
- El script debe cubrir los siguientes pasos en orden:
  1. Descargar o cargar los archivos fuente (usar la misma lógica que usará el stage `extract`).
  2. Mostrar las primeras filas y los tipos de datos de cada columna (`dtypes`).
  3. Reportar número total de registros y número de columnas.
  4. Identificar columnas clave (IDs, fechas, periodos).
  5. Contar valores únicos por columna para detectar posibles catálogos (< 100 valores únicos = candidato a catálogo).
  6. Analizar nivel geográfico: nacional, estatal o municipal (columnas `cve_ent`, `cve_mun`, etc.).
  7. Analizar valores nulos y vacíos: `NaN`, `NA`, `N/A`, cadenas vacías, espacios.
  8. Analizar periodicidad si hay múltiples archivos fuente (mensual, anual, etc.).
- El output final del script debe ser el reporte JSON generado con el skill `eda-reporte`. No mostrar solo prints; serializar resultados.
- No guardar archivos intermedios dentro de `eda/`. Solo el script y el `reporte_eda.json`.
- Importar utilidades del proyecto desde `core.utils` cuando sea posible (p.ej. `normalize_text`, `get_logger`).
