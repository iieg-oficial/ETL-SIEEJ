CREATE OR REPLACE VIEW view_poblacion_mitad_anio AS
SELECT
    pma.id,
    m.nomgeo AS municipio,
    s.nom_ent AS entidad,
    cs.sexo,
    pma.anio,
    pma.pob_00_04,
    pma.pob_05_09,
    pma.pob_10_14,
    pma.pob_15_19,
    pma.pob_20_24,
    pma.pob_25_29,
    pma.pob_30_34,
    pma.pob_35_39,
    pma.pob_40_44,
    pma.pob_45_49,
    pma.pob_50_54,
    pma.pob_55_59,
    pma.pob_60_64,
    pma.pob_65_69,
    pma.pob_70_74,
    pma.pob_75_79,
    pma.pob_80_84,
    pma.pob_85_mm,
    pma.pob_total,
    pma.fecha_actualizacion
FROM stg_poblacion_mitad_anio pma
LEFT JOIN cvegeo_municipalities m ON m.cvegeo = pma.municipio_id
LEFT JOIN cvegeo_states s ON s.cve_ent = pma.entidad_id
LEFT JOIN cat_sexo cs ON cs.id = pma.sexo_id
WHERE m.cve_ent = 14;

CREATE OR REPLACE VIEW view_grandes_grupos_edad AS
SELECT
    gge.id,
    m.nomgeo AS municipio,
    s.nom_ent AS entidad,
    cs.sexo,
    gge.anio,
    gge.pob_00_11,
    gge.pob_12_29,
    gge.pob_30_59,
    gge.pob_60_mm,
    gge.pob_total,
    gge.fecha_actualizacion
FROM stg_grandes_grupos_edad gge
LEFT JOIN cvegeo_municipalities m ON m.cvegeo = gge.municipio_id
LEFT JOIN cvegeo_states s ON s.cve_ent = gge.entidad_id
LEFT JOIN cat_sexo cs ON cs.id = gge.sexo_id
WHERE m.cve_ent = 14;

CREATE OR REPLACE VIEW view_indicadores_demograficos AS
SELECT
    idd.id,
    m.nomgeo AS municipio,
    s.nom_ent AS entidad,
    idd.anio,
    idd.hom_mit_ano,
    idd.muj_mit_ano,
    idd.pob_mit_mun,
    idd.muj_00_14,
    idd.hom_00_14,
    idd.pob_00_14,
    idd.muj_15_64,
    idd.hom_15_64,
    idd.pob_15_64,
    idd.muj_60_mas,
    idd.hom_60_mas,
    idd.pob_60_mas,
    idd.muj_65_mas,
    idd.hom_65_mas,
    idd.pob_65_mas,
    idd.pob_mit_ent,
    idd.edad_med,
    idd.por_mun,
    idd.ind_env_60,
    idd.ind_env_65,
    idd.rhm,
    idd.raz_dep_adu,
    idd.raz_dep_inf,
    idd.raz_dep,
    idd.fecha_actualizacion
FROM stg_indicadores_demograficos idd
LEFT JOIN cvegeo_municipalities m ON m.cvegeo = idd.municipio_id
LEFT JOIN cvegeo_states s ON s.cve_ent = idd.entidad_id
WHERE m.cve_ent = 14;
