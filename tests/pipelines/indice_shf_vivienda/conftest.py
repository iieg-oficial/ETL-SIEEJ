import io
from collections.abc import Callable

import pandas as pd
import pytest

from core.pipelines.indice_shf_vivienda.constants import RENAME_HEADER, SHEET_NAME

SOURCE_COLUMNS = ["Consecutivo", *RENAME_HEADER]

# Filas que reproducen los defectos conocidos de la fuente: el espacio al final
# del nombre del municipio, las tres columnas de geografía mutuamente
# excluyentes, y el mismo nombre de municipio en dos entidades distintas.
SAMPLE_ROWS: list[dict] = [
    {"Global": "Nacional", "Trimestre": 1, "Año": 2005, "Indice": 48.47},
    {"Global": "ZM Guadalajara", "Trimestre": 2, "Año": 2026, "Indice": 214.03},
    {"Estado": "Jalisco", "Trimestre": 3, "Año": 2017, "Indice": 101.22},
    {"Estado": "Coahuila", "Trimestre": 4, "Año": 2017, "Indice": 99.85},
    {"Estado": "Aguascalientes", "Municipio": "Jesús María ", "Trimestre": 1, "Año": 2026, "Indice": 180.11},
    {"Estado": "Ciudad de México", "Municipio": "Benito Juárez", "Trimestre": 1, "Año": 2026, "Indice": 205.40},
    {"Estado": "Quintana Roo", "Municipio": "Benito Juárez", "Trimestre": 1, "Año": 2026, "Indice": 176.92},
]


def _make_workbook(rows: list[dict], sheet_name: str = SHEET_NAME, columns: list[str] | None = None) -> bytes:
    df = pd.DataFrame(rows).reindex(columns=columns or SOURCE_COLUMNS)
    if "Consecutivo" in df.columns:
        df["Consecutivo"] = range(1, len(df) + 1)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    return buffer.getvalue()


@pytest.fixture
def make_workbook() -> Callable[..., bytes]:
    return _make_workbook


@pytest.fixture
def workbook_bytes() -> bytes:
    return _make_workbook(SAMPLE_ROWS)


@pytest.fixture
def extracted() -> pd.DataFrame:
    """The sheet as extract hands it to transform: renamed columns, everything as text."""
    df = pd.DataFrame(SAMPLE_ROWS).reindex(columns=list(RENAME_HEADER))
    df = df.rename(columns=RENAME_HEADER)
    return df.astype(object).where(df.notna(), None).astype("string")
