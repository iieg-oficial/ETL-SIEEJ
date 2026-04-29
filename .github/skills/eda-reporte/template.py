"""
Template para el reporte EDA estandarizado.
Sustituir los valores de ejemplo con los resultados reales del análisis.
"""

import json
from datetime import date

reporte: dict = {
    "flujo": "{flujo}",  # e.g. "fiscalia"
    "fecha_analisis": str(date.today()),  # ISO 8601
    "fuente": {
        "url": "https://ejemplo.gob.mx/datos",  # URL de descarga o None si es archivo manual
        "formato": "csv",  # "csv", "xlsx", "json", "zip", etc.
        "num_archivos": 1,  # Número de archivos que componen la fuente
        "periodicidad": "mensual",  # "mensual", "anual", "trimestral", "on-demand", etc.
    },
    "dimensiones": {
        "filas": 125000,
        "columnas": 18,
    },
    "columnas": [
        {
            "nombre_original": "CVE_ENT",
            "tipo_original": "object",  # dtype de pandas
            "tipo_homologado": "VARCHAR(2)",  # tipo SQL propuesto
            "es_clave": True,  # True si identifica al registro
            "es_catalogo": True,  # True si valores únicos < 100
            "valores_unicos": 32,
            "nulos_pct": 0.0,  # Porcentaje de nulos (0.0 - 100.0)
            "muestra_valores": ["01", "02", "03"],
        },
        {
            "nombre_original": "FECHA_HECHO",
            "tipo_original": "object",
            "tipo_homologado": "DATE",
            "es_clave": False,
            "es_catalogo": False,
            "valores_unicos": 3650,
            "nulos_pct": 1.2,
            "muestra_valores": ["2023-01-15", "2023-02-03"],
        },
        # Repetir para cada columna del dataset
    ],
    "geografia": {
        "nivel": "municipal",  # "nacional", "estatal", "municipal"
        "columnas_geo": ["CVE_ENT", "CVE_MUN"],
    },
    "notas": "La fuente mezcla registros históricos con actualizaciones. Requiere SCD.",
}

# Serializar y guardar
output_path = "./core/pipelines/{flujo}/eda/reporte_eda.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(reporte, f, indent=2, ensure_ascii=False)

print(f"Reporte guardado en {output_path}")
print(f"  Flujo       : {reporte['flujo']}")
print(f"  Filas       : {reporte['dimensiones']['filas']}")
print(f"  Columnas    : {reporte['dimensiones']['columnas']}")
catalogos = [c["nombre_original"] for c in reporte["columnas"] if c["es_catalogo"]]
print(f"  Catálogos   : {catalogos}")
