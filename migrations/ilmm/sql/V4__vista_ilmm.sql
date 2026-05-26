CREATE OR REPLACE VIEW vw_ilmm AS
SELECT
    s.id,
    s.fecha,
    s.clave_municipio,
    LPAD(m.cvegeo::text, 5, '0')  AS cvegeo,
    m.nomgeo                       AS nom_municipio,
    m.nom_ent,
    i.indicador,
    s.valor,
    s.error_estandar
FROM stg_ilmm s
JOIN cat_ilmm_indicador i ON i.id = s.indicador_id
LEFT JOIN cvegeo_municipalities m ON LPAD(m.cvegeo::text, 5, '0') = s.clave_municipio;

COMMENT ON VIEW vw_ilmm IS 'Vista de integración del pipeline ilmm. Expone indicadores del mercado de trabajo municipal con nombres geográficos.';
