"""El DAG separa los stages en tareas para poder reintentar una sola."""

import pytest

BOOTSTRAP_ID = "etl_code_bootstrap"
UPDATE_ID = "etl_code_update"


def test_los_dags_existen(all_dags):
    assert {BOOTSTRAP_ID, UPDATE_ID} <= set(all_dags)


def test_declara_una_tarea_por_stage(all_dags):
    for dag_id in (BOOTSTRAP_ID, UPDATE_ID):
        assert {task.task_id for task in all_dags[dag_id].tasks} == {"extract", "transform", "load"}


def test_los_stages_van_encadenados_en_orden(all_dags):
    dag = all_dags[BOOTSTRAP_ID]

    assert [t.task_id for t in dag.get_task("extract").downstream_list] == ["transform"]
    assert [t.task_id for t in dag.get_task("transform").downstream_list] == ["load"]
    assert dag.get_task("load").downstream_list == []


def test_el_bootstrap_se_dispara_a_mano(all_dags):
    dag = all_dags[BOOTSTRAP_ID]

    assert dag.timetable.summary in (None, "None")
    assert dag.catchup is False


def test_el_update_corre_con_el_calendario_del_registro(all_dags):
    from core.schedules import SCHEDULES

    assert all_dags[UPDATE_ID].timetable.summary == SCHEDULES[UPDATE_ID].cron


def test_es_un_pipeline_liviano_y_no_toma_el_pool_pesado(all_dags):
    assert all(task.pool == "default_pool" for dag_id in (BOOTSTRAP_ID, UPDATE_ID) for task in all_dags[dag_id].tasks)


class _Consulta:
    """Query falso: registra el valor con que se filtra por conjunto."""

    def __init__(self, ultimos, etags):
        self.ultimos, self.etags, self.conjunto = ultimos, etags, None

    def filter(self, criterio):
        self.conjunto = criterio.right.value
        return self

    def scalar(self):
        return self.ultimos.get(self.conjunto)

    def all(self):
        return [(etag,) for etag in self.etags]


class _Sesion:
    def __init__(self, ultimos, etags):
        self.ultimos, self.etags = ultimos, etags

    def query(self, *columnas):
        return _Consulta(self.ultimos, self.etags)


def _watermark(monkeypatch, ultimos, etags=()):
    from contextlib import contextmanager
    import importlib

    class _Db:
        def __init__(self, *args):
            self.cerrada = False

        def connect(self):
            pass

        def disconnect(self):
            self.cerrada = True

        @contextmanager
        def get_session(self):
            yield _Sesion(ultimos, etags)

    monkeypatch.setattr("core.db.Database", _Db)
    return importlib.import_module("dags.etl_code").get_watermark()


def test_el_watermark_es_por_conjunto(monkeypatch):
    from core.pipelines.code.datasets import BY_KEY

    since, _ = _watermark(monkeypatch, {BY_KEY["reto"].label: "2026-10-27 17:42:03+00:00"})

    assert since == {"reto": "2026-10-27 17:42:03+00:00"}


def test_un_conjunto_sin_cargas_no_tiene_watermark(monkeypatch):
    since, _ = _watermark(monkeypatch, {})

    assert since == {}


def test_cada_conjunto_toma_su_propio_corte(monkeypatch):
    from core.pipelines.code.datasets import BY_KEY

    ultimos = {BY_KEY["reto"].label: "2026-10-27", BY_KEY["academias"].label: "2026-10-22"}

    since, _ = _watermark(monkeypatch, ultimos)

    assert since == {"reto": "2026-10-27", "academias": "2026-10-22"}


def test_el_watermark_devuelve_solo_los_etags_con_valor(monkeypatch):
    _, etags = _watermark(monkeypatch, {}, etags=["a", None, "", "b"])

    assert etags == ["a", "b"]


def test_el_update_pasa_el_corte_por_conjunto_al_extract(monkeypatch):
    import importlib

    dag = importlib.import_module("dags.etl_code")
    capturado = {}

    class _Extract:
        def __init__(self, mode, since, processed_etags):
            capturado.update(mode=mode, since=since, etags=processed_etags)

        def execute(self):
            pass

    monkeypatch.setattr(dag, "get_watermark", lambda: ({"reto": "2026-10-27"}, ["e1"]))
    monkeypatch.setattr("core.pipelines.code.stages.extract.CodeExtract", _Extract)

    dag.run_extract("update")

    assert capturado == {"mode": "update", "since": {"reto": "2026-10-27"}, "etags": ["e1"]}


def test_el_bootstrap_no_consulta_el_watermark(monkeypatch):
    import importlib

    dag = importlib.import_module("dags.etl_code")
    capturado = {}

    class _Extract:
        def __init__(self, mode, since, processed_etags):
            capturado.update(since=since, etags=processed_etags)

        def execute(self):
            pass

    monkeypatch.setattr(dag, "get_watermark", lambda: pytest.fail("no debe consultar la base"))
    monkeypatch.setattr("core.pipelines.code.stages.extract.CodeExtract", _Extract)

    dag.run_extract("bootstrap")

    assert capturado == {"since": {}, "etags": ()}
