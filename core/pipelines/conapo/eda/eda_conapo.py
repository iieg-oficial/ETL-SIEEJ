"""
EDA script for CONAPO population data.
Analyzes three datasets: mid-year population, large age groups, and demographic indicators.
"""

import io
import json
import zipfile
from datetime import date

import pandas as pd
import requests
import urllib3

from core.pipelines.conapo.config import settings
from core.utils.logger import get_logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = get_logger("conapo.eda")


def fetch_zip() -> zipfile.ZipFile:
    """Download and open the CONAPO ZIP file."""
    logger.info(f"Fetching {settings.CONAPO_URL}")
    response = requests.get(settings.CONAPO_URL, verify=False, timeout=120)
    response.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(response.content))


def read_excel_from_zip(z: zipfile.ZipFile, filename: str) -> pd.DataFrame:
    """Read an Excel file from the ZIP archive."""
    with z.open(filename) as f:
        return pd.read_excel(f)


def analyze_dataframe(df: pd.DataFrame, name: str) -> dict:
    """Analyze a DataFrame and return EDA results."""
    logger.info(f"Analyzing {name}: {df.shape}")

    columns_info = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        nunique = df[col].nunique()
        null_count = df[col].isna().sum()
        null_pct = round(null_count / len(df) * 100, 2) if len(df) > 0 else 0

        # Determine if it's a key column
        es_clave = col in ["CLAVE", "CLAVE_ENT", "NOM_ENT", "NOM_MUN", "SEXO", "AÑO"]

        # Determine if it's a catalog (less than 100 unique values and not numeric)
        es_catalogo = nunique < 100 and dtype == "object"

        # Get sample values
        if dtype == "object":
            muestra = df[col].dropna().unique()[:5].tolist()
        else:
            muestra = df[col].dropna().head(5).tolist()

        # Determine homologated type
        if col in ["CLAVE", "CLAVE_ENT"]:
            tipo_homologado = "INTEGER"
        elif col in ["NOM_ENT", "NOM_MUN"]:
            tipo_homologado = "VARCHAR(100)"
        elif col == "SEXO":
            tipo_homologado = "VARCHAR(10)"
        elif col == "AÑO":
            tipo_homologado = "INTEGER"
        elif dtype in ["int64", "float64"]:
            tipo_homologado = "INTEGER" if dtype == "int64" else "FLOAT"
        else:
            tipo_homologado = "VARCHAR(50)"

        columns_info.append(
            {
                "nombre_original": col,
                "tipo_original": dtype,
                "tipo_homologado": tipo_homologado,
                "es_clave": es_clave,
                "es_catalogo": es_catalogo,
                "valores_unicos": int(nunique),
                "nulos_pct": null_pct,
                "muestra_valores": muestra,
            }
        )

    return {
        "nombre": name,
        "filas": len(df),
        "columnas": len(df.columns),
        "columnas_info": columns_info,
    }


def main():
    """Run EDA analysis on CONAPO data."""
    z = fetch_zip()

    # Analyze each dataset
    df_pma = read_excel_from_zip(z, "14_Jalisco/1_Grupo_Quinq_14_JL.xlsx")
    df_gge = read_excel_from_zip(z, "14_Jalisco/2_Gran_Gedad_14_JL.xlsx")
    df_idd = read_excel_from_zip(z, "14_Jalisco/3_Indicadores_Dem_14_JL.xlsx")

    pma_analysis = analyze_dataframe(df_pma, "poblacion_mitad_anio")
    gge_analysis = analyze_dataframe(df_gge, "grandes_grupos_edad")
    idd_analysis = analyze_dataframe(df_idd, "indicadores_demograficos")

    # Build report
    reporte = {
        "flujo": "conapo",
        "fecha_analisis": str(date.today()),
        "fuente": {
            "url": settings.CONAPO_URL,
            "formato": "xlsx (zip)",
            "num_archivos": 3,
            "periodicidad": "anual",
            "periodo": "1990-2040 (proyecciones)",
        },
        "datasets": [pma_analysis, gge_analysis, idd_analysis],
        "dimensiones": {
            "filas_totales": pma_analysis["filas"] + gge_analysis["filas"] + idd_analysis["filas"],
            "num_datasets": 3,
        },
        "geografia": {
            "nivel": "municipal",
            "columnas_geo": ["CLAVE", "CLAVE_ENT", "NOM_ENT", "NOM_MUN"],
            "entidad": "Jalisco (14)",
            "num_municipios": df_pma["CLAVE"].nunique(),
        },
        "notas": (
            "Datos de proyecciones de población de CONAPO para Jalisco. "
            "Tres datasets: población por grupos quinquenales, grandes grupos de edad, "
            "e indicadores demográficos. Periodo 1990-2040."
        ),
    }

    # Save report
    output_path = "./core/pipelines/conapo/eda/reporte_eda.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)

    logger.info(f"Report saved to {output_path}")
    logger.info(f"  Total rows: {reporte['dimensiones']['filas_totales']}")
    logger.info(f"  Datasets: {reporte['dimensiones']['num_datasets']}")
    logger.info(f"  Municipalities: {reporte['geografia']['num_municipios']}")

    return reporte


if __name__ == "__main__":
    main()
