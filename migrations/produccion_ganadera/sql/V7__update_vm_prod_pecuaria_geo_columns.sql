DROP MATERIALIZED VIEW IF EXISTS vm_prod_pecuaria_geo;

CREATE MATERIALIZED VIEW vm_prod_pecuaria_geo AS
SELECT
    sg.id AS fid,
    make_date(sg.anio, 1, 1) AS fecha_periodo_seleccion,
    LPAD(m.cve_ent::text, 2, '0')::varchar(2) AS cve_ent,
    m.nom_ent AS entidad,
    LPAD(m.cvegeo::text, 5, '0')::varchar(5) AS cvegeo_municipio,
    m.nomgeo AS municipio,
    sg.valor_produccion / 1000000.0 AS valor_produccion_total_mdp,
    m.geom_iieg,
    m.geom_inegi
FROM stg_ganadera AS sg
INNER JOIN cvegeo_municipalities AS m
    ON m.cve_mun = sg.municipio_id
    AND m.cve_ent = sg.entidad_id
INNER JOIN cat_productos AS cp
    ON cp.id = sg.producto_id
WHERE sg.entidad_id = 14
    AND LOWER(BTRIM(cp.producto)) <> 'ganado en pie'
ORDER BY sg.id
WITH NO DATA;

CREATE UNIQUE INDEX ix_vm_prod_pecuaria_geo_fid
    ON vm_prod_pecuaria_geo (fid);

CREATE INDEX ix_vm_prod_pecuaria_geo_geom_iieg
    ON vm_prod_pecuaria_geo USING GIST (geom_iieg);

CREATE INDEX ix_vm_prod_pecuaria_geo_geom_inegi
    ON vm_prod_pecuaria_geo USING GIST (geom_inegi);

COMMENT ON MATERIALIZED VIEW vm_prod_pecuaria_geo IS
    'Produccion pecuaria municipal de Jalisco, para consumo GIS.';
COMMENT ON COLUMN vm_prod_pecuaria_geo.fid IS 'Identificador estable de la fila.';
COMMENT ON COLUMN vm_prod_pecuaria_geo.fecha_periodo_seleccion IS
    'Fecha de referencia anual de la produccion pecuaria.';
COMMENT ON COLUMN vm_prod_pecuaria_geo.cve_ent IS 'Clave INEGI de la entidad federativa.';
COMMENT ON COLUMN vm_prod_pecuaria_geo.entidad IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vm_prod_pecuaria_geo.cvegeo_municipio IS 'Clave INEGI del municipio.';
COMMENT ON COLUMN vm_prod_pecuaria_geo.municipio IS 'Nombre del municipio.';
COMMENT ON COLUMN vm_prod_pecuaria_geo.valor_produccion_total_mdp IS
    'Valor total de la produccion pecuaria en millones de pesos corrientes; excluye Ganado en pie.';
COMMENT ON COLUMN vm_prod_pecuaria_geo.geom_iieg IS
    'Geometria municipal del marco geoestadistico IIEG, SRID 6368.';
COMMENT ON COLUMN vm_prod_pecuaria_geo.geom_inegi IS
    'Geometria municipal del marco geoestadistico INEGI, SRID 6368.';
