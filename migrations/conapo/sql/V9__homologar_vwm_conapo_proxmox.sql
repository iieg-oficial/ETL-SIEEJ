-- =============================================================================
-- V9__homologar_vwm_conapo_proxmox.sql  |  Pipeline: conapo
-- Homologa las 8 MVs de conapo con sus equivalentes en proxmox
-- (demografia.*). No modifica V6-V8: los datos y el grid ya coinciden
-- exactamente con proxmox (6,375 filas: 125 municipios x 51 anios
-- 1990-2040), validado con datos reales (Guadalajara 2020). El unico
-- problema es de esquema de columnas:
--   - `poblacion`: proxmox NO tiene clave_municipio (patron de columnas
--     multiples, igual que las vistas derivadas de efipem #240); las 4
--     columnas quedan como numeric sin precision fija.
--   - Las otras 7 vistas: proxmox nombra la columna de valor uniformemente
--     `valor numeric(12,2)`, en vez de un nombre propio por vista
--     (razon_dependencia, edad_mediana, porcentaje, etc.).
-- Ver comparaciones/compare_conapo.py
-- =============================================================================

DROP MATERIALIZED VIEW IF EXISTS razon_dependencia_infantil;
DROP MATERIALIZED VIEW IF EXISTS razon_dependencia_adulta;
DROP MATERIALIZED VIEW IF EXISTS razon_dependencia;
DROP MATERIALIZED VIEW IF EXISTS porcentaje_poblacional_municipal_en_entidad;
DROP MATERIALIZED VIEW IF EXISTS edad_mediana;
DROP MATERIALIZED VIEW IF EXISTS poblacion_mujeres;
DROP MATERIALIZED VIEW IF EXISTS poblacion_hombres;
DROP MATERIALIZED VIEW IF EXISTS poblacion;

-- ---------------------------------------------------------------------------
-- 1. poblacion (sin clave_municipio, 4 columnas numeric)
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW poblacion AS
SELECT
    ROW_NUMBER() OVER ()::bigint               AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                     AS nombre,
    make_date(i.anio, 1, 1)                    AS fecha,
    '14'::char(2)                              AS clave_entidad,
    i.pob_mit_mun::numeric                     AS poblacion_total,
    i.muj_mit_ano::numeric                     AS poblacion_mujeres,
    i.hom_mit_ano::numeric                     AS poblacion_hombres,
    ROUND(i.por_mun::numeric, 2)               AS poblacion_respecto_jalisco
FROM stg_indicadores_demograficos i
JOIN cvegeo_municipalities g ON i.municipio_id = g.cvegeo
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX ix_poblacion_fid ON poblacion (fid);

-- ---------------------------------------------------------------------------
-- 2. poblacion_hombres
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW poblacion_hombres AS
SELECT
    ROW_NUMBER() OVER ()::bigint               AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                     AS nombre,
    make_date(i.anio, 1, 1)                    AS fecha,
    '14'::char(2)                              AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    i.hom_mit_ano::numeric(12,2)               AS valor
FROM stg_indicadores_demograficos i
JOIN cvegeo_municipalities g ON i.municipio_id = g.cvegeo
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX ix_poblacion_hombres_fid ON poblacion_hombres (fid);

-- ---------------------------------------------------------------------------
-- 3. poblacion_mujeres
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW poblacion_mujeres AS
SELECT
    ROW_NUMBER() OVER ()::bigint               AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                     AS nombre,
    make_date(i.anio, 1, 1)                    AS fecha,
    '14'::char(2)                              AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    i.muj_mit_ano::numeric(12,2)               AS valor
FROM stg_indicadores_demograficos i
JOIN cvegeo_municipalities g ON i.municipio_id = g.cvegeo
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX ix_poblacion_mujeres_fid ON poblacion_mujeres (fid);

-- ---------------------------------------------------------------------------
-- 4. edad_mediana
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW edad_mediana AS
SELECT
    ROW_NUMBER() OVER ()::bigint               AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                     AS nombre,
    make_date(i.anio, 1, 1)                    AS fecha,
    '14'::char(2)                              AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    i.edad_med::numeric(12,2)                  AS valor
FROM stg_indicadores_demograficos i
JOIN cvegeo_municipalities g ON i.municipio_id = g.cvegeo
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX ix_edad_mediana_fid ON edad_mediana (fid);

-- ---------------------------------------------------------------------------
-- 5. porcentaje_poblacional_municipal_en_entidad
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW porcentaje_poblacional_municipal_en_entidad AS
SELECT
    ROW_NUMBER() OVER ()::bigint               AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                     AS nombre,
    make_date(i.anio, 1, 1)                    AS fecha,
    '14'::char(2)                              AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    ROUND(i.por_mun::numeric, 2)::numeric(12,2) AS valor
FROM stg_indicadores_demograficos i
JOIN cvegeo_municipalities g ON i.municipio_id = g.cvegeo
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX ix_porcentaje_poblacional_municipal_en_entidad_fid
    ON porcentaje_poblacional_municipal_en_entidad (fid);

-- ---------------------------------------------------------------------------
-- 6. razon_dependencia
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW razon_dependencia AS
SELECT
    ROW_NUMBER() OVER ()::bigint               AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                     AS nombre,
    make_date(i.anio, 1, 1)                    AS fecha,
    '14'::char(2)                              AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    ROUND(i.raz_dep::numeric, 2)::numeric(12,2) AS valor
FROM stg_indicadores_demograficos i
JOIN cvegeo_municipalities g ON i.municipio_id = g.cvegeo
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX ix_razon_dependencia_fid ON razon_dependencia (fid);

-- ---------------------------------------------------------------------------
-- 7. razon_dependencia_adulta
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW razon_dependencia_adulta AS
SELECT
    ROW_NUMBER() OVER ()::bigint               AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                     AS nombre,
    make_date(i.anio, 1, 1)                    AS fecha,
    '14'::char(2)                              AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    ROUND(i.raz_dep_adu::numeric, 2)::numeric(12,2) AS valor
FROM stg_indicadores_demograficos i
JOIN cvegeo_municipalities g ON i.municipio_id = g.cvegeo
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX ix_razon_dependencia_adulta_fid ON razon_dependencia_adulta (fid);

-- ---------------------------------------------------------------------------
-- 8. razon_dependencia_infantil
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW razon_dependencia_infantil AS
SELECT
    ROW_NUMBER() OVER ()::bigint               AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                     AS nombre,
    make_date(i.anio, 1, 1)                    AS fecha,
    '14'::char(2)                              AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    ROUND(i.raz_dep_inf::numeric, 2)::numeric(12,2) AS valor
FROM stg_indicadores_demograficos i
JOIN cvegeo_municipalities g ON i.municipio_id = g.cvegeo
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX ix_razon_dependencia_infantil_fid ON razon_dependencia_infantil (fid);

-- =============================================================================
-- Comentarios
-- =============================================================================

COMMENT ON MATERIALIZED VIEW poblacion IS
    'Proyeccion anual de poblacion total, hombres y mujeres por municipio (CONAPO).';
COMMENT ON COLUMN poblacion.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN poblacion.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN poblacion.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN poblacion.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN poblacion.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN poblacion.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN poblacion.poblacion_total IS 'Poblacion total proyectada';
COMMENT ON COLUMN poblacion.poblacion_mujeres IS 'Poblacion femenina proyectada';
COMMENT ON COLUMN poblacion.poblacion_hombres IS 'Poblacion masculina proyectada';
COMMENT ON COLUMN poblacion.poblacion_respecto_jalisco IS 'Porcentaje de la poblacion municipal respecto al total de Jalisco (0-100)';

COMMENT ON MATERIALIZED VIEW poblacion_hombres IS
    'Proyeccion anual de poblacion masculina por municipio (CONAPO).';
COMMENT ON COLUMN poblacion_hombres.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN poblacion_hombres.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN poblacion_hombres.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN poblacion_hombres.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN poblacion_hombres.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN poblacion_hombres.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN poblacion_hombres.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN poblacion_hombres.valor IS 'Poblacion masculina proyectada';

COMMENT ON MATERIALIZED VIEW poblacion_mujeres IS
    'Proyeccion anual de poblacion femenina por municipio (CONAPO).';
COMMENT ON COLUMN poblacion_mujeres.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN poblacion_mujeres.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN poblacion_mujeres.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN poblacion_mujeres.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN poblacion_mujeres.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN poblacion_mujeres.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN poblacion_mujeres.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN poblacion_mujeres.valor IS 'Poblacion femenina proyectada';

COMMENT ON MATERIALIZED VIEW edad_mediana IS
    'Edad mediana proyectada por municipio y anio (CONAPO).';
COMMENT ON COLUMN edad_mediana.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN edad_mediana.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN edad_mediana.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN edad_mediana.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN edad_mediana.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN edad_mediana.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN edad_mediana.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN edad_mediana.valor IS 'Edad mediana proyectada';

COMMENT ON MATERIALIZED VIEW porcentaje_poblacional_municipal_en_entidad IS
    'Peso demografico del municipio respecto al total de Jalisco (CONAPO).';
COMMENT ON COLUMN porcentaje_poblacional_municipal_en_entidad.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN porcentaje_poblacional_municipal_en_entidad.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN porcentaje_poblacional_municipal_en_entidad.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN porcentaje_poblacional_municipal_en_entidad.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN porcentaje_poblacional_municipal_en_entidad.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN porcentaje_poblacional_municipal_en_entidad.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN porcentaje_poblacional_municipal_en_entidad.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN porcentaje_poblacional_municipal_en_entidad.valor IS 'Porcentaje de la poblacion municipal respecto al total de Jalisco (0-100)';

COMMENT ON MATERIALIZED VIEW razon_dependencia IS
    'Razon de dependencia total (dependientes / poblacion en edad activa) por municipio (CONAPO).';
COMMENT ON COLUMN razon_dependencia.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN razon_dependencia.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN razon_dependencia.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN razon_dependencia.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN razon_dependencia.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN razon_dependencia.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN razon_dependencia.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN razon_dependencia.valor IS 'Razon de dependencia total';

COMMENT ON MATERIALIZED VIEW razon_dependencia_adulta IS
    'Razon de dependencia adulta (65+ / poblacion en edad activa) por municipio (CONAPO).';
COMMENT ON COLUMN razon_dependencia_adulta.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN razon_dependencia_adulta.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN razon_dependencia_adulta.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN razon_dependencia_adulta.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN razon_dependencia_adulta.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN razon_dependencia_adulta.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN razon_dependencia_adulta.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN razon_dependencia_adulta.valor IS 'Razon de dependencia adulta';

COMMENT ON MATERIALIZED VIEW razon_dependencia_infantil IS
    'Razon de dependencia infantil (0-14 / poblacion en edad activa) por municipio (CONAPO).';
COMMENT ON COLUMN razon_dependencia_infantil.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN razon_dependencia_infantil.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN razon_dependencia_infantil.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN razon_dependencia_infantil.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN razon_dependencia_infantil.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN razon_dependencia_infantil.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN razon_dependencia_infantil.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN razon_dependencia_infantil.valor IS 'Razon de dependencia infantil';
