DROP MATERIALIZED VIEW IF EXISTS vm_porcentaje_participacion_geo;

CREATE MATERIALIZED VIEW vm_porcentaje_participacion_geo AS
SELECT
    p.id AS fid,
    make_date(p.anio, 1, 1) AS fecha_periodo_seleccion,
    LPAD(m.cve_ent::text, 2, '0')::varchar(2) AS cve_ent,
    m.nom_ent AS entidad,
    LPAD(m.cvegeo::text, 5, '0')::varchar(5) AS cvegeo_municipio,
    m.nomgeo AS municipio,
    p.porc_participacion AS porcentaje_participacion,
    m.geom_iieg,
    m.geom_inegi
FROM stg_participacion AS p
INNER JOIN cvegeo_municipalities AS m
    ON m.cve_mun = p.municipio_id
    AND m.cve_ent = p.entidad_id
ORDER BY p.id
WITH NO DATA;

CREATE UNIQUE INDEX ix_vm_porcentaje_participacion_geo_fid
    ON vm_porcentaje_participacion_geo (fid);

CREATE INDEX ix_vm_porcentaje_participacion_geo_fecha_periodo_seleccion
    ON vm_porcentaje_participacion_geo (fecha_periodo_seleccion);

CREATE INDEX ix_vm_porcentaje_participacion_geo_geom_iieg
    ON vm_porcentaje_participacion_geo USING GIST (geom_iieg);

CREATE INDEX ix_vm_porcentaje_participacion_geo_geom_inegi
    ON vm_porcentaje_participacion_geo USING GIST (geom_inegi);

COMMENT ON MATERIALIZED VIEW vm_porcentaje_participacion_geo IS
    'Porcentaje de participacion electoral por municipio para consumo GIS.';
COMMENT ON COLUMN vm_porcentaje_participacion_geo.fid IS
    'Identificador unico de la fila de participacion.';
COMMENT ON COLUMN vm_porcentaje_participacion_geo.fecha_periodo_seleccion IS
    'Fecha de referencia anual de la eleccion (primer dia del ano).';
COMMENT ON COLUMN vm_porcentaje_participacion_geo.cve_ent IS
    'Clave INEGI de dos digitos de la entidad federativa.';
COMMENT ON COLUMN vm_porcentaje_participacion_geo.entidad IS
    'Nombre de la entidad federativa.';
COMMENT ON COLUMN vm_porcentaje_participacion_geo.cvegeo_municipio IS
    'Clave INEGI de cinco digitos del municipio.';
COMMENT ON COLUMN vm_porcentaje_participacion_geo.municipio IS
    'Nombre oficial del municipio.';
COMMENT ON COLUMN vm_porcentaje_participacion_geo.porcentaje_participacion IS
    'Porcentaje de participacion electoral municipal.';
COMMENT ON COLUMN vm_porcentaje_participacion_geo.geom_iieg IS
    'Geometria municipal del marco geoestadistico IIEG, SRID 6368.';
COMMENT ON COLUMN vm_porcentaje_participacion_geo.geom_inegi IS
    'Geometria municipal del marco geoestadistico INEGI, SRID 6368.';
