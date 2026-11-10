CREATE EXTENSION IF NOT EXISTS postgis;

CREATE MATERIALIZED VIEW vm_academias_deportivas_geo AS
SELECT
    ROW_NUMBER() OVER (
        ORDER BY a.fecha_corte, a.municipio_id, a.deporte_id, a.id
    ) AS fid,
    MAKE_DATE(EXTRACT(YEAR FROM a.fecha_corte)::integer, 1, 1) AS fecha_periodo_seleccion,
    LPAD(a.entidad_id::text, 2, '0')::varchar(2) AS cve_ent,
    e.nom_ent AS entidad,
    (
        LPAD(a.entidad_id::text, 2, '0')
        || LPAD(a.municipio_id::text, 3, '0')
    )::varchar(5) AS cvegeo_municipio,
    m.nomgeo AS municipio,
    d.deporte,
    a.deporte_nombre_largo,
    t.tipo,
    a.beneficiarios_total,
    a.beneficiarios_hombres,
    a.beneficiarios_mujeres,
    a.domicilio,
    a.horarios,
    ST_X(geom) AS x,
    ST_Y(geom) AS y,
    geom
FROM (
    SELECT
        a.*,
        CASE
            WHEN a.longitud BETWEEN -180 AND 180
             AND a.latitud BETWEEN -90 AND 90
            THEN ST_Transform(
                ST_SetSRID(ST_MakePoint(a.longitud, a.latitud), 4326),
                6368
            )::geometry(Point, 6368)
        END AS geom
    FROM stg_academias_deportivas AS a
) AS a
JOIN cat_deportes AS d
    ON d.id = a.deporte_id
JOIN cat_tipos_academia AS t
    ON t.id = a.tipo_id
LEFT JOIN cvegeo_states AS e
    ON e.cve_ent = a.entidad_id
LEFT JOIN cvegeo_municipalities AS m
    ON m.cve_ent = a.entidad_id
   AND m.cve_mun = a.municipio_id
ORDER BY a.fecha_corte, a.municipio_id, a.deporte_id, a.id
WITH NO DATA;

CREATE UNIQUE INDEX ix_vm_academias_deportivas_geo_fid
    ON vm_academias_deportivas_geo (fid);

CREATE INDEX ix_vm_academias_deportivas_geo_cvegeo_municipio
    ON vm_academias_deportivas_geo (cvegeo_municipio);

CREATE INDEX ix_vm_academias_deportivas_geo_geom
    ON vm_academias_deportivas_geo USING GIST (geom);

COMMENT ON MATERIALIZED VIEW vm_academias_deportivas_geo IS
    'Academias deportivas de CODE, Espacios para la Paz, con ubicación puntual para consumo GIS.';
COMMENT ON COLUMN vm_academias_deportivas_geo.fid IS
    'Identificador único de la fila materializada.';
COMMENT ON COLUMN vm_academias_deportivas_geo.fecha_periodo_seleccion IS
    'Primer día del año de la fecha de corte de la academia.';
COMMENT ON COLUMN vm_academias_deportivas_geo.cve_ent IS
    'Clave INEGI de dos dígitos de la entidad federativa.';
COMMENT ON COLUMN vm_academias_deportivas_geo.entidad IS
    'Nombre oficial de la entidad federativa, resuelto contra cvegeo.';
COMMENT ON COLUMN vm_academias_deportivas_geo.cvegeo_municipio IS
    'Clave INEGI de cinco dígitos de la entidad y municipio.';
COMMENT ON COLUMN vm_academias_deportivas_geo.municipio IS
    'Nombre oficial del municipio, resuelto contra cvegeo.';
COMMENT ON COLUMN vm_academias_deportivas_geo.deporte IS
    'Nombre del deporte, resuelto desde cat_deportes.';
COMMENT ON COLUMN vm_academias_deportivas_geo.deporte_nombre_largo IS
    'Nombre largo con que CODE captura la academia o disciplina, tal como viene.';
COMMENT ON COLUMN vm_academias_deportivas_geo.tipo IS
    'Tipo de academia, resuelto desde cat_tipos_academia.';
COMMENT ON COLUMN vm_academias_deportivas_geo.beneficiarios_total IS
    'Total de beneficiarios reportado; nulo si el origen no lo trae y puede no igualar hombres más mujeres.';
COMMENT ON COLUMN vm_academias_deportivas_geo.beneficiarios_hombres IS
    'Beneficiarios hombres; nulo si el origen no lo trae.';
COMMENT ON COLUMN vm_academias_deportivas_geo.beneficiarios_mujeres IS
    'Beneficiarias mujeres; nulo si el origen no lo trae.';
COMMENT ON COLUMN vm_academias_deportivas_geo.domicilio IS
    'Domicilio de la academia, en texto libre.';
COMMENT ON COLUMN vm_academias_deportivas_geo.horarios IS
    'Días y horarios de la academia, en texto libre.';
COMMENT ON COLUMN vm_academias_deportivas_geo.x IS
    'Coordenada X en metros, proyección EPSG:6368; nula sin coordenadas válidas de origen.';
COMMENT ON COLUMN vm_academias_deportivas_geo.y IS
    'Coordenada Y en metros, proyección EPSG:6368; nula sin coordenadas válidas de origen.';
COMMENT ON COLUMN vm_academias_deportivas_geo.geom IS
    'Geometría puntual EPSG:6368; nula sin coordenadas válidas de origen.';

CREATE MATERIALIZED VIEW vm_polideportivos_geo AS
SELECT
    ROW_NUMBER() OVER (
        ORDER BY p.fecha_corte, p.municipio_id, p.nombre_centro, p.id
    ) AS fid,
    MAKE_DATE(EXTRACT(YEAR FROM p.fecha_corte)::integer, 1, 1) AS fecha_periodo_seleccion,
    LPAD(p.entidad_id::text, 2, '0')::varchar(2) AS cve_ent,
    e.nom_ent AS entidad,
    (
        LPAD(p.entidad_id::text, 2, '0')
        || LPAD(p.municipio_id::text, 3, '0')
    )::varchar(5) AS cvegeo_municipio,
    m.nomgeo AS municipio,
    p.nombre_centro,
    p.domicilio,
    p.horarios,
    p.servicios,
    (
        SELECT STRING_AGG(d.deporte, ', ' ORDER BY d.deporte)
        FROM polideportivo_deportes AS pd
        JOIN cat_deportes AS d
            ON d.id = pd.deporte_id
        WHERE pd.polideportivo_id = p.id
    ) AS deportes,
    ST_X(geom) AS x,
    ST_Y(geom) AS y,
    geom
FROM (
    SELECT
        p.*,
        CASE
            WHEN p.longitud BETWEEN -180 AND 180
             AND p.latitud BETWEEN -90 AND 90
            THEN ST_Transform(
                ST_SetSRID(ST_MakePoint(p.longitud, p.latitud), 4326),
                6368
            )::geometry(Point, 6368)
        END AS geom
    FROM stg_polideportivos AS p
) AS p
LEFT JOIN cvegeo_states AS e
    ON e.cve_ent = p.entidad_id
LEFT JOIN cvegeo_municipalities AS m
    ON m.cve_ent = p.entidad_id
   AND m.cve_mun = p.municipio_id
ORDER BY p.fecha_corte, p.municipio_id, p.nombre_centro, p.id
WITH NO DATA;

CREATE UNIQUE INDEX ix_vm_polideportivos_geo_fid
    ON vm_polideportivos_geo (fid);

CREATE INDEX ix_vm_polideportivos_geo_cvegeo_municipio
    ON vm_polideportivos_geo (cvegeo_municipio);

CREATE INDEX ix_vm_polideportivos_geo_geom
    ON vm_polideportivos_geo USING GIST (geom);

COMMENT ON MATERIALIZED VIEW vm_polideportivos_geo IS
    'Polideportivos de CODE con la lista de deportes agregada en texto y ubicación puntual para consumo GIS.';
COMMENT ON COLUMN vm_polideportivos_geo.fid IS
    'Identificador único de la fila materializada.';
COMMENT ON COLUMN vm_polideportivos_geo.fecha_periodo_seleccion IS
    'Primer día del año de la fecha de corte del polideportivo.';
COMMENT ON COLUMN vm_polideportivos_geo.cve_ent IS
    'Clave INEGI de dos dígitos de la entidad federativa.';
COMMENT ON COLUMN vm_polideportivos_geo.entidad IS
    'Nombre oficial de la entidad federativa, resuelto contra cvegeo.';
COMMENT ON COLUMN vm_polideportivos_geo.cvegeo_municipio IS
    'Clave INEGI de cinco dígitos de la entidad y municipio.';
COMMENT ON COLUMN vm_polideportivos_geo.municipio IS
    'Nombre oficial del municipio, resuelto contra cvegeo.';
COMMENT ON COLUMN vm_polideportivos_geo.nombre_centro IS
    'Nombre del polideportivo.';
COMMENT ON COLUMN vm_polideportivos_geo.domicilio IS
    'Domicilio del polideportivo, en texto libre.';
COMMENT ON COLUMN vm_polideportivos_geo.horarios IS
    'Días y horarios del polideportivo, en texto libre.';
COMMENT ON COLUMN vm_polideportivos_geo.servicios IS
    'Descripción de servicios y disciplinas, en texto libre y tal como la captura CODE.';
COMMENT ON COLUMN vm_polideportivos_geo.deportes IS
    'Deportes que ofrece el polideportivo, separados por coma y en orden alfabético; nulo si no tiene deportes asociados.';
COMMENT ON COLUMN vm_polideportivos_geo.x IS
    'Coordenada X en metros, proyección EPSG:6368; nula sin coordenadas válidas de origen.';
COMMENT ON COLUMN vm_polideportivos_geo.y IS
    'Coordenada Y en metros, proyección EPSG:6368; nula sin coordenadas válidas de origen.';
COMMENT ON COLUMN vm_polideportivos_geo.geom IS
    'Geometría puntual EPSG:6368; nula sin coordenadas válidas de origen.';
