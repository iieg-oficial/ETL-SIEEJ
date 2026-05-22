CREATE OR REPLACE VIEW vw_participacion AS
SELECT
    s.nom_ent AS entidad,
    m.nomgeo AS municipio,
    p.porc_participacion,
    p.anio
FROM stg_participacion p
LEFT JOIN cvegeo_states s ON p.entidad_id = s.cve_ent
LEFT JOIN cvegeo_municipalities m ON p.municipio_id = m.cve_mun AND p.entidad_id = m.cve_ent;
