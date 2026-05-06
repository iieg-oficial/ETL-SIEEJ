CREATE OR REPLACE VIEW view_iim_entidades AS
SELECT
    e.entidad_id,
    s.nom_ent               AS entidad,
    e.viv_totales,
    e.por_viv_remesas,
    e.por_viv_emigrantes,
    e.por_viv_reto,
    e.iim_dp2,
    e.grado_iim,
    e.lugar_contexto_nacional,
    e.fecha
FROM iim_estatal e
LEFT JOIN cvegeo_states s ON s.cve_ent = e.entidad_id;

CREATE OR REPLACE VIEW view_iim_municipios_jalisco AS
SELECT
    i.municipio_id,
    m.nomgeo                AS municipio,
    i.viv_totales,
    i.por_viv_remesas,
    i.por_viv_emigrantes,
    i.por_viv_reto,
    i.iim_dp2,
    i.grado_iim,
    i.lugar_contexto_nacional,
    i.fecha
FROM iim_municipal i
LEFT JOIN cvegeo_municipalities m ON m.cvegeo = i.municipio_id
WHERE m.cve_ent = 14;
