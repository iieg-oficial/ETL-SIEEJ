RENAME_IIM_MUNICIPAL_2010: dict[str, str] = {
    "cve_ent": "entidad_id",
    "cve_mun": "municipio_id",
    "tot_viv": "viv_totales",
    "viv_rem": "por_viv_remesas",
    "viv_emig": "por_viv_emigrantes",
    "viv_circ": "por_viv_circ",
    "viv_ret": "por_viv_reto",
    "iaim": "iaim",
    "gaim": "gaim",
    "pos_nal": "lugar_contexto_nacional",
}

RENAME_IIM_MUNICIPAL_2020: dict[str, str] = {
    "cve_mun": "municipio_id",
    "viv_tot": "viv_totales",
    "viv_rem": "por_viv_remesas",
    "viv_emig": "por_viv_emigrantes",
    "viv_circ": "por_viv_circ",
    "viv_ret": "por_viv_reto",
    "iim_dp2": "iim_dp2",
    "gim_dp2": "gim_dp2",
    "pos_nal": "lugar_contexto_nacional",
}

RENAME_IIM_ESTATAL_2020: dict[str, str] = {
    "cve_ent": "entidad_id",
    "viv_tot": "viv_totales",
    "viv_rem": "por_viv_remesas",
    "viv_emig": "por_viv_emigrantes",
    "viv_circ": "por_viv_circ",
    "viv_ret": "por_viv_reto",
    "iim_dp2": "iim_dp2",
    "gim_dp2": "gim_dp2",
    "pos_nal": "lugar_contexto_nacional",
}

MUNICIPAL_COLS: list[str] = [
    "municipio_id",
    "viv_totales",
    "por_viv_remesas",
    "por_viv_emigrantes",
    "por_viv_circ",
    "por_viv_reto",
    "iaim",
    "gaim",
    "iim_dp2",
    "gim_dp2",
    "lugar_contexto_nacional",
    "fecha",
]

ESTATAL_COLS: list[str] = [
    "entidad_id",
    "viv_totales",
    "por_viv_remesas",
    "por_viv_emigrantes",
    "por_viv_circ",
    "por_viv_reto",
    "iim_dp2",
    "gim_dp2",
    "lugar_contexto_nacional",
    "fecha",
]
