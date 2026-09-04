CREATE MATERIALIZED VIEW vm_agricola_geo AS
SELECT
    sa.id AS fid,
    make_date(sa.anio, 1, 1) AS fecha,
    LPAD(m.cve_ent::text, 2, '0')::varchar(2) AS cve_ent,
    m.nom_ent AS entidad,
    LPAD(m.cvegeo::text, 5, '0')::varchar(5) AS cvegeo,
    m.nomgeo AS municipio,
    sa.valor_produccion / 1000000.0 AS valor_produccion_total_mdp,
    sa.sup_sembrada AS superficie_sembrada_total_ha,
    sa.sup_cosechada AS superficie_cosechada_total_ha,
    sa.sup_siniestrada AS superficie_siniestrada_total_ha,
    sa.volumen_produccion AS volumen_produccion_total_toneladas,
    m.geom_iieg,
    m.geom_inegi
FROM stg_agricola AS sa
INNER JOIN cvegeo_municipalities AS m
    ON m.cve_mun = sa.municipio_id
    AND m.cve_ent = sa.entidad_id
WHERE sa.entidad_id = 14
ORDER BY sa.id
WITH NO DATA;

CREATE UNIQUE INDEX ix_vm_agricola_geo_fid
    ON vm_agricola_geo (fid);

CREATE INDEX ix_vm_agricola_geo_geom_iieg
    ON vm_agricola_geo USING GIST (geom_iieg);

CREATE INDEX ix_vm_agricola_geo_geom_inegi
    ON vm_agricola_geo USING GIST (geom_inegi);

COMMENT ON MATERIALIZED VIEW vm_agricola_geo IS
    'Produccion agricola municipal de Jalisco, para consumo GIS.';
COMMENT ON COLUMN vm_agricola_geo.fid IS 'Identificador estable de la fila.';
COMMENT ON COLUMN vm_agricola_geo.fecha IS 'Fecha de referencia anual de la produccion agricola.';
COMMENT ON COLUMN vm_agricola_geo.cve_ent IS 'Clave INEGI de la entidad federativa.';
COMMENT ON COLUMN vm_agricola_geo.entidad IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vm_agricola_geo.cvegeo IS 'Clave INEGI del municipio.';
COMMENT ON COLUMN vm_agricola_geo.municipio IS 'Nombre del municipio.';
COMMENT ON COLUMN vm_agricola_geo.valor_produccion_total_mdp IS
    'Valor total de la produccion agricola en millones de pesos corrientes.';
COMMENT ON COLUMN vm_agricola_geo.superficie_sembrada_total_ha IS
    'Superficie total sembrada en hectareas.';
COMMENT ON COLUMN vm_agricola_geo.superficie_cosechada_total_ha IS
    'Superficie total cosechada en hectareas.';
COMMENT ON COLUMN vm_agricola_geo.superficie_siniestrada_total_ha IS
    'Superficie total siniestrada en hectareas.';
COMMENT ON COLUMN vm_agricola_geo.volumen_produccion_total_toneladas IS
    'Volumen total de produccion en toneladas.';
COMMENT ON COLUMN vm_agricola_geo.geom_iieg IS
    'Geometria municipal del marco geoestadistico IIEG, SRID 6368.';
COMMENT ON COLUMN vm_agricola_geo.geom_inegi IS
    'Geometria municipal del marco geoestadistico INEGI, SRID 6368.';
