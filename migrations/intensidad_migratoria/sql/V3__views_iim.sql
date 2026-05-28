CREATE OR REPLACE VIEW view_iim_entidades AS
SELECT
    e.entidad_id,
    s.nom_ent               AS entidad,
    e.viv_totales,
    e.por_viv_remesas,
    e.por_viv_emigrantes,
    e.por_viv_reto,
    e.iim_dp2,
    e.gim_dp2,
    e.lugar_contexto_nacional,
    e.fecha
FROM iim_estatal e
LEFT JOIN cvegeo_states s ON s.cve_ent = e.entidad_id;

CREATE OR REPLACE VIEW view_iim_municipios_jalisco_2010 AS
SELECT
    i.municipio_id,
    m.nomgeo                AS municipio,
    i.viv_totales,
    i.por_viv_remesas,
    i.por_viv_emigrantes,
    i.por_viv_reto,
    i.iaim,
    i.gaim,
    i.lugar_contexto_nacional,
    RANK() OVER (ORDER BY i.iaim DESC) AS lugar_entidad
FROM iim_municipal i
LEFT JOIN cvegeo_municipalities m ON m.cvegeo = i.municipio_id
WHERE m.cve_ent = 14 AND i.fecha = 2010;

CREATE OR REPLACE VIEW view_iim_municipios_jalisco_2020 AS
SELECT
    i.municipio_id,
    m.nomgeo                AS municipio,
    i.viv_totales,
    i.por_viv_remesas,
    i.por_viv_emigrantes,
    i.por_viv_reto,
    i.iim_dp2,
    i.gim_dp2,
    i.lugar_contexto_nacional,
    RANK() OVER (ORDER BY i.iim_dp2 ASC) AS lugar_entidad
FROM iim_municipal i
LEFT JOIN cvegeo_municipalities m ON m.cvegeo = i.municipio_id
WHERE m.cve_ent = 14 AND i.fecha = 2020;
