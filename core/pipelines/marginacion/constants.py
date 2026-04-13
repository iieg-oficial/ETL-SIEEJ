from typing import Final, List


def rename_municipal(year: int) -> dict[str, str]:
    return {
        "CVE_ENT": "entidad_id",
        "NOM_ENT": "entidad",
        "CVE_MUN": "municipio_id",
        "NOM_MUN": "municipio",
        "POB_TOT": "pob_total",
        "ANALF": "porc_pob15_analfabeta",
        "SBASC": "pob15_sin_educ_bas",
        "OVSDE": "porc_viv_sin_drenaje_ni_excusado",
        "OVSEE": "porc_viv_sin_energia",
        "OVSAE": "porc_viv_sin_agua_entubada",
        "OVPT": "porc_viv_piso_tierra",
        "VHAC": "prom_ocup_por_cuarto",
        "PL.5000": "porc_pob_loc_menos5000_hab",
        "PO2SM": "pob_ocup_hasta_2_sal_min",
        f"IM_{year}": "indice_marginacion",
        f"GM_{year}": "grado_marginacion",
        f"IMN_{year}": "indice_marginacion_normalizado",
    }


def rename_localidad(year: int) -> dict[str, str]:
    return {
        "CVE_LOC": "cve_geo_id",
        "ENT": "entidad_id",
        "NOM_ENT": "entidad",
        "MUN": "municipio_id",
        "NOM_MUN": "municipio",
        "LOC": "clave_localidad",
        "NOM_LOC": "localidad",
        "POB_TOT": "pob_total",
        "ANALF": "porc_pob15_analfabeta",
        "SBASC": "porc_pob15_sin_educ_basica",
        "OVSDE": "porc_viv_sin_drenaje_ni_excusado",
        "OVSEE": "porc_viv_sin_energia",
        "OVSAE": "porc_viv_sin_agua_entubada",
        "OVPT": "porc_viv_piso_tierra",
        "OVHAC": "prom_ocup_por_cuarto",
        "OVSREF": "porc_viv_sin_refrigerador",
        f"IM_{year}": "indice_marginacion",
        f"GM_{year}": "grado_marginacion",
        f"IMN_{year}": "indice_marginacion_normalizado",
    }


NULL_VALUES: Final[List[str]] = ["n.a.", "n/a", "na", "null", ""]

TITLE_COLS: Final[List[str]] = ["entidad", "municipio", "localidad"]
