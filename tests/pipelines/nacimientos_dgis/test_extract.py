import io
import zipfile

import pytest

from core.pipelines.nacimientos_dgis.constants import CATALOG_DIR, CSV_SUFFIX, XLSX_SUFFIX
from core.pipelines.nacimientos_dgis.stages.extract import NacimientosDgisExtract


def _zip(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, data in files.items():
            z.writestr(name, data)
    return buf.getvalue()


@pytest.fixture
def extract() -> NacimientosDgisExtract:
    return NacimientosDgisExtract(year=2025)


def test_extract_csv_bytes_flat_edition(extract):
    """Older editions ship the CSV directly inside the zip."""
    archive = _zip({"Nacimientos_2024.csv": b"a,b\n1,2\n"})
    assert extract._member_bytes(archive, CSV_SUFFIX, "flat") == b"a,b\n1,2\n"


def test_extract_csv_bytes_nested_edition(extract):
    """The 2025 edition wraps the CSV in a second zip."""
    inner = _zip({"Nacimientos_2025.csv": b"c,d\n3,4\n"})
    outer = _zip({"Registros de Nacimientos 2025/sinac_2025.zip": inner})
    assert extract._member_bytes(outer, CSV_SUFFIX, "nested") == b"c,d\n3,4\n"


def test_extract_csv_bytes_missing_csv_raises_valueerror(extract):
    """A zip without a CSV fails loudly, not with a bare StopIteration."""
    archive = _zip({"readme.txt": b"nothing here"})
    with pytest.raises(ValueError, match="No se encontró"):
        extract._member_bytes(archive, CSV_SUFFIX, "empty")


def test_member_bytes_finds_any_suffix(extract):
    """El mismo descenso sirve para los XLSX del paquete de catálogos."""
    archive = _zip({"SEXO.xlsx": b"fake-xlsx"})
    assert extract._member_bytes(archive, XLSX_SUFFIX, "catalogos") == b"fake-xlsx"


def test_catalogos_a_medias_no_quedan_en_cache(extract, tmp_path, monkeypatch):
    """Una corrida que muere a media descarga no debe envenenar el caché."""
    extract.work_dir = tmp_path

    def _explota(package):
        raise RuntimeError("se cayo la red")

    monkeypatch.setattr(extract, "_catalog_archive", _explota)

    with pytest.raises(RuntimeError):
        extract._fetch_catalogs("sinac_catalogos_2024.zip")

    assert not (tmp_path / CATALOG_DIR / "sinac_catalogos_2024").exists()
