"""
Template para el reporte EDA estandarizado.
Sustituir los valores de ejemplo con los resultados reales del análisis.
"""

import json
from datetime import date

reporte: dict = {
    "flujo": "{flujo}",
    "fecha_analisis": str(date.today()),
    "fuente": {
        "url": "https://ejemplo.gob.mx/datos",
        "formato": "csv",
        "num_archivos": 1,
        "periodicidad": "mensual",
    },
    "dimensiones": {
        "filas": 125000,
        "columnas": 18,
    },
    "columnas": [
        {
            "nombre_original": "CVE_ENT",
            "tipo_original": "object",
            "tipo_homologado": "VARCHAR(2)",
            "es_clave": True,
            "es_catalogo": True,
            "valores_unicos": 32,
            "nulos_pct": 0.0,
            "muestra_valores": ["01", "02", "03"],
        },
    ],
    "geografia": {
        "nivel": "municipal",
        "columnas_geo": ["CVE_ENT", "CVE_MUN"],
    },
    "notas": "La fuente mezcla registros históricos con actualizaciones. Requiere SCD.",
}

output_path = "./core/pipelines/{flujo}/eda/reporte_eda.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(reporte, f, indent=2, ensure_ascii=False)

print(f"Reporte guardado en {output_path}")
print(f"  Flujo       : {reporte['flujo']}")
print(f"  Filas       : {reporte['dimensiones']['filas']}")
print(f"  Columnas    : {reporte['dimensiones']['columnas']}")
catalogos = [c["nombre_original"] for c in reporte["columnas"] if c["es_catalogo"]]
print(f"  Catálogos   : {catalogos}")
