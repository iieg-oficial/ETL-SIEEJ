CREATE MATERIALIZED VIEW IF NOT EXISTS tasa_fecundidad AS
SELECT
    ROW_NUMBER() OVER ()::bigint     AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)           AS nombre,
    t.fecha,
    t.entidad_id::char(2)            AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5) AS clave_municipio,
    t.pob_mujeres_15_49              AS poblacion_mujeres_15_49,
    t.nacimientos,
    t.tasa_fec_gen                   AS tasa_fecundidad_general
FROM cvegeo_municipalities g
CROSS JOIN (SELECT DISTINCT fecha FROM stg_tasa_fecundidad) d
LEFT JOIN stg_tasa_fecundidad t
    ON t.municipio_id = LPAD(g.cvegeo::text, 5, '0')
    AND t.fecha = d.fecha
WHERE g.cvegeo / 1000 = 14
WITH NO DATA;
