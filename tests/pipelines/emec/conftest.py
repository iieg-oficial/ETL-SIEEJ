import io
import zipfile
from collections.abc import Callable

import pytest

DATASET_DIR = "conjunto_de_datos"
CATALOG_MEMBER = "catalogos/tc_actividad.csv"

CSV_HEADER = "CODIGO_ACTIVIDAD,ANIO,MES,ENTIDAD,H000W_I000W,J000W,REMUNERACION_MEDIA,M000W,K100W,ESTATUS"
CATALOG_CSV = "\n".join(
    [
        "CODIGO_ACTIVIDAD,DESCRIPCION_ACTIVIDAD",
        "43,Comercio al por mayor",
        "46,Comercio al por menor",
    ]
)


def _make_zip(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return buffer.getvalue()


def _csv_row(
    codigo: str = "43",
    anio: str = "2026",
    mes: str = "\t01",
    entidad: str = "Jalisco",
    per_ocu_tot: str = "79.39817072",
    remuneraciones_tot: str = "70.43033482",
    remuneraciones_media: str = "88.70523613",
    ingresos: str = "50.80201758",
    compras: str = "54.37760289",
    estatus: str = "Cifras preliminares",
) -> str:
    """One dataset row. Defaults mirror a real Jalisco record."""
    return (
        f"{codigo},{anio},{mes},{entidad},{per_ocu_tot},{remuneraciones_tot},"
        f"{remuneraciones_media},{ingresos},{compras},{estatus}"
    )


@pytest.fixture
def make_zip() -> Callable[[dict[str, bytes]], bytes]:
    return _make_zip


@pytest.fixture
def dataset_dir() -> str:
    return DATASET_DIR


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
        member = f"{DATASET_DIR}/tr_emec_entidad_federativa_indice_2008_{year}.csv"
        return make_zip(
            {
                member: "\n".join([CSV_HEADER, *rows]).encode("utf-8"),
                CATALOG_MEMBER: catalog.encode("utf-8"),
            }
        )

    return _build
