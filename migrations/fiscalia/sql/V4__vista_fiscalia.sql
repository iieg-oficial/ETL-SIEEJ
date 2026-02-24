CREATE OR REPLACE VIEW mart_fiscalia_vw  AS
SELECT
    c.id,
    d.delito,
    ba.bien_afectado,
    v.violencia,
    zg.zona_geografica,
    m.nomgeo AS municipio,
    m.cvegeo,
    col.colonia,
    cal.calle,
    cr.cruce,
    c.hora,
    c.longitud,
    c.latitud,
    c.fecha_denuncia,
    c.fecha_actualizacion
FROM casos c
LEFT JOIN delitos d
    ON c.delitos_id = d.id
LEFT JOIN bien_afectado ba
    ON d.bien_afectado_id = ba.id
LEFT JOIN violencia v
    ON c.violencia_id = v.id
LEFT JOIN zonas_geograficas zg
    ON c.zonas_geograficas_id = zg.id
LEFT JOIN cvegeo_municipalities m
    ON c.municipios_id = m.cve_mun
    AND m.cve_ent = 14
LEFT JOIN colonias col
    ON c.colonias_id = col.id
LEFT JOIN calles cal
    ON c.calles_id = cal.id
LEFT JOIN cruces cr
    ON c.cruces_id = cr.id;
