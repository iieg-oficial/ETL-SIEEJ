CREATE OR REPLACE VIEW view_agricola_jalisco AS
SELECT
    sa.id,
    sa.anio,
    m.nomgeo                        AS municipio,
    s.nom_ent                       AS entidad,
    ddr.dis_des_rural,
    cadr.ctr_apoyo_des_rural,
    cc.tipo_ciclo,
    cm.modalidad,
    cum.unidad_med,
    ccu.cultivo,
    sa.sup_sembrada,
    sa.sup_cosechada,
    sa.sup_siniestrada,
    sa.volumen_produccion,
    sa.rendimiento,
    sa.precio_med_rural,
    sa.valor_produccion
FROM stg_agricola sa
LEFT JOIN cvegeo_municipalities m   ON m.cve_mun  = sa.municipio_id AND m.cve_ent = sa.entidad_id
LEFT JOIN cvegeo_states s           ON s.cve_ent  = sa.entidad_id
LEFT JOIN cat_distritos_des_rural ddr   ON ddr.id = sa.distrito_des_rural_id
LEFT JOIN cat_ctrs_apoyo_des_rural cadr ON cadr.id = sa.ctr_apoyo_des_rural_id
LEFT JOIN cat_ciclos cc             ON cc.id       = sa.tipo_ciclo_id
LEFT JOIN cat_modalidades cm        ON cm.id       = sa.modalidad_id
LEFT JOIN cat_unidades_medida cum   ON cum.id      = sa.unidad_med_id
LEFT JOIN cat_cultivos ccu          ON ccu.id      = sa.cultivo_id
WHERE sa.entidad_id = 14;
