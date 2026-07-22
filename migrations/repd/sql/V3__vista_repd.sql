-- =======================================================================
-- V3: Vista analitica REPD -- resuelve catalogos y municipios
-- =======================================================================

CREATE OR REPLACE VIEW vw_repd AS
SELECT
    c.id,
    c.feb,
    s.nombre                        AS sexo,
    n.nombre                        AS nacionalidad,
    ar.nombre                       AS rango_edad,
    c.fecha_reporte,
    c.fecha_desaparicion,
    c.estado_desaparicion,
    md.nomgeo                       AS municipio_desaparicion,
    st.nombre                       AS estatus,
    c.fecha_localizacion,
    lc.nombre                       AS condicion_localizacion,
    lcl.nombre                      AS clasificacion_localizacion,
    c.estado_localizacion,
    ml.nomgeo                       AS municipio_localizacion,
    c.fecha_cierre,
    ct.nombre                       AS tipo_cierre,
    c.feb_vinculado,
    c.tiene_carpeta_investigacion,
    c.version_actual,
    c.fecha_creacion,
    c.fecha_actualizacion
FROM stg_repd_casos c
LEFT JOIN cat_sexo s                            ON c.sexo_id = s.id
LEFT JOIN cat_nacionalidad n                    ON c.nacionalidad_id = n.id
LEFT JOIN cat_rango_edad ar                     ON c.rango_edad_id = ar.id
LEFT JOIN cat_estatus st                        ON c.estatus_id = st.id
LEFT JOIN cat_condicion_localizacion lc         ON c.condicion_localizacion_id = lc.id
LEFT JOIN cat_clasificacion_localizacion lcl    ON c.clasificacion_localizacion_id = lcl.id
LEFT JOIN cat_tipo_cierre ct                    ON c.tipo_cierre_id = ct.id
LEFT JOIN cvegeo_municipalities md              ON c.municipio_desaparicion_id = md.id
LEFT JOIN cvegeo_municipalities ml              ON c.municipio_localizacion_id = ml.id;
