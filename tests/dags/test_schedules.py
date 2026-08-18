from core.schedules import SCHEDULES

CRON_ALIASES = ("@monthly", "@yearly", "@quarterly", "@weekly", "@daily", "@hourly", "@once")


def scheduled_dag_ids(all_dags):
    return {dag_id for dag_id, dag in all_dags.items() if dag.timetable.summary not in (None, "None")}


def test_every_scheduled_dag_is_registered(all_dags):
    assert scheduled_dag_ids(all_dags) == set(SCHEDULES)


def test_registry_matches_what_the_dags_declare(all_dags):
    mismatched = {
        dag_id: (all_dags[dag_id].timetable.summary, entry.cron)
        for dag_id, entry in SCHEDULES.items()
        if all_dags[dag_id].timetable.summary != entry.cron
    }
    assert not mismatched


def test_no_dag_file_declares_a_schedule_literal(dag_files):
    offenders = {
        path.name for path in dag_files if any(f'schedule="{alias}"' in path.read_text() for alias in CRON_ALIASES)
    }
    assert not offenders, f"aliases de cron ocultan colisiones: {offenders}"
