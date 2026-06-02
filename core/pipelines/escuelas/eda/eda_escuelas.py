import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[4]))

from core.pipelines.escuelas.constants import DIRECTORIO_DATASET, ESTADISTICA_DATASET, PIPELINE_NAME
from core.pipelines.escuelas.stages.extract import EscuelasExtract


def homologate_type(dtype: Any) -> str:
    dtype_name = str(dtype)
    if "int" in dtype_name:
        return "INTEGER"
    if "float" in dtype_name:
        return "FLOAT"
    if "date" in dtype_name or "time" in dtype_name:
        return "DATE"
    return "VARCHAR"


def column_report(dataset: str, df: pd.DataFrame) -> list[dict[str, Any]]:
    rows = len(df)
    report = []

    for column in df.columns:
        unique_values = int(df[column].nunique(dropna=True))
        null_count = int(df[column].isna().sum())
        sample_values = [str(value) for value in df[column].dropna().drop_duplicates().head(5).tolist()]
        is_key = (
            column in {"clave_ct", "turno", "nivel", "programa"}
            if dataset == DIRECTORIO_DATASET
            else column
            in {
                "nivel_programa",
                "sostenimiento",
            }
        )

        report.append(
            {
                "dataset": dataset,
                "nombre_original": column,
                "tipo_original": str(df[column].dtype),
                "tipo_homologado": homologate_type(df[column].dtype),
                "es_clave": is_key,
                "es_catalogo": unique_values < 100,
                "valores_unicos": unique_values,
                "nulos_pct": round((null_count / rows) * 100, 4) if rows else 0.0,
                "muestra_valores": sample_values,
            }
        )

    return report


def build_report() -> dict[str, Any]:
    extractor = EscuelasExtract(mode="bootstrap")
    sources = extractor.source()
    datasets = extractor.action(sources)

    directorio = datasets[DIRECTORIO_DATASET]
    estadistica = datasets[ESTADISTICA_DATASET]

    directorio_totals = directorio[["escuelas", "total_matriculados", "total_docentes_directivo"]].sum()
    estadistica_totals = estadistica.loc[
        estadistica["sostenimiento"].str.lower() != "total", ["escuelas", "matricula", "docentes"]
    ].sum()

    return {
        "flujo": PIPELINE_NAME,
        "fecha_analisis": str(date.today()),
        "fuente": {
            "url": "Google Drive folder",
            "formato": "csv",
            "num_archivos": 2,
            "periodicidad": "on-demand",
            "archivos": {
                DIRECTORIO_DATASET: str(sources[DIRECTORIO_DATASET]),
                ESTADISTICA_DATASET: str(sources[ESTADISTICA_DATASET]),
            },
        },
        "dimensiones": {
            DIRECTORIO_DATASET: {"filas": len(directorio), "columnas": len(directorio.columns)},
            ESTADISTICA_DATASET: {"filas": len(estadistica), "columnas": len(estadistica.columns)},
        },
        "columnas": column_report(DIRECTORIO_DATASET, directorio) + column_report(ESTADISTICA_DATASET, estadistica),
        "geografia": {
            "nivel": "municipal",
            "columnas_geo": ["municipio", "nombre_municipio", "localidad", "nombre_localidad"],
            "filtro_geografico": "Jalisco",
        },
        "validaciones": {
            "directorio_total_escuelas": int(directorio_totals["escuelas"]),
            "directorio_total_matricula": int(directorio_totals["total_matriculados"]),
            "directorio_total_docentes": int(directorio_totals["total_docentes_directivo"]),
            "estadistica_sin_total_escuelas": int(estadistica_totals["escuelas"]),
            "estadistica_sin_total_matricula": int(estadistica_totals["matricula"]),
            "estadistica_sin_total_docentes": int(estadistica_totals["docentes"]),
            "matricula_por_sexo_consistente": bool(
                (
                    directorio["hombres_matriculados"] + directorio["mujeres_matriculadas"]
                    == directorio["total_matriculados"]
                ).all()
            ),
        },
        "notas": (
            "Los datos se cargan con anio=2026. Las filas de sostenimiento total en estadistica se preservan "
            "como parte de la fuente."
        ),
    }


def main() -> None:
    report = build_report()
    output_path = Path("core/pipelines/escuelas/eda/reporte_eda.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    print(f"Reporte guardado en {output_path}")
    print(f"  Flujo       : {report['flujo']}")
    print(f"  Archivos    : {report['fuente']['num_archivos']}")
    print(f"  Directorio  : {report['dimensiones'][DIRECTORIO_DATASET]['filas']:,} filas")
    print(f"  Estadistica : {report['dimensiones'][ESTADISTICA_DATASET]['filas']:,} filas")


if __name__ == "__main__":
    main()
