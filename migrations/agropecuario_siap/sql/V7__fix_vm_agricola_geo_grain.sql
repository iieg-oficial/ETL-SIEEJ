DROP MATERIALIZED VIEW vm_agricola_geo;

CREATE MATERIALIZED VIEW vm_agricola_geo AS
WITH produccion_municipal AS (
    SELECT
        MIN(sa.id) AS fid,
        sa.anio,
        sa.entidad_id,
        sa.municipio_id,
        SUM(sa.valor_produccion) / 1000.0 AS valor_produccion_total_mdp,
        SUM(sa.sup_sembrada) AS superficie_sembrada_total_ha,
        SUM(sa.sup_cosechada) AS superficie_cosechada_total_ha,
        SUM(sa.sup_siniestrada) AS superficie_siniestrada_total_ha
    FROM stg_agricola AS sa
    WHERE sa.entidad_id = 14
    GROUP BY
        sa.anio,
        sa.entidad_id,
        sa.municipio_id
)
SELECT
    pm.fid,
    make_date(pm.anio, 1, 1) AS fecha,
    LPAD(m.cve_ent::text, 2, '0')::varchar(2) AS cve_ent,
    m.nom_ent AS entidad,
    LPAD(m.cvegeo::text, 5, '0')::varchar(5) AS cvegeo,
    m.nomgeo AS municipio,
    pm.valor_produccion_total_mdp,
    pm.superficie_sembrada_total_ha,
    pm.superficie_cosechada_total_ha,
    pm.superficie_siniestrada_total_ha,
    m.geom_iieg,
    m.geom_inegi
FROM produccion_municipal AS pm
INNER JOIN cvegeo_municipalities AS m
    ON m.cve_mun = pm.municipio_id
    AND m.cve_ent = pm.entidad_id
ORDER BY fecha, cvegeo
WITH NO DATA;

CREATE UNIQUE INDEX ix_vm_agricola_geo_fid
    ON vm_agricola_geo (fid);

CREATE UNIQUE INDEX ux_vm_agricola_geo_fecha_cvegeo
    ON vm_agricola_geo (fecha, cvegeo);

CREATE INDEX ix_vm_agricola_geo_geom_iieg
    ON vm_agricola_geo USING GIST (geom_iieg);

CREATE INDEX ix_vm_agricola_geo_geom_inegi
    ON vm_agricola_geo USING GIST (geom_inegi);

COMMENT ON MATERIALIZED VIEW vm_agricola_geo IS
    'Produccion agricola municipal anual de Jalisco, para consumo GIS.';
COMMENT ON COLUMN vm_agricola_geo.fid IS
    'Identificador estable, unico y no nulo de la fila anual-municipal.';
COMMENT ON COLUMN vm_agricola_geo.fecha IS
    'Fecha anual de referencia de la produccion agricola.';
COMMENT ON COLUMN vm_agricola_geo.cve_ent IS
    'Clave INEGI de la entidad federativa.';
COMMENT ON COLUMN vm_agricola_geo.entidad IS
    'Nombre de la entidad federativa.';
COMMENT ON COLUMN vm_agricola_geo.cvegeo IS
    'Clave INEGI del municipio.';
COMMENT ON COLUMN vm_agricola_geo.municipio IS
    'Nombre oficial del municipio.';
COMMENT ON COLUMN vm_agricola_geo.valor_produccion_total_mdp IS
    'Valor total de la produccion en millones de pesos corrientes.';
COMMENT ON COLUMN vm_agricola_geo.superficie_sembrada_total_ha IS
    'Superficie total sembrada en hectareas.';
COMMENT ON COLUMN vm_agricola_geo.superficie_cosechada_total_ha IS
    'Superficie total cosechada en hectareas.';
COMMENT ON COLUMN vm_agricola_geo.superficie_siniestrada_total_ha IS
    'Superficie total siniestrada en hectareas.';
COMMENT ON COLUMN vm_agricola_geo.geom_iieg IS
    'Geometria municipal del marco geoestadistico IIEG, SRID 6368.';
COMMENT ON COLUMN vm_agricola_geo.geom_inegi IS
    'Geometria municipal del marco geoestadistico INEGI, SRID 6368.';
