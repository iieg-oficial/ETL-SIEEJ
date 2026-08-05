"""Static catalog values that the source does not always publish.

ESTATUS only ships the statuses present in the current edition ("Cifras
definitivas" and "Cifras preliminares" today). The data dictionary declares a
third one, "Cifras revisadas", which appears when INEGI revises a period. The
catalog is seeded with the three so a revision does not shift the ids that
stg_emec already references, and any unforeseen value is still upserted.
"""

ESTATUS_SEED: list[str] = [
    "Cifras definitivas",
    "Cifras revisadas",
    "Cifras preliminares",
]
