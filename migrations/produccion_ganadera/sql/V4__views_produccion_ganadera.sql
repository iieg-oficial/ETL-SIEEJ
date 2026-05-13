CREATE OR REPLACE VIEW view_ganadera_jalisco AS
SELECT
    sg.id,
    sg.anio,
    m.nomgeo                        AS municipio,
    s.nom_ent                       AS entidad,
    ddr.dis_des_rural,
    ce.especie,
    cp.producto,
    sg.volumen_produccion,
    sg.peso_sacrificio,
    sg.precio_med_rural,
    sg.valor_produccion,
    sg.animales_sacrificados
FROM stg_ganadera sg
LEFT JOIN cvegeo_municipalities m   ON m.cve_mun = sg.municipio_id AND m.cve_ent = sg.entidad_id
LEFT JOIN cvegeo_states s           ON s.cve_ent = sg.entidad_id
LEFT JOIN cat_distritos_des_rural ddr ON ddr.id  = sg.distrito_des_rural_id
LEFT JOIN cat_especies ce           ON ce.id      = sg.especie_id
LEFT JOIN cat_productos cp          ON cp.id      = sg.producto_id
WHERE sg.entidad_id = 14;
