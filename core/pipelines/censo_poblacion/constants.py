RENAME_INEGI_2010_COL: dict[str, str] = {
    "entidad": "entidad_id",
    "nom_ent": "entidad",
    "mun": "municipio_id",
    "nom_mun": "municipio",
    "loc": "localidad_id",
    "nom_loc": "localidad",
    "pobtot": "total",
    "pobfem": "total_mujeres",
    "pobmas": "total_hombres",
    "tvivhab": "viviendas_habitadas",
}

RENAME_INEGI_2020_COL: dict[str, str] = {
    "ENTIDAD": "entidad_id",
    "NOM_ENT": "entidad",
    "MUN": "municipio_id",
    "NOM_MUN": "municipio",
    "LOC": "localidad_id",
    "NOM_LOC": "localidad",
    "POBTOT": "total",
    "POBFEM": "total_mujeres",
    "POBMAS": "total_hombres",
    "TVIVHAB": "viviendas_habitadas",
}


RENAME_INEGI_2015_COL: dict[str, str] = {
    "Entidad federativa": "entidad",
    "Municipio": "municipio",
    "Sexo": "sexo",
    "Población total": "total",
}

NULL_VALUES: list[str] = ["*"]

LOC_FILTER_VALUES: list[int] = [0, 9998, 9999]

NUMERIC_COLS: list[str] = ["total", "total_mujeres", "total_hombres", "viviendas_habitadas"]

POBLACION_COLS: list[str] = [
    "entidad_id",
    "municipio_id",
    "localidad_id",
    "fuente_id",
    "total",
    "total_mujeres",
    "total_hombres",
    "viviendas_habitadas",
]
