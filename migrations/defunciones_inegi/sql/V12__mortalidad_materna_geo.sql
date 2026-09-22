CREATE SERVER IF NOT EXISTS nacimientos_dgis_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (
    dbname 'nacimientos_dgis',
    host '${fdw_host}',
    port '${fdw_port}'
);

CREATE USER MAPPING IF NOT EXISTS FOR CURRENT_USER
SERVER nacimientos_dgis_server
OPTIONS (
    user '${fdw_user}',
    password '${fdw_password}'
);

CREATE FOREIGN TABLE IF NOT EXISTS nacimientos_dgis_certificados (
    anio SMALLINT,
    fecha_nacimiento DATE,
    cve_geo INTEGER
)
SERVER nacimientos_dgis_server
OPTIONS (schema_name 'public', table_name 'stg_nacimientos_certificados');

CREATE MATERIALIZED VIEW vm_mortalidad_materna_geo AS
WITH defunciones_maternas AS (
    SELECT
        d.anio_ocurrencia,
        d.entidad_residencia_id,
        d.municipio_residencia_id,
        COUNT(*) AS defunciones_maternas
    FROM stg_defunciones AS d
    INNER JOIN cvegeo_municipalities AS m
        ON m.cve_ent = d.entidad_residencia_id
        AND m.cve_mun = d.municipio_residencia_id
    WHERE d.razon_materna_id = 1
        AND d.entidad_residencia_id = 14
        AND d.anio_ocurrencia >= 2020
    GROUP BY
        d.anio_ocurrencia,
        d.entidad_residencia_id,
        d.municipio_residencia_id
),
nacimientos_vivos AS (
    SELECT
        EXTRACT(YEAR FROM n.fecha_nacimiento)::integer AS anio,
        n.cve_geo,
        COUNT(*) AS nacimientos_vivos
    FROM nacimientos_dgis_certificados AS n
    WHERE n.fecha_nacimiento IS NOT NULL
        AND n.fecha_nacimiento >= DATE '2020-01-01'
    GROUP BY EXTRACT(YEAR FROM n.fecha_nacimiento)::integer, n.cve_geo
)
SELECT
    (n.anio * 100000 + m.cvegeo)::integer AS fid,
    make_date(n.anio, 1, 1) AS fecha_periodo_seleccion,
    LPAD(m.cve_ent::text, 2, '0')::varchar(2) AS cve_ent,
    m.nom_ent AS entidad,
    LPAD(m.cvegeo::text, 5, '0')::varchar(5) AS cvegeo_municipio,
    m.nomgeo AS municipio,
    COALESCE(d.defunciones_maternas, 0) AS defunciones_maternas,
    n.nacimientos_vivos,
    COALESCE(d.defunciones_maternas, 0) * 100000.0
        / NULLIF(n.nacimientos_vivos, 0) AS razon_mortalidad_materna,
    m.geom_iieg,
    m.geom_inegi
FROM nacimientos_vivos AS n
INNER JOIN cvegeo_municipalities AS m
    ON m.cvegeo = n.cve_geo
    AND m.cve_ent = 14
LEFT JOIN defunciones_maternas AS d
    ON d.anio_ocurrencia = n.anio
    AND d.entidad_residencia_id = m.cve_ent
    AND d.municipio_residencia_id = m.cve_mun
ORDER BY n.anio, m.cvegeo
WITH NO DATA;

CREATE UNIQUE INDEX ix_vm_mortalidad_materna_geo_fid
    ON vm_mortalidad_materna_geo (fid);

CREATE UNIQUE INDEX ix_vm_mortalidad_materna_geo_periodo_municipio
    ON vm_mortalidad_materna_geo (fecha_periodo_seleccion, cvegeo_municipio);

CREATE INDEX ix_vm_mortalidad_materna_geo_fecha_periodo_seleccion
    ON vm_mortalidad_materna_geo (fecha_periodo_seleccion);

CREATE INDEX ix_vm_mortalidad_materna_geo_geom_iieg
    ON vm_mortalidad_materna_geo USING GIST (geom_iieg);

CREATE INDEX ix_vm_mortalidad_materna_geo_geom_inegi
    ON vm_mortalidad_materna_geo USING GIST (geom_inegi);

COMMENT ON MATERIALIZED VIEW vm_mortalidad_materna_geo IS
    'Razon municipal de mortalidad materna de residentes de Jalisco, desde 2020, para consumo GIS.';
COMMENT ON COLUMN vm_mortalidad_materna_geo.fid IS
    'Identificador entero, unico y estable por combinacion de anio y municipio.';
COMMENT ON COLUMN vm_mortalidad_materna_geo.fecha_periodo_seleccion IS
    'Fecha de referencia anual de la defuncion (primer dia del ano).';
COMMENT ON COLUMN vm_mortalidad_materna_geo.cve_ent IS
    'Clave INEGI de dos digitos de la entidad federativa.';
COMMENT ON COLUMN vm_mortalidad_materna_geo.entidad IS
    'Nombre de la entidad federativa.';
COMMENT ON COLUMN vm_mortalidad_materna_geo.cvegeo_municipio IS
    'Clave INEGI de cinco digitos del municipio.';
COMMENT ON COLUMN vm_mortalidad_materna_geo.municipio IS
    'Nombre oficial del municipio.';
COMMENT ON COLUMN vm_mortalidad_materna_geo.defunciones_maternas IS
    'Defunciones maternas de residentes de Jalisco, con razon_materna_id igual a 1.';
COMMENT ON COLUMN vm_mortalidad_materna_geo.nacimientos_vivos IS
    'Certificados de nacimiento agrupados por anio de nacimiento y municipio de residencia de la madre.';
COMMENT ON COLUMN vm_mortalidad_materna_geo.razon_mortalidad_materna IS
    'Defunciones maternas por cada 100000 nacimientos vivos, sin redondear.';
COMMENT ON COLUMN vm_mortalidad_materna_geo.geom_iieg IS
    'Geometria municipal del marco geoestadistico IIEG, SRID 6368.';
COMMENT ON COLUMN vm_mortalidad_materna_geo.geom_inegi IS
    'Geometria municipal del marco geoestadistico INEGI, SRID 6368.';
