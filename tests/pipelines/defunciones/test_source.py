import pytest

from core.pipelines.defunciones.helpers import source


CAT_1998 = ',\n,\n"CLAVE","DESCRIP"\n"1001","1 Hora"\n"4998","Años no especificados"\n'.encode("latin-1")
CAT_2014 = "CVE,DESCRIP\n1001,Una hora   \n4998,Edad no especificada\n".encode("utf-8-sig")
CAT_2014_TABS = b'CVE,DESCRIP\n"1001\t","Una hora"\n'


def test_read_catalog_csv_1998_skips_junk_rows_and_quotes():
    df = source.read_catalog_csv(CAT_1998)
    assert list(df.columns) == ["clave", "descripcion"]
    assert df.iloc[0].tolist() == ["1001", "1 Hora"]
    assert df.iloc[-1]["clave"] == "4998"


def test_read_catalog_csv_2014_handles_bom_cve_and_padding():
    df = source.read_catalog_csv(CAT_2014)
    assert df.iloc[0].tolist() == ["1001", "Una hora"]


def test_read_catalog_csv_strips_embedded_tabs():
    df = source.read_catalog_csv(CAT_2014_TABS)
    assert df.iloc[0]["clave"] == "1001"


def test_find_catalog_csv_excludes_siblings(make_zip):
    zip_bytes = make_zip(
        {
            "edad.csv": b"CVE,DESCRIP\n1,x\n",
            "edad_agrupada.csv": b"CVE,DESCRIP\n1,x\n",
            "edadgest.csv": b"CVE,DESCRIP\n1,x\n",
        }
    )
    name, _ = source.find_catalog_csv(zip_bytes, keyword="edad", exclude=("agrup", "gest"))
    assert name == "edad.csv"


def test_find_catalog_csv_descends_nested_zip(make_zip):
    inner = make_zip({"Catalogos/edad.csv": b"CVE,DESCRIP\n1,x\n"})
    outer = make_zip({"CATALOGOS_DEFUN_2021.zip": inner})
    name, raw = source.find_catalog_csv(outer, keyword="edad", exclude=("agrup", "gest"))
    assert name.endswith("edad.csv")
    assert raw.startswith(b"CVE")


def test_find_catalog_csv_raises_on_ambiguous(make_zip):
    zip_bytes = make_zip({"edad.csv": b"a", "cat_edad.csv": b"b"})
    with pytest.raises(ValueError):
        source.find_catalog_csv(zip_bytes, keyword="edad")


def test_find_catalog_csv_raises_when_missing(make_zip):
    zip_bytes = make_zip({"sexo.csv": b"a"})
    with pytest.raises(FileNotFoundError):
        source.find_catalog_csv(zip_bytes, keyword="edad")


@pytest.mark.parametrize(
    "url,expected",
    [
        ("x/CATALOGOS_DEFUN_1998-1999.zip?v=1.1.1", 1999),
        ("x/CATALOGOS_DEFUN_2004-2011.zip?v=1.1.1", 2011),
        ("x/CATALOGOS_DEFUN_2024.zip?v=2025.12.22", 2024),
    ],
)
def test_edition_year(url, expected):
    assert source._edition_year(url) == expected


def test_read_registro_csv_lowercases_headers_and_keeps_text():
    raw = b"ENT_REGIS,SEXO\n01,1\n14,2\n"
    df = source.read_registro_csv(raw)
    assert list(df.columns) == ["ent_regis", "sexo"]
    assert df.iloc[0]["ent_regis"] == "01"


def test_find_registro_csv_picks_largest(make_zip):
    zip_bytes = make_zip({"diccionario.csv": b"a,b\n1,2\n", "datos.csv": b"x,y\n" + b"1,2\n" * 50})
    name, _ = source.find_registro_csv(zip_bytes)
    assert name == "datos.csv"


LOCALIDADES_2022 = (
    b"cve_ent,cve_mun,cve_loc,nom_loc\n"
    b'"01","000","0000","Aguascalientes"\n'
    b'"01","001","0001","Aguascalientes"\n'
    b'"88","999","9999","Localidad no especificada"\n'
    b'"99","999","7777","Cifra confidencial"\n'
)


def test_read_localidades_csv_parses_padded_hierarchy_and_sentinels():
    df = source.read_localidades_csv(LOCALIDADES_2022)
    assert list(df.columns) == ["cve_ent", "cve_mun", "cve_loc", "descripcion"]
    assert df.iloc[0].tolist() == ["01", "000", "0000", "Aguascalientes"]
    sentinel = df[df["cve_ent"] == "88"].iloc[0]
    assert sentinel["cve_mun"] == "999"
    assert sentinel["cve_loc"] == "9999"
    assert sentinel["descripcion"] == "Localidad no especificada"
