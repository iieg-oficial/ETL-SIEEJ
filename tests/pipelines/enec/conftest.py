import io
import zipfile
from collections.abc import Callable

import pytest

from core.pipelines.enec.constants import MEASURE_RENAME

DATASET_DIR = "conjunto_de_datos"

# El encabezado real trae "J000A " CON UN ESPACIO AL FINAL; el fixture lo
# reproduce a propósito para que las pruebas ejerzan el strip del extract.
SOURCE_MEASURES = [f"{c} " if c == "J000A" else c for c in MEASURE_RENAME]

NACIONAL_HEADER = ",".join(
    [
        "CODIGO_ACTIVIDAD",
        "DESCRIPCION_ACTIVIDAD",
        "ANIO",
        "MES",
        "CVEGEO",
        "CVE_ENT",
        "NOM_ENT",
        *SOURCE_MEASURES,
        "ESTATUS",
    ]
)
ENTIDAD_HEADER = NACIONAL_HEADER


def _make_zip(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return buffer.getvalue()


def _measure_values(**overrides) -> list[str]:
    """A plausible value per measure, integers for counts and decimals for rates."""
    values = {}
    for source, name in MEASURE_RENAME.items():
        if name.startswith(("dias_", "horas_", "remuneracion_media", "salario_medio", "sueldo_medio")):
            values[source] = "123.456"
        else:
            values[source] = "1000"
    values.update(overrides)
    return [values[c] for c in MEASURE_RENAME]


def _csv_row(
    codigo: str = "23",
    descripcion: str = "Construcción",
    anio: str = "2026",
    mes: str = "\t01",
    cvegeo: str = "\t14",
    nom_ent: str = "Jalisco",
    estatus: str = "Cifras preliminares",
    **measures: str,
) -> str:
    campos = [codigo, descripcion, anio, mes, cvegeo, cvegeo, nom_ent, *_measure_values(**measures), estatus]
    return ",".join(campos)


@pytest.fixture
def make_zip() -> Callable[[dict[str, bytes]], bytes]:
    return _make_zip


@pytest.fixture
def csv_row() -> Callable[..., str]:
    return _csv_row


@pytest.fixture
def nacional_header() -> str:
    return NACIONAL_HEADER


@pytest.fixture
def make_dataset_zip(make_zip, csv_row) -> Callable[..., bytes]:
    """Build a ZIP shaped like the INEGI publication: a national and a state CSV."""

    def _build(
        year: str = "2026",
        nacional: list[str] | None = None,
        entidad: list[str] | None = None,
    ) -> bytes:
        nacional = nacional if nacional is not None else [csv_row(cvegeo="\t00", nom_ent="Nacional")]
        entidad = entidad if entidad is not None else [csv_row()]
        return make_zip(
            {
                f"{DATASET_DIR}/enec_absoluto_nacional_2018_{year}.csv": "\n".join([NACIONAL_HEADER, *nacional]).encode(
                    "utf-8"
                ),
                f"{DATASET_DIR}/enec_absoluto_entidad_2018_{year}.csv": "\n".join([ENTIDAD_HEADER, *entidad]).encode(
                    "utf-8"
                ),
            }
        )

    return _build
