"""Rinde el calendario de DAGs ordenado por fecha de ejecución (`just schedules`)."""

import sys
from datetime import UTC, datetime, timedelta

from core.schedules import MIN_SEPARATION_MINUTES, upcoming_firings

HEADER = f"{'SE EJECUTA (UTC)':<22}{'DAG':<40}{'FRECUENCIA':<34}CARGA"
LEGEND = (
    "pesado = corre en el pool heavy_pipeline: nunca coincide con otro pesado y cede\n"
    "         el paso a los livianos en cola. Ver docs/airflow.md."
)


def main(days: int) -> int:
    now = datetime.now(UTC)
    horizon = now + timedelta(days=days)
    firings = [f for f in upcoming_firings(start=now, years=days // 365 + 1) if f[0] <= horizon]

    print(f"Calendario de DAGs — próximos {days} días, {len(firings)} ejecuciones\n")
    print("Airflow ejecuta al CIERRE del período: el DAG que corre el 1 de octubre")
    print("procesa septiembre. Horas en UTC.\n")
    print(HEADER)
    print("-" * len(HEADER))

    previous = None
    collisions = 0
    for instant, dag_id, entry in firings:
        carga = "pesado" if entry.pool != "default_pool" else "liviano"
        aviso = ""
        if previous is not None:
            minutes = (instant - previous).total_seconds() / 60
            if minutes < MIN_SEPARATION_MINUTES:
                aviso = f"  <-- solo {minutes:.0f} min despues de la anterior"
                collisions += 1
        print(f"{instant:%Y-%m-%d %H:%M}      {dag_id:<40}{entry.frequency:<34}{carga}{aviso}")
        previous = instant

    print(f"\n{LEGEND}\n")
    if collisions:
        print(f"{collisions} ejecuciones a menos de {MIN_SEPARATION_MINUTES} min de la anterior.")
        return 1

    print(f"Ninguna ejecución a menos de {MIN_SEPARATION_MINUTES} min de otra.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 90))
