CREATE OR REPLACE VIEW view_marginacion_municipal AS
SELECT
    mm.id,
    m.nomgeo                            AS municipio,
    gm.grado_marginacion,
    mm.pob_total,
    mm.porc_pob15_analfabeta,
    mm.pob15_sin_educ_bas,
    mm.porc_viv_sin_drenaje_ni_excusado,
    mm.porc_viv_sin_energia,
    mm.porc_viv_sin_agua_entubada,
    mm.porc_viv_piso_tierra,
    mm.prom_ocup_por_cuarto,
    mm.porc_pob_loc_menos5000_hab,
    mm.pob_ocup_hasta_2_sal_min,
    mm.indice_marginacion,
    mm.indice_marginacion_normalizado,
    mm.fecha_actualizacion
FROM marginaciones_municipales mm
LEFT JOIN cvegeo_municipalities m  ON m.cvegeo = mm.municipio_id
LEFT JOIN grados_marginacion gm    ON gm.id    = mm.grado_marginacion_id
WHERE m.cve_ent = 14;

CREATE OR REPLACE VIEW view_marginacion_localidades AS
SELECT
    ml.id,
    l.localidad,
    m.nomgeo                             AS municipio,
    gm.grado_marginacion,
    ml.pob_total,
    ml.porc_pob15_analfabeta,
    ml.porc_pob15_sin_educ_basica,
    ml.porc_viv_sin_drenaje_ni_excusado,
    ml.porc_viv_sin_energia,
    ml.porc_viv_sin_agua_entubada,
    ml.porc_viv_piso_tierra,
    ml.prom_ocup_por_cuarto,
    ml.porc_viv_sin_refrigerador,
    ml.indice_marginacion,
    ml.indice_marginacion_normalizado,
    ml.fecha_actualizacion
FROM marginaciones_localidades ml
LEFT JOIN localidades l            ON l.id     = ml.localidad_id
LEFT JOIN cvegeo_municipalities m  ON m.cvegeo = l.municipio_id
LEFT JOIN grados_marginacion gm    ON gm.id    = ml.grado_marginacion_id;
