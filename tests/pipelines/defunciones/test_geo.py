from core.utils import geo


def test_cvegeo_code_builds_five_digit_key():
    assert geo.cvegeo_code(14, 39) == 14039
    assert geo.cvegeo_code(1, 1) == 1001


def test_cvegeo_code_rejects_invalid_or_unknown():
    assert geo.cvegeo_code(None, 39) is None
    assert geo.cvegeo_code(14, None) is None
    assert geo.cvegeo_code("", "") is None
    assert geo.cvegeo_code(0, 0) is None
    assert geo.cvegeo_code(14, 999) == 14999


def test_resolve_municipio_ids_maps_each_role():
    mapping = {14039: 700, 9015: 250}
    roles = (
        ("ent_resid", "mun_resid", "municipio_resid_id"),
        ("ent_ocurr", "mun_ocurr", "municipio_ocurr_id"),
    )
    records = [
        {"ent_resid": 14, "mun_resid": 39, "ent_ocurr": 9, "mun_ocurr": 15},
        {"ent_resid": 14, "mun_resid": 999, "ent_ocurr": None, "mun_ocurr": 1},
    ]
    geo.resolve_municipio_ids(records, roles, mapping)

    assert records[0]["municipio_resid_id"] == 700
    assert records[0]["municipio_ocurr_id"] == 250
    assert records[1]["municipio_resid_id"] is None
    assert records[1]["municipio_ocurr_id"] is None
