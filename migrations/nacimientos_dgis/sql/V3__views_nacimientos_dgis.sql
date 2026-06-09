CREATE OR REPLACE VIEW vw_nacimientos AS
SELECT
    n.id,
    n.anio,
    m.nomgeo  AS municipio,
    s.nom_ent AS entidad,
    n.cve_geo,
    n.edad_madre,
    n.tot_nac,
    n.nac_padre_conocido,
    n.nac_padre_18_mas,
    n.nac_padre_25_mas,
    n.fecha_actualizacion
FROM stg_nacimientos n
LEFT JOIN cvegeo_municipalities m ON m.cvegeo = n.cve_geo
LEFT JOIN cvegeo_states s ON s.cve_ent = 14;
