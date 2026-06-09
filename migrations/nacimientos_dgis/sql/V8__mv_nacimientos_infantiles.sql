CREATE MATERIALIZED VIEW IF NOT EXISTS nacimientos_infantiles AS
SELECT
    ROW_NUMBER() OVER ()::bigint     AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)           AS nombre,
    t.fecha,
    '14'::char(2)                    AS clave_entidad,
    COALESCE(t.nac_madres_10_14, 0)::numeric
        AS nacimientos,
    COALESCE(t.tasa_esp_fec_madres_10_14, 0)::numeric
        AS tasa_fecundidad_especifica,
    COALESCE(t.pct_padres_18_mas_madres_10_14, 0)::numeric
        AS porcentaje_con_edad_mayor_18
FROM cvegeo_municipalities g
CROSS JOIN (SELECT DISTINCT fecha FROM stg_nacimientos_adolescentes) d
LEFT JOIN stg_nacimientos_adolescentes t
    ON t.municipio_id = LPAD(g.cvegeo::text, 5, '0')
    AND t.fecha = d.fecha
WHERE g.cvegeo / 1000 = 14
WITH NO DATA;
