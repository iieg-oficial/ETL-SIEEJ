from typing import Final

FACT_DATASET: Final[str] = "stg_defunciones"

CAPITULO_GRUPO_DATASET: Final[str] = "cat_capitulo_grupo"
CAPITULO_GRUPO_KEYWORD: Final[str] = "capitulo"
CHAPTER_TOTAL_GPO: Final[int] = 0

EDICION_DATASET: Final[str] = "cat_edicion"

LOCALIDADES_DATASET: Final[str] = "cat_localidades"

VERSIONED_SOURCE_COLUMNS: Final[dict[str, str]] = {
    "ocupacion": "cat_ocupacion",
    "tipo_defun": "cat_presunta_defuncion_violenta",
    "derechohab": "cat_derecho_habiencia",
}

CODED_SOURCE_COLUMNS: Final[dict[str, str]] = {
    "causa_def": "cat_causa_defuncion",
    "cod_adicio": "cat_codigo_adicional",
    "lista_mex": "cat_lista_mexicana",
    "gr_lismex": "cat_grupo_lista_mexicana",
    "maternas": "cat_causa_defuncion",
    "gramos": "cat_peso_producto",
}

ENTIDAD_JALISCO: Final[int] = 14
JALISCO_FILTER_COLUMN: Final[str] = "ent_resid"

ANIO_COLUMN: Final[str] = "anio_registro_id"

GEO_ROLES: Final[tuple[tuple[str, str, str], ...]] = (
    ("entidad_resid", "municipio_resid", "cvegeo_resid_id"),
    ("entidad_ocurr", "municipio_ocurr", "cvegeo_ocurr_id"),
)

# (raw entidad, raw municipio, raw localidad / localidad FK target, entidad FK, municipio FK)
# Each level resolves from its OWN raw code against cat_localidades: the entidad level uses
# (ent, 0, 0) and the municipio level (ent, mun, 0). Deriving them from the localidad row's
# hierarchy would be wrong: (14, 039, 9999) has no row in the catalog while (14, 120, 9999) does,
# so an unresolved localidad would drag entidad and municipio down with it.
GEO_LEVEL_ROLES: Final[tuple[tuple[str, str, str, str, str], ...]] = (
    ("entidad_registro", "municipio_regis", "localidad_regis_id", "entidad_registro_id", "municipio_regis_id"),
    ("entidad_resid", "municipio_resid", "localidad_resid_id", "entidad_resid_id", "municipio_resid_id"),
    ("entidad_ocurr", "municipio_ocurr", "localidad_ocurr_id", "entidad_ocurr_id", "municipio_ocurr_id"),
    ("entidad_ocules", "municipio_ocules", "localidad_ocules_id", "entidad_ocules_id", "municipio_ocules_id"),
)

COLUMN_CATALOG: Final[dict[str, str]] = {
    "causa_def": "cat_causa_defuncion",
    "cod_adicio": "cat_codigo_adicional",
    "lista_mex": "cat_lista_mexicana",
    "sexo": "cat_sexo",
    "afromex": "cat_afromexicano",
    "conindig": "cat_condicion_indigena",
    "lengua": "cat_lengua_indigena",
    "cve_lengua": "cat_lenguas",
    "nacionalid": "cat_nacionalidad",
    "nacesp_cve": "cat_origen",
    "ent_nac": "cat_entidad_pais",
    "edad": "cat_edad",
    "sem_gest": "cat_edad_gestacional",
    "gramos": "cat_peso_producto",
    "dia_ocurr": "cat_dia",
    "mes_ocurr": "cat_mes",
    "anio_ocur": "cat_anio",
    "dia_regis": "cat_dia",
    "mes_regis": "cat_mes",
    "anio_regis": "cat_anio",
    "dia_nacim": "cat_dia",
    "mes_nacim": "cat_mes",
    "anio_nacim": "cat_anio",
    "cond_act": "cat_condicion_actividad",
    "ocupacion": "cat_ocupacion",
    "escolarida": "cat_escolaridad",
    "edo_civil": "cat_estado_civil",
    "tipo_defun": "cat_presunta_defuncion_violenta",
    "ocurr_trab": "cat_ocurrio_trabajo",
    "lugar_ocur": "cat_lugar_ocurrencia",
    "par_agre": "cat_parentesco_agresor",
    "vio_fami": "cat_violencia_familiar",
    "asist_medi": "cat_asistencia_medica",
    "cirugia": "cat_cirugia",
    "natviole": "cat_accidental_violenta",
    "necropsia": "cat_necropsia",
    "usonecrops": "cat_uso_necropsia",
    "encefalica": "cat_muerte_encefalica",
    "donador": "cat_donador",
    "sitio_ocur": "cat_sitio_ocurrencia",
    "cond_cert": "cat_certificante",
    "derechohab": "cat_derecho_habiencia",
    "embarazo": "cat_condicion_embarazo",
    "rel_emba": "cat_relacion_con_embarazo",
    "horas": "cat_hora",
    "minutos": "cat_minuto",
    "lista1": "cat_lista_cie",
    "gr_lismex": "cat_grupo_lista_mexicana",
    "area_ur": "cat_area_urbana_rural",
    "edad_agru": "cat_edad_agrupada",
    "complicaro": "cat_complicaron_embarazo",
    "dia_cert": "cat_dia",
    "mes_cert": "cat_mes",
    "anio_cert": "cat_anio",
    "maternas": "cat_causa_defuncion",
    "razon_m": "cat_razon_materna",
    "tloc_regis": "cat_tamano_localidad",
    "tloc_resid": "cat_tamano_localidad",
    "tloc_ocurr": "cat_tamano_localidad",
}

EDITION_COLUMN_ALIASES: Final[dict[str, str]] = {
    "presunto": "tipo_defun",
}

FK_COLUMN_OVERRIDES: Final[dict[str, str]] = {
    "lista1": "lista_cie_id",
    "nacesp_cve": "origen_id",
    "ent_nac": "entidad_pais_nac_id",
    "causa_def": "causa_defuncion_id",
    "cod_adicio": "cod_adicional_id",
    "conindig": "cond_indigena_id",
    "lengua": "lengua_indigena_id",
    "cve_lengua": "lenguas_id",
    "sem_gest": "edad_gestacional_id",
    "cond_act": "condicion_act_id",
    "escolarida": "escolaridad_id",
    "tipo_defun": "tipo_defuncion_id",
    "lugar_ocur": "lugar_ocurr_id",
    "par_agre": "parentesco_agre_id",
    "vio_fami": "violencia_familiar_id",
    "asist_medi": "asist_medica_id",
    "natviole": "accidental_vio_id",
    "usonecrops": "uso_necropsia_id",
    "cond_cert": "certificante_id",
    "derechohab": "derecho_hab_id",
    "area_ur": "area_urbana_id",
    "edad_agru": "edad_agrupada_id",
    "complicaro": "complicaron_id",
    "anio_nacim": "anio_nacimiento_id",
    "mes_nacim": "mes_nacimiento_id",
    "dia_nacim": "dia_nacimiento_id",
    "anio_regis": "anio_registro_id",
    "mes_regis": "mes_registro_id",
    "dia_regis": "dia_registro_id",
    "anio_ocur": "anio_ocurr_id",
    "dia_cert": "dia_certificacion_id",
    "mes_cert": "mes_certificacion_id",
    "anio_cert": "anio_certificacion_id",
    "tloc_regis": "tamanio_loc_regis_id",
    "tloc_resid": "tamanio_loc_resid_id",
    "tloc_ocurr": "tamanio_loc_ocurr_id",
}

CATALOG_FK_COLUMNS: Final[dict[str, str]] = {col: FK_COLUMN_OVERRIDES.get(col, f"{col}_id") for col in COLUMN_CATALOG}

GEO_COLUMN_RENAMES: Final[dict[str, str]] = {
    "ent_regis": "entidad_registro",
    "mun_regis": "municipio_regis",
    "ent_resid": "entidad_resid",
    "mun_resid": "municipio_resid",
    "ent_ocurr": "entidad_ocurr",
    "mun_ocurr": "municipio_ocurr",
    "ent_ocules": "entidad_ocules",
    "mun_ocules": "municipio_ocules",
}

LOCALIDAD_FK_COLUMNS: Final[dict[str, str]] = {
    "loc_regis": "localidad_regis_id",
    "loc_resid": "localidad_resid_id",
    "loc_ocurr": "localidad_ocurr_id",
    "loc_ocules": "localidad_ocules_id",
}

REGISTRO_RENAMES: Final[dict[str, str]] = {
    **CATALOG_FK_COLUMNS,
    **GEO_COLUMN_RENAMES,
    **LOCALIDAD_FK_COLUMNS,
}

ETL_MANAGED_COLUMNS: Final[frozenset[str]] = frozenset(
    {"id", "fecha_actualizacion", "capitulo_grupo_id", "cvegeo_resid_id", "cvegeo_ocurr_id"}
    | {ent_fk for *_, ent_fk, _ in GEO_LEVEL_ROLES}
    | {mun_fk for *_, mun_fk in GEO_LEVEL_ROLES}
)

TEXT_FACT_COLUMNS: Final[frozenset[str]] = frozenset(CATALOG_FK_COLUMNS[col] for col in CODED_SOURCE_COLUMNS)
