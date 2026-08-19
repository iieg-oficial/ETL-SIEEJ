import io
import zipfile
from collections.abc import Callable

import pytest

DATASET_DIR = "conjunto_de_datos"

CSV_HEADER = (
    "PRODUCTO,COBERTURA,ANIO,ID_MES,CVEGEO,CVE_ENT,ESPECIE_GANADERA,NUMERO_CABEZAS,"
    "ESTATUS_DATO_CBZ,PRODUCCION_CARNE,ESTATUS_DATO_PROD,VALOR_PRODUCCION,"
    "ESTATUS_DATO_VPROD,ESTATUS"
)


def _make_zip(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return buffer.getvalue()


def _csv_row(
    anio: str = "2026",
    mes: str = "\t\t01",
    cvegeo: str = "14",
    especie: str = "Ganado bovino",
    cabezas: str = "100",
    estatus_cbz: str = "Disponible",
    carne: str = "10",
    estatus_prod: str = "Disponible",
    valor: str = "500",
    estatus_vprod: str = "Disponible",
    estatus: str = "Cifras Preliminares",
) -> str:
    """One dataset row. Defaults mirror a real Jalisco record."""
    return (
        f"ESGRM. Mensual,Estatal,{anio},{mes},{cvegeo},{cvegeo},{especie},{cabezas},"
        f"{estatus_cbz},{carne},{estatus_prod},{valor},{estatus_vprod},{estatus}"
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
    """Build a ZIP shaped like the INEGI publication: one CSV per year."""

    def _build(years: dict[str, list[str]] | None = None) -> bytes:
        years = years or {"2026": [csv_row()]}
        members = {
            f"{DATASET_DIR}/esgrm_mensual_tr_cifra_{year}.csv": "\n".join([CSV_HEADER, *rows]).encode("latin-1")
            for year, rows in years.items()
        }
        return make_zip(members)

    return _build
