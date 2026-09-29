DROP MATERIALIZED VIEW vm_prod_pecuaria_geo;

CREATE MATERIALIZED VIEW vm_prod_pecuaria_geo AS
WITH produccion_municipal AS (
    SELECT
        MIN(sg.id) AS fid,
        sg.anio,
        sg.entidad_id,
        sg.municipio_id,
        SUM(sg.valor_produccion) / 1000.0 AS valor_produccion_total_mdp
    FROM stg_ganadera AS sg
    INNER JOIN cat_productos AS cp
        ON cp.id = sg.producto_id
    WHERE sg.entidad_id = 14
        AND LOWER(BTRIM(cp.producto)) <> 'ganado en pie'
    GROUP BY
        sg.anio,
        sg.entidad_id,
        sg.municipio_id
)
SELECT
    pm.fid,
    make_date(pm.anio, 1, 1) AS fecha_periodo_seleccion,
    LPAD(m.cve_ent::text, 2, '0')::varchar(2) AS cve_ent,
    m.nom_ent AS entidad,
    LPAD(m.cvegeo::text, 5, '0')::varchar(5) AS cvegeo_municipio,
    m.nomgeo AS municipio,
    pm.valor_produccion_total_mdp,
    m.geom_iieg,
    m.geom_inegi
FROM produccion_municipal AS pm
INNER JOIN cvegeo_municipalities AS m
    ON m.cve_mun = pm.municipio_id
    AND m.cve_ent = pm.entidad_id
ORDER BY fecha_periodo_seleccion, cvegeo_municipio
WITH NO DATA;

CREATE UNIQUE INDEX ix_vm_prod_pecuaria_geo_fid
    ON vm_prod_pecuaria_geo (fid);

CREATE UNIQUE INDEX ux_vm_prod_pecuaria_geo_fecha_cvegeo_municipio
    ON vm_prod_pecuaria_geo (fecha_periodo_seleccion, cvegeo_municipio);

CREATE INDEX ix_vm_prod_pecuaria_geo_geom_iieg
    ON vm_prod_pecuaria_geo USING GIST (geom_iieg);

CREATE INDEX ix_vm_prod_pecuaria_geo_geom_inegi
    ON vm_prod_pecuaria_geo USING GIST (geom_inegi);

COMMENT ON MATERIALIZED VIEW vm_prod_pecuaria_geo IS
    'Produccion pecuaria municipal anual de Jalisco, para consumo GIS.';
COMMENT ON COLUMN vm_prod_pecuaria_geo.fid IS
    'Identificador estable, unico y no nulo de la fila anual-municipal.';
COMMENT ON COLUMN vm_prod_pecuaria_geo.fecha_periodo_seleccion IS
    'Fecha anual de referencia de la produccion pecuaria.';
COMMENT ON COLUMN vm_prod_pecuaria_geo.cve_ent IS
    'Clave INEGI de la entidad federativa.';
COMMENT ON COLUMN vm_prod_pecuaria_geo.entidad IS
    'Nombre de la entidad federativa.';
COMMENT ON COLUMN vm_prod_pecuaria_geo.cvegeo_municipio IS
    'Clave INEGI del municipio.';
COMMENT ON COLUMN vm_prod_pecuaria_geo.municipio IS
    'Nombre oficial del municipio.';
COMMENT ON COLUMN vm_prod_pecuaria_geo.valor_produccion_total_mdp IS
    'Valor total de la produccion en millones de pesos corrientes; excluye Ganado en pie.';
COMMENT ON COLUMN vm_prod_pecuaria_geo.geom_iieg IS
    'Geometria municipal del marco geoestadistico IIEG, SRID 6368.';
COMMENT ON COLUMN vm_prod_pecuaria_geo.geom_inegi IS
    'Geometria municipal del marco geoestadistico INEGI, SRID 6368.';
