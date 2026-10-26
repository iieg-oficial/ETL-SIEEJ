CREATE EXTENSION IF NOT EXISTS postgis;

CREATE MATERIALIZED VIEW vm_prog_estra_sej_geo AS
WITH directorio_canonico AS (
    SELECT *
    FROM (
        SELECT
            d.*,
            ROW_NUMBER() OVER (
                PARTITION BY d.clave_ct
                ORDER BY d.fecha_corte DESC, d.fecha_actualizacion DESC, d.id DESC
            ) AS fila_canonica
        FROM stg_directorio_centros_trabajo AS d
    ) AS directorio_clasificado
    WHERE fila_canonica = 1
),
escuelas_programas AS (
    SELECT
        ep.id AS programa_escuela_id,
        ep.clave_ct AS clave_centro_de_trabajo,
        d.entidad_id,
        d.municipio_id,
        d.nombre_ct,
        d.domicilio,
        d.codigo_postal,
        d.telefono,
        ep.fecha_corte,
        pe.programa_estrategico,
        CASE
            WHEN LOWER(pe.programa_estrategico) IN (
                'jalisco bilingüe',
                'talento al estilo jalisco',
                'talento en estilo jalisco'
            ) THEN 'Con alumnos beneficiarios'
            WHEN LOWER(pe.programa_estrategico) IN (
                'jalisco presente escuelas de tiempo completo',
                'aulas de música',
                'vida saludable'
            ) THEN 'Sede'
        END AS estatus_sede,
        CASE
            WHEN d.longitud BETWEEN -180 AND 180
             AND d.latitud BETWEEN -90 AND 90
            THEN ST_Transform(
                ST_SetSRID(ST_MakePoint(d.longitud, d.latitud), 4326),
                6368
            )::geometry(Point, 6368)
        END AS geom
    FROM stg_escuelas_programas_estrategicos AS ep
    INNER JOIN directorio_canonico AS d
        ON d.clave_ct = ep.clave_ct
    INNER JOIN cat_programas_estrategicos AS pe
        ON pe.id = ep.programa_estrategico_id
)
SELECT
    ROW_NUMBER() OVER (
        ORDER BY ep.clave_centro_de_trabajo, ep.programa_estrategico, ep.programa_escuela_id
    ) AS fid,
    MAKE_DATE(EXTRACT(YEAR FROM ep.fecha_corte)::integer, 1, 1) AS fecha_periodo_seleccion,
    LPAD(ep.entidad_id::text, 2, '0')::varchar(2) AS cve_ent,
    e.nom_ent AS entidad,
    (
        LPAD(ep.entidad_id::text, 2, '0')
        || LPAD(ep.municipio_id::text, 3, '0')
    )::varchar(5) AS cvegeo_municipio,
    m.nomgeo AS municipio,
    ep.clave_centro_de_trabajo,
    ep.nombre_ct,
    ep.domicilio,
    ep.codigo_postal,
    ep.telefono,
    ep.programa_estrategico,
    ep.estatus_sede,
    ST_X(ep.geom) AS x,
    ST_Y(ep.geom) AS y,
    ep.geom
FROM escuelas_programas AS ep
LEFT JOIN cvegeo_states AS e
    ON e.cve_ent = ep.entidad_id
LEFT JOIN cvegeo_municipalities AS m
    ON m.cve_ent = ep.entidad_id
   AND m.cve_mun = ep.municipio_id
ORDER BY ep.clave_centro_de_trabajo, ep.programa_estrategico, ep.programa_escuela_id
WITH NO DATA;

CREATE UNIQUE INDEX ix_vm_prog_estra_sej_geo_fid
    ON vm_prog_estra_sej_geo (fid);

CREATE INDEX ix_vm_prog_estra_sej_geo_cvegeo_municipio
    ON vm_prog_estra_sej_geo (cvegeo_municipio);

CREATE INDEX ix_vm_prog_estra_sej_geo_geom
    ON vm_prog_estra_sej_geo USING GIST (geom);

COMMENT ON MATERIALIZED VIEW vm_prog_estra_sej_geo IS
    'Escuelas beneficiadas por programas estratégicos de la SEJ, con ubicación puntual para consumo GIS.';
COMMENT ON COLUMN vm_prog_estra_sej_geo.fid IS
    'Identificador único de la fila materializada.';
COMMENT ON COLUMN vm_prog_estra_sej_geo.fecha_periodo_seleccion IS
    'Primer día del año de la fecha de corte del programa estratégico.';
COMMENT ON COLUMN vm_prog_estra_sej_geo.cve_ent IS
    'Clave INEGI de dos dígitos de la entidad federativa.';
COMMENT ON COLUMN vm_prog_estra_sej_geo.entidad IS
    'Nombre oficial de la entidad federativa, resuelto contra cvegeo.';
COMMENT ON COLUMN vm_prog_estra_sej_geo.cvegeo_municipio IS
    'Clave INEGI de cinco dígitos de la entidad y municipio.';
COMMENT ON COLUMN vm_prog_estra_sej_geo.municipio IS
    'Nombre oficial del municipio, resuelto contra cvegeo.';
COMMENT ON COLUMN vm_prog_estra_sej_geo.clave_centro_de_trabajo IS
    'Clave de centro de trabajo (CCT) de la escuela beneficiada.';
COMMENT ON COLUMN vm_prog_estra_sej_geo.nombre_ct IS
    'Nombre del centro de trabajo de la fila canónica más reciente.';
COMMENT ON COLUMN vm_prog_estra_sej_geo.domicilio IS
    'Domicilio reportado por el directorio canónico.';
COMMENT ON COLUMN vm_prog_estra_sej_geo.codigo_postal IS
    'Código postal reportado por el directorio canónico.';
COMMENT ON COLUMN vm_prog_estra_sej_geo.telefono IS
    'Teléfono reportado por el directorio canónico.';
COMMENT ON COLUMN vm_prog_estra_sej_geo.programa_estrategico IS
    'Nombre del programa estratégico estatal que beneficia a la escuela.';
COMMENT ON COLUMN vm_prog_estra_sej_geo.estatus_sede IS
    'Tipo de beneficio: Sede o Con alumnos beneficiarios.';
COMMENT ON COLUMN vm_prog_estra_sej_geo.x IS
    'Coordenada X en metros, proyección EPSG:6368; nula sin coordenadas válidas de origen.';
COMMENT ON COLUMN vm_prog_estra_sej_geo.y IS
    'Coordenada Y en metros, proyección EPSG:6368; nula sin coordenadas válidas de origen.';
COMMENT ON COLUMN vm_prog_estra_sej_geo.geom IS
    'Geometría puntual EPSG:6368; nula sin coordenadas válidas de origen.';
