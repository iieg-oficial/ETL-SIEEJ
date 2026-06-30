from datetime import date

from core.pipelines.censos_economicos.schemas import (
    StgEconomicoEstatal2018,
    StgEconomicoEstatal2023,
    StgEconomicoMunicipal2018,
    StgEconomicoMunicipal2023,
    StgEconomicoNacional2018,
    StgEconomicoNacional2023,
)

CENSO_METADATA: dict[int, dict] = {
    2018: {
        "anio": 2018,
        "descripcion": "Censos Economicos 2019 (datos 2018)",
        "fecha_publicacion": date(2020, 12, 15),
        "fuente": "INEGI",
    },
    2023: {
        "anio": 2023,
        "descripcion": "Censos Economicos 2024 (datos 2023)",
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
    2018: {
        "nacional": StgEconomicoNacional2018,
        "estatal": StgEconomicoEstatal2018,
        "municipal": StgEconomicoMunicipal2018,
    },
    2023: {
        "nacional": StgEconomicoNacional2023,
        "estatal": StgEconomicoEstatal2023,
        "municipal": StgEconomicoMunicipal2023,
    },
}
