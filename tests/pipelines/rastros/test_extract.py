import pytest

from core.pipelines.rastros.constants import RENAME_HEADER
from core.pipelines.rastros.stages.extract import RastrosExtract


@pytest.fixture
def extract() -> RastrosExtract:
    return RastrosExtract()


def test_concatenates_every_yearly_csv(extract, make_dataset_zip, csv_row):
    archive = make_dataset_zip(
        {
            "2024": [csv_row(anio="2024"), csv_row(anio="2024", especie="Ganado ovino")],
            "2025": [csv_row(anio="2025")],
        }
    )

    df = extract.action(archive)

    assert len(df) == 3
    assert set(df["anio"]) == {"2024", "2025"}


def test_keeps_only_the_renamed_columns(extract, make_dataset_zip):
    df = extract.action(make_dataset_zip())

    assert list(df.columns) == list(RENAME_HEADER.values())


def test_years_are_discovered_not_hardcoded(extract, make_dataset_zip, csv_row):
    """A future edition must flow through without touching the code."""
    df = extract.action(make_dataset_zip({"2031": [csv_row(anio="2031")]}))

    assert df["anio"].tolist() == ["2031"]


def test_zip_without_dataset_csv_raises(extract, make_zip):
    archive = make_zip({"metadatos/metadatos.txt": b"solo metadatos"})

    with pytest.raises(FileNotFoundError, match="esgrm_mensual_tr_cifra"):
        extract.action(archive)


def test_ignores_files_outside_the_dataset_folder(extract, make_zip, csv_row, csv_header, dataset_dir):
    """Only conjunto_de_datos/ holds data; the bitacora sits next to it."""
    archive = make_zip(
        {
            f"{dataset_dir}/esgrm_mensual_tr_cifra_2026.csv": "\n".join([csv_header, csv_row()]).encode("latin-1"),
            f"{dataset_dir}/bitacora_de_cambios_esgrm_mensual_tr_cifra_2019.csv": b"otra,cosa\n1,2\n",
            "catalogos/tc_entidad.csv": b"CVE_ENT,NOM_ENT\n14,Jalisco\n",
        }
    )

    df = extract.action(archive)

    assert len(df) == 1


def test_missing_source_column_fails_loudly(extract, make_zip, csv_header, dataset_dir):
    """A silent rename upstream must not produce a half-empty DataFrame."""
    header = csv_header.replace(",VALOR_PRODUCCION", ",VALOR_PROD")
    archive = make_zip({f"{dataset_dir}/esgrm_mensual_tr_cifra_2026.csv": f"{header}\n".encode("latin-1")})

    with pytest.raises(ValueError, match="VALOR_PRODUCCION"):
        extract.action(archive)
