"""El DAG separa los stages en tareas para poder reintentar una sola."""

DAG_ID = "etl_secretaria_educacion_bootstrap"


def test_el_dag_existe(all_dags):
    assert DAG_ID in all_dags


def test_declara_una_tarea_por_stage(all_dags):
    tareas = {task.task_id for task in all_dags[DAG_ID].tasks}

    assert tareas == {"extract", "transform", "load"}


def test_los_stages_van_encadenados_en_orden(all_dags):
    dag = all_dags[DAG_ID]

    assert [t.task_id for t in dag.get_task("extract").downstream_list] == ["transform"]
    assert [t.task_id for t in dag.get_task("transform").downstream_list] == ["load"]
    assert dag.get_task("load").downstream_list == []


def test_no_corre_solo_ni_recupera_ejecuciones_pasadas(all_dags):
    # Se dispara a mano: la dependencia sube datos sin calendario fijo.
    dag = all_dags[DAG_ID]

    assert dag.timetable.summary in (None, "None")
    assert dag.catchup is False


def test_es_un_pipeline_liviano_y_no_toma_el_pool_pesado(all_dags):
    # No está en HEAVY_PIPELINES, así que no debe competir por el semáforo.
    assert all(task.pool == "default_pool" for task in all_dags[DAG_ID].tasks)
