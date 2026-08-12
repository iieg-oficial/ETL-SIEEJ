"""Static catalog values, seeded so the ids never shift between editions.

The edition published today only carries two of the three statuses the data
dictionary documents. The third is seeded anyway, in a fixed order, so the ids
that stg_enec_nacional and stg_enec_entidad already reference do not shift the
first time INEGI revises a period.
"""

ESTATUS_SEED: list[str] = [
    "Cifras definitivas",
    "Cifras revisadas",
    "Cifras preliminares",
]
