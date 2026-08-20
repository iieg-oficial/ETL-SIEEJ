import io
import zipfile
from collections.abc import Callable

import pytest

DATASET_DIR = "conjunto_de_datos"
CATALOG_MEMBER = "catalogos/tc_actividad.csv"

CSV_HEADER = "CODIGO_ACTIVIDAD,CODIGO_ENTIDAD,ENTIDAD,ANIO,MES,H001A,H001D,J000A,O101A,M312A,ESTATUS"
CATALOG_CSV = "\n".join(
    [
        "CODIGO_ACTIVIDAD,DESCRIPCION",
        "31-33,Industrias manufactureras",
        "311,Industria alimentaria",
    ]
)


def _make_zip(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return buffer.getvalue()


def _csv_row(
    codigo: str = "31-33",
    cod_entidad: str = "\t14",
    entidad: str = "Jalisco",
    anio: str = "2026",
    mes: str = "1",
    per_ocu_tot: str = "79150",
    horas: str = "16337.001",
    remuneraciones: str = "1153818",
    valor_produccion: str = "25622352",
    valor_ventas: str = "24926158",
    estatus: str = "Cifras preliminares",
) -> str:
    """One dataset row. Defaults mirror a real record, tab-padded entity included."""
    return (
        f"{codigo},{cod_entidad},{entidad},{anio},{mes},{per_ocu_tot},{horas},"
        f"{remuneraciones},{valor_produccion},{valor_ventas},{estatus}"
    )


@pytest.fixture
def make_zip() -> Callable[[dict[str, bytes]], bytes]:
    return _make_zip


@pytest.fixture
def csv_header() -> str:
    return CSV_HEADER


@pytest.fixture
def csv_row() -> Callable[..., str]:
    return _csv_row


@pytest.fixture
def make_dataset_zip(make_zip, csv_row) -> Callable[..., bytes]:
    """Build a ZIP shaped like the INEGI publication: one dataset CSV plus the catalog."""

    def _build(year: str = "2026", rows: list[str] | None = None, catalog: str = CATALOG_CSV) -> bytes:
        rows = rows if rows is not None else [csv_row()]
        member = f"{DATASET_DIR}/tr_variable_total_entidad_mensual_2018_{year}.csv"
        return make_zip(
            {
                member: "\n".join([CSV_HEADER, *rows]).encode("utf-8"),
                CATALOG_MEMBER: catalog.encode("utf-8"),
            }
        )

    return _build
