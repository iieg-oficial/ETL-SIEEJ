from datetime import date

from core.pipelines.censos_economicos.schemas import (
    StgEconomicoEstatal2019,
    StgEconomicoEstatal2024,
    StgEconomicoMunicipal2019,
    StgEconomicoMunicipal2024,
    StgEconomicoNacional2019,
    StgEconomicoNacional2024,
)

CENSO_METADATA: dict[int, dict] = {
    2019: {
        "anio": 2019,
        "descripcion": "Censos Economicos 2019",
        "fecha_publicacion": date(2020, 12, 15),
        "fuente": "INEGI",
    },
    2024: {
        "anio": 2024,
        "descripcion": "Censos Economicos 2024",
        "fecha_publicacion": date(2025, 7, 24),
        "fuente": "INEGI",
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

CAT_ESTRATOS: list[dict] = [
    {"id": 1, "codigo": None, "descripcion": "Suma de estratos"},
    {"id": 2, "codigo": 1, "descripcion": "0 a 10"},
    {"id": 3, "codigo": 2, "descripcion": "11 a 50"},
    {"id": 4, "codigo": 3, "descripcion": "51 a 250"},
    {"id": 5, "codigo": 4, "descripcion": "251 y más"},
    {"id": 6, "codigo": 99, "descripcion": "Agrupados por confidencialidad"},
]

ESTRATOS_CODIGO_MAP: dict = {
    None: 1,
    1: 2,
    2: 3,
    3: 4,
    4: 5,
    99: 6,
}

STG_MODEL_MAP: dict[int, dict[str, type]] = {
    2019: {
        "nacional": StgEconomicoNacional2019,
        "estatal": StgEconomicoEstatal2019,
        "municipal": StgEconomicoMunicipal2019,
    },
    2024: {
        "nacional": StgEconomicoNacional2024,
        "estatal": StgEconomicoEstatal2024,
        "municipal": StgEconomicoMunicipal2024,
    },
}
