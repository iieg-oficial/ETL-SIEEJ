CREATE OR REPLACE VIEW view_inegi_2010 AS
SELECT
    p.entidad_id,
    s.nom_ent                AS entidad,
    p.municipio_id,
    m.nomgeo                 AS municipio,
    l.localidad,
    CASE WHEN p.localidad_id IS NULL THEN 'Municipal' ELSE 'Localidad' END AS nivel,
    p.total,
    p.total_hombres,
    p.total_mujeres,
    p.viviendas_habitadas
FROM poblacion p
LEFT JOIN localidades          l ON l.id       = p.localidad_id
LEFT JOIN cvegeo_municipalities m ON m.cve_mun  = p.municipio_id AND m.cve_ent = p.entidad_id
LEFT JOIN cvegeo_states         s ON s.cve_ent  = p.entidad_id
WHERE p.fuente_id = 1;

CREATE OR REPLACE VIEW view_inegi_2015 AS
SELECT
    p.entidad_id,
    s.nom_ent                AS entidad,
    p.municipio_id,
    m.nomgeo                 AS municipio,
    CASE WHEN p.localidad_id IS NULL THEN 'Municipal' ELSE 'Localidad' END AS nivel,
    p.total,
    p.total_hombres,
    p.total_mujeres
FROM poblacion p
LEFT JOIN cvegeo_municipalities m ON m.cve_mun  = p.municipio_id AND m.cve_ent = p.entidad_id
LEFT JOIN cvegeo_states         s ON s.cve_ent  = p.entidad_id
WHERE p.fuente_id = 2;

CREATE OR REPLACE VIEW view_inegi_2020 AS
SELECT
    p.entidad_id,
    s.nom_ent                AS entidad,
    p.municipio_id,
    m.nomgeo                 AS municipio,
    l.localidad,
    CASE WHEN p.localidad_id IS NULL THEN 'Municipal' ELSE 'Localidad' END AS nivel,
    p.total,
    p.total_hombres,
    p.total_mujeres,
    p.viviendas_habitadas
FROM poblacion p
LEFT JOIN localidades          l ON l.id       = p.localidad_id
LEFT JOIN cvegeo_municipalities m ON m.cve_mun  = p.municipio_id AND m.cve_ent = p.entidad_id
LEFT JOIN cvegeo_states         s ON s.cve_ent  = p.entidad_id
WHERE p.fuente_id = 3;
