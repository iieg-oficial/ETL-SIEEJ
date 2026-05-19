RENAME_HEADER_BASE = {
    "Anio": "anio",
    "Cveestado": "entidad_id",
    "Nomestado": "entidad",
    "Cveddr": "distrito_des_rural_id",
    "Nomddr": "dis_des_rural",
    "Cvempio": "municipio_id",
    "Nommunicipio": "municipio",
    "Cveespecie": "especie_id",
    "Nomespecie": "especie",
    "Cveproducto": "producto_id",
    "Nomproducto": "producto",
    "Volumen": "volumen_produccion",
    "Peso": "peso_sacrificio",
    "Precio": "precio_med_rural",
    "Valor": "valor_produccion",
    "Asacrificado": "animales_sacrificados",
}

NULL_VALUES = [
    "no especificado",
    "sin información",
    "sin informacion",
    "sin información",
    "*",
    "****",
    "---",
    "n/a",
    "na",
    "nan",
    "null",
    "ninguno",
    "sin dato",
    "nd",
    "s/d",
    "s/n",
    "ne",
]

FLOAT_COLS = [
    "volumen_produccion",
    "peso_sacrificio",
    "precio_med_rural",
    "valor_produccion",
    "animales_sacrificados",
]

TITLE_COLS = [
    "especie",
    "producto",
    "municipio",
    "entidad",
    "dis_des_rural",
]

RENAME_HEADER_NO_GEO = {
    k: v for k, v in RENAME_HEADER_BASE.items() if k not in {"Cveddr", "Nomddr", "Cvempio", "Nommunicipio"}
}
