"""Expande el registro a instantes de ejecución.

Usa croniter directo, que es el mismo parser que Airflow usa por dentro
(`airflow/timetables/_cron.py`), sin depender de que Airflow esté instalado.
"""

from datetime import datetime, timedelta

from croniter import croniter

from core.schedules.policy import SIMULATED_YEARS, Schedule
from core.schedules.registry import SCHEDULES

EPOCH = datetime(2026, 1, 1)


def upcoming_firings(
    start: datetime | None = None, years: int = SIMULATED_YEARS
) -> list[tuple[datetime, str, Schedule]]:
    """Ejecuciones de todos los DAGs registrados dentro de `years`, en orden cronológico."""
    start = start or EPOCH
    horizon = start + timedelta(days=round(365.25 * years))

    firings = []
    for dag_id, entry in SCHEDULES.items():
        schedule = croniter(entry.cron, start)
        while True:
            instant = schedule.get_next(datetime)
            if instant > horizon:
                break
            firings.append((instant, dag_id, entry))

    return sorted(firings, key=lambda firing: (firing[0], firing[1]))
