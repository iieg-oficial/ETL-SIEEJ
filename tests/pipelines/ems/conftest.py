import io
import zipfile
from collections.abc import Callable

import pytest

DATASET_DIR = "conjunto_de_datos"
CATALOG_MEMBER = "catalogos/tc_actividad.csv"

CSV_HEADER = "CODIGO_ACTIVIDAD,NOM_ENT,CVEGEO,ANIO,MES,M000,H000A,H000,I000A,K000,J000,ESTATUS"
CATALOG_CSV = "\n".join(
    [
        "CODIGO_ACTIVIDAD,DESCRIPCION_ACTIVIDAD",
        "51,Información en medios masivos",
        "61,Servicios educativos",
    ]
)


def _make_zip(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return buffer.getvalue()


def _csv_row(
    codigo: str = "51",
    nom_ent: str = "Jalisco",
    cvegeo: str = "14",
    anio: str = "2026",
    mes: str = "\t01",
    ingresos: str = "29.8498949",
    per_ocu_tot: str = "77.25054857",
    per_ocu_dep: str = "",
    per_ocu_no_dep: str = "",
    gastos: str = "27.35093621",
    remuneraciones: str = "85.41058831",
    estatus: str = "Cifras preliminares",
) -> str:
    """One dataset row. Defaults mirror a real record, empty personal breakdown included."""
    return (
        f"{codigo},{nom_ent},{cvegeo},{anio},{mes},{ingresos},{per_ocu_tot},"
        f"{per_ocu_dep},{per_ocu_no_dep},{gastos},{remuneraciones},{estatus}"
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
        member = f"{DATASET_DIR}/tr_ems_entidad_federativa_indice_2013_{year}.csv"
        return make_zip(
            {
                member: "\n".join([CSV_HEADER, *rows]).encode("utf-8"),
                CATALOG_MEMBER: catalog.encode("utf-8"),
            }
        )

    return _build
