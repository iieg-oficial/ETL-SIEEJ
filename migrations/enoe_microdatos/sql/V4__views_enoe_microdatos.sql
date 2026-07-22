CREATE MATERIALIZED VIEW IF NOT EXISTS mv_enoe_microdatos AS
SELECT
    s.id,
    s.anio,
    s.trimestre,
    -- geografía
    st.nom_ent                          AS entidad,
    m.nomgeo                            AS municipio,
    s.ur,
    s.zona,
    -- sociodemográfico
    s.sex,
    s.eda,
    s.nac_anio,
    s.e_con,
    s.niv_ins,
    s.anios_esc,
    -- condición de actividad
    s.clase1,
    s.clase2,
    s.clase3,
    sec.descripcion                     AS sector,
    ocu.descripcion                     AS ocupacion,
    sit.descripcion                     AS situacion_trabajo,
    s.seg_soc,
    s.rama,
    s.scian,
    s.ing7c,
    s.dur9c,
    s.emple7c,
    -- horas e ingresos
    s.hrsocup,
    s.ingocup,
    s.ing_x_hrs,
    s.salario,
    -- tasas y complementos
    s.tpg_p8a,
    s.tcco,
    s.cp_anoc,
    s.imssissste,
    s.ma48me1sm,
    -- informalidad
    s.tue_ppal,
    s.emp_ppal,
    s.trans_ppal,
    s.sub_o,
    s.mh_fil2,
    s.mh_col,
    s.sec_ins,
    -- COE1/COE2
    s.p3b,
    s.p3i,
    s.p10b,
    -- indicadores derivados
    s.es_pea,
    s.es_ocupado,
    s.es_desocupado,
    s.es_informal,
    -- factor de expansión
    s.fac,
    s.fac_men
FROM stg_enoe_microdatos s
LEFT JOIN cvegeo_states         st  ON st.cve_ent = s.entidad_id
LEFT JOIN cvegeo_municipalities m   ON m.cve_ent  = s.entidad_id AND m.cve_mun = s.municipio_id
LEFT JOIN cat_enoe_sector       sec ON sec.id      = s.sector_id
LEFT JOIN cat_enoe_ocupacion    ocu ON ocu.id      = s.ocupacion_id
LEFT JOIN cat_enoe_situacion_trabajo sit ON sit.id = s.situacion_trabajo_id
WHERE s.entidad_id = 14;

CREATE UNIQUE INDEX IF NOT EXISTS uix_mv_enoe_microdatos_id
    ON mv_enoe_microdatos (id);
