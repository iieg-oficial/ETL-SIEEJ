"""Static catalog values, seeded so the ids never shift between editions.

Only the three statuses the source actually publishes are seeded. The data
dictionary mentions a fourth case as "Cifras ajustadas y/o Cifras corregidas",
but that phrasing does not say whether the published label is one string or two,
and seeding a guessed spelling would create a junk catalog row that never
matches. An unforeseen status is upserted from the data instead.
"""

ESTATUS_SEED: list[str] = [
    "Cifras definitivas",
    "Cifras revisadas",
    "Cifras preliminares",
]
