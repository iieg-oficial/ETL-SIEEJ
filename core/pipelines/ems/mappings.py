"""Static catalog values, seeded so the ids never shift between editions.

Unlike EMEC, EMS already publishes the three statuses today. They are still
seeded in a fixed order rather than derived from the data: which statuses appear
depends on the edition, and letting the order float would renumber the ids that
stg_ems already references the first time a status stops being published.
"""

ESTATUS_SEED: list[str] = [
    "Cifras definitivas",
    "Cifras revisadas",
    "Cifras preliminares",
]
