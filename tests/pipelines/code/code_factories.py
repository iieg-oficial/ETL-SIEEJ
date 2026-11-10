"""Constructores sinteticos con la forma de las cargas de CODE. No se copia ningun archivo real."""

from contextlib import contextmanager
from pathlib import Path

import geopandas as gpd
import pandas as pd
from core.acervo.client import Upload
from core.pipelines.code.constants import UPLOAD_FIELD

DATA_FIELD = "carga_de_datos"
RETO_NAME = "Puntos de activación del programa Reto, Reactivación para Todas y Todos"
ACADEMIAS_NAME = "Academias deportivas, Espacios para la Paz"
POLIDEPORTIVOS_NAME = "Polideportivos "


def make_upload(
    index: int = 0,
    name: str = RETO_NAME,
    field: str = UPLOAD_FIELD,
    uploaded_at: str = "2026-09-09 17:15:51+00:00",
    updated_at: str = "2026-09-09 17:16:53+00:00",
    etag: str = "abc123",
) -> Upload:
    return Upload(
        object_key=f"k{index}",
        filename="f.zip",
        size=1,
        uploaded_at=uploaded_at,
        envio="persona",
        envio_id=28,
        conjunto=RETO_NAME,
        updated_at=updated_at,
        field_path=f"conunto_datos[{index}].{field}",
        fecha_corte="",
        fecha_actualizacion="",
        etag=etag,
        dataset_name=name.strip(),
    )


CAT_DEPORTE = pd.DataFrame({"deporte": ["Atletismo", "Natación", "Charrería"], "id": [1, 19, 13]})
CAT_TIPO = pd.DataFrame({"tipo": ["Centro Regional", "Regular", None], "id": [1.0, 2.0, None]})


def gdf_from_rows(rows: list[dict]) -> gpd.GeoDataFrame:
    """Geometria en EPSG:6368 construida desde las columnas en grados, como los archivos reales."""
    frame = pd.DataFrame(rows)
    return gpd.GeoDataFrame(
        frame, geometry=gpd.points_from_xy(frame["x_6368"], frame["y_6368"]), crs="EPSG:4326"
    ).to_crs("EPSG:6368")


def write_gpkg(path: Path, rows: list[dict], layer: str) -> None:
    gdf_from_rows(rows).to_file(path, layer=layer, driver="GPKG")


DEPORTE_CSV = "deporte,id\nAtletismo,1\nNatación,19\nCharrería,13\n"
TIPO_CSV = "tipo,id\nCentro Regional,1\nRegular,2\n,\n"

ACADEMIA_ROW = {
    "fecha": "01/10/2026",
    "municipio": "Acatic",
    "cve_mun": "001",
    "beneficiarios_total": 75.0,
    "beneficiarios_hombres": 37.0,
    "beneficiarios_mujeres": 38.0,
    "deportenombrelargo": "CHARRERÍA",
    "deporte": "Charrería",
    "cat_deporte": 5,
    "tipo": "Regular",
    "cat_tipo": 2,
    "domicilio": "Plaza  Principal 1",
    "horarios": "Lunes 7:00 pm",
    "y_6368": 20.78,
    "x_6368": -102.9,
}

POLI_ROW = {
    "fecha": "01/01/2026",
    "clave_entidad": 14,
    "cve_mun": "039",
    "x_6368": -103.34,
    "y_6368": 20.7,
    "nombre_centro": "Polideportivo Paradero ",
    "domicilio": "Calle 1",
    "horarios": "Lunes a viernes",
    "deportes": "19,13",
    "servicios": "Escuela deportiva",
}


class FakeSession:
    def __init__(self):
        self.deletes = []

    def execute(self, statement, params=None):
        self.deletes.append(statement)
        return None

    def flush(self):
        pass


class FakeDb:
    def connect(self):
        pass

    def disconnect(self):
        pass

    @contextmanager
    def get_session(self):
        yield FakeSession()
