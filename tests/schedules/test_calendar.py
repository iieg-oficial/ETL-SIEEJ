from datetime import timedelta

from core.schedules import MIN_SEPARATION_MINUTES, SCHEDULES, upcoming_firings


def test_registry_uses_explicit_crons():
    offenders = {dag_id for dag_id, entry in SCHEDULES.items() if entry.cron.startswith("@")}
    assert not offenders


def test_no_two_dags_fire_within_the_separation_window():
    firings = upcoming_firings()
    minimum = timedelta(minutes=MIN_SEPARATION_MINUTES)

    collisions = [
        (str(before[0]), before[1], str(after[0]), after[1])
        for before, after in zip(firings, firings[1:])
        if after[0] - before[0] < minimum
    ]

    assert not collisions, (
        f"disparos a menos de {MIN_SEPARATION_MINUTES} min: {collisions[:5]} "
        "— reasigna el horario en core/schedules/registry.py (ver `just schedules`)"
    )
