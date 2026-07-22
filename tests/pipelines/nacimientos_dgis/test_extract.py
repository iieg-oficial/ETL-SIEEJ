import io
import zipfile

import pytest

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
    assert extract._extract_csv_bytes(archive, "flat") == b"a,b\n1,2\n"


def test_extract_csv_bytes_nested_edition(extract):
    """The 2025 edition wraps the CSV in a second zip."""
    inner = _zip({"Nacimientos_2025.csv": b"c,d\n3,4\n"})
    outer = _zip({"Registros de Nacimientos 2025/sinac_2025.zip": inner})
    assert extract._extract_csv_bytes(outer, "nested") == b"c,d\n3,4\n"


def test_extract_csv_bytes_missing_csv_raises_valueerror(extract):
    """A zip without a CSV fails loudly, not with a bare StopIteration."""
    archive = _zip({"readme.txt": b"nothing here"})
    with pytest.raises(ValueError, match="No CSV found"):
        extract._extract_csv_bytes(archive, "empty")
