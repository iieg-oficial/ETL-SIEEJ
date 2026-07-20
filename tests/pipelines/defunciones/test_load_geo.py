import logging

from core.pipelines.defunciones.stages.load import DefuncionesLoad

# Real rows from entidad_municipio_localidad_2022.csv (DGIS), including every sentinel level.
CATALOG_2022 = {
    (140000000, 1): 10,
    (140390000, 1): 11,
    (140390001, 1): 12,
    (880000000, 1): 20,
    (888880000, 1): 21,
    (888888888, 1): 22,
    (990000000, 1): 30,
    (999990000, 1): 31,
    (999999999, 1): 32,
}
LABELS = {
    10: "Jalisco",
    11: "Guadalajara",
    12: "Guadalajara",
    20: "Entidad no aplica para A00 - R99 Y V90 - Y89",
    21: "Municipio no aplica para A00 - R99 Y V90 - Y89",
    22: "Localidad no aplica",
    30: "Entidad no especificada",
    31: "Municipio no especificado",
    32: "Localidad no especificada",
}


class _FakeSession:
    def __init__(self, edicion_rows, localidad_rows):
        self._results = [edicion_rows, localidad_rows]

    def execute(self, _statement):
        return self._results.pop(0)


def _resolve(records):
    load = object.__new__(DefuncionesLoad)
    load.logger = logging.getLogger("test")
    edicion_rows = [(2022, 1)]
    localidad_rows = [(codigo, eid, sid) for (codigo, eid), sid in CATALOG_2022.items()]
    load._resolve_localidades(_FakeSession(edicion_rows, localidad_rows), records)
    return records


def _record(ent, mun, loc):
    return {
        "anio_registro_id": 2022,
        "entidad_ocules": ent,
        "municipio_ocules": mun,
        "localidad_ocules_id": loc,
    }


def test_no_aplica_sentinels_resolve_to_their_labels():
    record = _resolve([_record(88, 888, 8888)])[0]

    assert LABELS[record["entidad_ocules_id"]] == "Entidad no aplica para A00 - R99 Y V90 - Y89"
    assert LABELS[record["municipio_ocules_id"]] == "Municipio no aplica para A00 - R99 Y V90 - Y89"
    assert LABELS[record["localidad_ocules_id"]] == "Localidad no aplica"


def test_no_especificado_sentinels_resolve_to_their_labels():
    record = _resolve([_record(99, 999, 9999)])[0]

    assert LABELS[record["entidad_ocules_id"]] == "Entidad no especificada"
    assert LABELS[record["municipio_ocules_id"]] == "Municipio no especificado"
    assert LABELS[record["localidad_ocules_id"]] == "Localidad no especificada"


def test_real_geography_resolves_every_level():
    record = _resolve([_record(14, 39, 1)])[0]

    assert LABELS[record["entidad_ocules_id"]] == "Jalisco"
    assert LABELS[record["municipio_ocules_id"]] == "Guadalajara"
    assert LABELS[record["localidad_ocules_id"]] == "Guadalajara"


def test_unresolved_localidad_does_not_drag_down_entidad_and_municipio():
    # (14, 039, 9999) has no row in the real catalog, but Jalisco and Guadalajara must still resolve.
    record = _resolve([_record(14, 39, 9999)])[0]

    assert LABELS[record["entidad_ocules_id"]] == "Jalisco"
    assert LABELS[record["municipio_ocules_id"]] == "Guadalajara"
    assert record["localidad_ocules_id"] is None


def test_all_four_roles_resolve_independently():
    record = {
        "anio_registro_id": 2022,
        "entidad_registro": 14,
        "municipio_regis": 39,
        "localidad_regis_id": 1,
        "entidad_resid": 14,
        "municipio_resid": 39,
        "localidad_resid_id": 1,
        "entidad_ocurr": 99,
        "municipio_ocurr": 999,
        "localidad_ocurr_id": 9999,
        "entidad_ocules": 88,
        "municipio_ocules": 888,
        "localidad_ocules_id": 8888,
    }
    _resolve([record])

    assert LABELS[record["entidad_registro_id"]] == "Jalisco"
    assert LABELS[record["municipio_regis_id"]] == "Guadalajara"
    assert LABELS[record["entidad_resid_id"]] == "Jalisco"
    assert LABELS[record["municipio_resid_id"]] == "Guadalajara"
    assert LABELS[record["entidad_ocurr_id"]] == "Entidad no especificada"
    assert LABELS[record["municipio_ocurr_id"]] == "Municipio no especificado"
    assert LABELS[record["entidad_ocules_id"]] == "Entidad no aplica para A00 - R99 Y V90 - Y89"
    assert LABELS[record["municipio_ocules_id"]] == "Municipio no aplica para A00 - R99 Y V90 - Y89"


def test_missing_raw_codes_leave_fks_null():
    record = _resolve([_record(None, None, None)])[0]

    assert record["entidad_ocules_id"] is None
    assert record["municipio_ocules_id"] is None
    assert record["localidad_ocules_id"] is None
