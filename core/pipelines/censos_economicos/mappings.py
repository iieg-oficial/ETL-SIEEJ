from datetime import date

CENSO_METADATA: dict[int, dict] = {
    2019: {
        "anio": 2019,
        "descripcion": "Censos Economicos 2019",
        "fecha_publicacion": date(2020, 12, 15),
    },
    2024: {
        "anio": 2024,
        "descripcion": "Censos Economicos 2024",
        "fecha_publicacion": date(2025, 7, 24),
    },
}

CLASIFICADOR_CODIGO_MAP: dict[int, str] = {
    1: "Gran sector",
    2: "Sector",
    3: "Subsector",
    4: "Rama",
    5: "Subrama",
    6: "Clase",
}
