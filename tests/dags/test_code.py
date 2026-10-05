"""El DAG separa los stages en tareas para poder reintentar una sola."""

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
