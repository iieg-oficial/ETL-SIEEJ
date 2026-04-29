---
name: eda-reporte
description: Genera el reporte JSON estandarizado como output del análisis exploratorio de datos.
---

# Skill: EDA Reporte

## Purpose
Invocar al finalizar el script EDA para serializar los resultados en un JSON estructurado que será consumido por los agentes DB y DEA.

## Steps

1. Ejecutar el script EDA capturando los resultados en variables Python (no imprimir únicamente en consola).
2. Construir el diccionario de reporte siguiendo el schema definido en `template.py` de esta carpeta.
3. Serializar con `json.dump(reporte, f, indent=2, ensure_ascii=False)`.
4. Guardar en `./core/pipelines/{flujo}/eda/reporte_eda.json`.
5. Imprimir un resumen de los campos más relevantes (flujo, filas, columnas detectadas como catálogo) para confirmar que el reporte se generó correctamente.

## Template

→ Ver `template.py` en esta carpeta.

## References

- Archivo de ejemplo: `core/pipelines/fiscalia/` (adaptación del script de análisis)
