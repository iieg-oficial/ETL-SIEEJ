---
name: eda-reporte
description: Genera el reporte JSON estandarizado como output del análisis exploratorio de datos.
---

# Skill: EDA Reporte

## Purpose
Invocar al finalizar el script EDA para serializar los resultados en un JSON estructurado que será consumido por los agentes DB y DEA.

## Steps

1. Ejecutar el script EDA capturando los resultados en variables Python (no imprimir únicamente en consola).
2. Construir el diccionario de reporte siguiendo el schema definido abajo.
3. Serializar con `json.dump(reporte, f, indent=2, ensure_ascii=False)`.
4. Guardar en `./core/pipelines/{flujo}/eda/reporte_eda.json`.
5. Imprimir un resumen de los campos más relevantes (flujo, filas, columnas detectadas como catálogo) para confirmar que el reporte se generó correctamente.

## Template

```python
reporte = {
    "flujo": "{flujo}",
    "fecha_analisis": "YYYY-MM-DD",
    "fuente": {
        "url": "https://...",
        "formato": "csv|xlsx|json|...",
        "num_archivos": 1,
        "periodicidad": "mensual|anual|trimestral|on-demand"
    },
    "dimensiones": {
        "filas": 0,
        "columnas": 0
    },
    "columnas": [
        {
            "nombre_original": "nombre_en_fuente",
            "tipo_original": "object|int64|float64|...",
            "tipo_homologado": "VARCHAR|INT|FLOAT|DATE|TIMESTAMP",
            "es_clave": False,
            "es_catalogo": False,
            "valores_unicos": 0,
            "nulos_pct": 0.0,
            "muestra_valores": []
        }
    ],
    "geografia": {
        "nivel": "municipal|estatal|nacional|ninguno",
        "columnas_geo": ["cve_mun", "cve_ent"]
    },
    "notas": ""
}
```
