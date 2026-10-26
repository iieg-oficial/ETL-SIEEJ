CREATE EXTENSION IF NOT EXISTS postgis;

CREATE MATERIALIZED VIEW vm_reto_code_geo AS
SELECT
    ROW_NUMBER() OVER (
        ORDER BY p.fecha_corte, p.municipio_id, p.nombre_espacio, p.id
    ) AS fid,
    MAKE_DATE(EXTRACT(YEAR FROM p.fecha_corte)::integer, 1, 1) AS fecha_periodo_seleccion,
    LPAD(p.entidad_id::text, 2, '0')::varchar(2) AS cve_ent,
    e.nom_ent AS entidad,
    (
        LPAD(p.entidad_id::text, 2, '0')
        || LPAD(p.municipio_id::text, 3, '0')
    )::varchar(5) AS cvegeo_municipio,
    m.nomgeo AS municipio,
    p.nombre_espacio,
    p.dias_horarios,
    a.actividad,
    p.cantidad_usuarios,
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
    FROM stg_puntos_activacion_reto AS p
) AS p
LEFT JOIN cat_actividades AS a
    ON a.id = p.actividad_id
LEFT JOIN cvegeo_states AS e
    ON e.cve_ent = p.entidad_id
LEFT JOIN cvegeo_municipalities AS m
    ON m.cve_ent = p.entidad_id
   AND m.cve_mun = p.municipio_id
ORDER BY p.fecha_corte, p.municipio_id, p.nombre_espacio, p.id
WITH NO DATA;

CREATE UNIQUE INDEX ix_vm_reto_code_geo_fid
    ON vm_reto_code_geo (fid);

CREATE INDEX ix_vm_reto_code_geo_cvegeo_municipio
    ON vm_reto_code_geo (cvegeo_municipio);

CREATE INDEX ix_vm_reto_code_geo_geom
    ON vm_reto_code_geo USING GIST (geom);

COMMENT ON MATERIALIZED VIEW vm_reto_code_geo IS
    'Puntos de activación del programa Reto CODE, con ubicación puntual para consumo GIS.';
COMMENT ON COLUMN vm_reto_code_geo.fid IS
    'Identificador único de la fila materializada.';
COMMENT ON COLUMN vm_reto_code_geo.fecha_periodo_seleccion IS
    'Primer día del año de la fecha de corte del punto de activación.';
COMMENT ON COLUMN vm_reto_code_geo.cve_ent IS
    'Clave INEGI de dos dígitos de la entidad federativa.';
COMMENT ON COLUMN vm_reto_code_geo.entidad IS
    'Nombre oficial de la entidad federativa, resuelto contra cvegeo.';
COMMENT ON COLUMN vm_reto_code_geo.cvegeo_municipio IS
    'Clave INEGI de cinco dígitos de la entidad y municipio.';
COMMENT ON COLUMN vm_reto_code_geo.municipio IS
    'Nombre oficial del municipio, resuelto contra cvegeo.';
COMMENT ON COLUMN vm_reto_code_geo.nombre_espacio IS
    'Nombre del espacio donde se realiza la actividad.';
COMMENT ON COLUMN vm_reto_code_geo.dias_horarios IS
    'Días y horarios de la actividad, en texto libre.';
COMMENT ON COLUMN vm_reto_code_geo.actividad IS
    'Nombre de la actividad, resuelto desde cat_actividades.';
COMMENT ON COLUMN vm_reto_code_geo.cantidad_usuarios IS
    'Cantidad de usuarios reportada por CODE; no debe sumarse entre espacios sin validación metodológica.';
COMMENT ON COLUMN vm_reto_code_geo.x IS
    'Coordenada X en metros, proyección EPSG:6368; nula sin coordenadas válidas de origen.';
COMMENT ON COLUMN vm_reto_code_geo.y IS
    'Coordenada Y en metros, proyección EPSG:6368; nula sin coordenadas válidas de origen.';
COMMENT ON COLUMN vm_reto_code_geo.geom IS
    'Geometría puntual EPSG:6368; nula sin coordenadas válidas de origen.';
