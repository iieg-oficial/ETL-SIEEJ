CREATE MATERIALIZED VIEW vm_aulas_google_geo AS
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
aulas_canonicas AS (
    SELECT *
    FROM (
        SELECT
            a.*,
            ROW_NUMBER() OVER (
                PARTITION BY a.clave_ct
                ORDER BY a.fecha_corte DESC, a.fecha_actualizacion DESC, a.id DESC
            ) AS fila_canonica
        FROM stg_aulas_google AS a
    ) AS aulas_clasificadas
    WHERE fila_canonica = 1
),
aulas_geo AS (
    SELECT
        a.id AS aula_id,
        a.clave_ct AS clave_centro_de_trabajo,
        a.fecha_corte,
        d.entidad_id,
        d.municipio_id,
        d.nombre_ct,
        d.domicilio,
        d.codigo_postal,
        d.telefono,
        CASE
            WHEN d.longitud BETWEEN -180 AND 180
             AND d.latitud BETWEEN -90 AND 90
            THEN ST_Transform(
                ST_SetSRID(ST_MakePoint(d.longitud, d.latitud), 4326),
                6368
            )::geometry(Point, 6368)
        END AS geom
    FROM aulas_canonicas AS a
    INNER JOIN directorio_canonico AS d
        ON d.clave_ct = a.clave_ct
)
SELECT
    ROW_NUMBER() OVER (ORDER BY a.clave_centro_de_trabajo, a.aula_id) AS fid,
    MAKE_DATE(EXTRACT(YEAR FROM a.fecha_corte)::integer, 1, 1) AS fecha_periodo_seleccion,
    LPAD(a.entidad_id::text, 2, '0')::varchar(2) AS cve_ent,
    e.nom_ent AS entidad,
    (
        LPAD(a.entidad_id::text, 2, '0')
        || LPAD(a.municipio_id::text, 3, '0')
    )::varchar(5) AS cvegeo_municipio,
    m.nomgeo AS municipio,
    a.clave_centro_de_trabajo,
    a.nombre_ct,
    a.domicilio,
    a.codigo_postal,
    a.telefono,
    ST_X(a.geom) AS x,
    ST_Y(a.geom) AS y,
    a.geom
FROM aulas_geo AS a
LEFT JOIN cvegeo_states AS e
    ON e.cve_ent = a.entidad_id
LEFT JOIN cvegeo_municipalities AS m
    ON m.cve_ent = a.entidad_id
   AND m.cve_mun = a.municipio_id
ORDER BY a.clave_centro_de_trabajo, a.aula_id
WITH NO DATA;

CREATE UNIQUE INDEX ix_vm_aulas_google_geo_fid
    ON vm_aulas_google_geo (fid);

CREATE INDEX ix_vm_aulas_google_geo_cvegeo_municipio
    ON vm_aulas_google_geo (cvegeo_municipio);

CREATE INDEX ix_vm_aulas_google_geo_geom
    ON vm_aulas_google_geo USING GIST (geom);

COMMENT ON MATERIALIZED VIEW vm_aulas_google_geo IS
    'Escuelas con Aulas Google de la SEJ, con ubicación puntual para consumo GIS.';
COMMENT ON COLUMN vm_aulas_google_geo.fid IS
    'Identificador único de la fila materializada.';
COMMENT ON COLUMN vm_aulas_google_geo.fecha_periodo_seleccion IS
    'Primer día del año de la fecha de corte de Aulas Google.';
COMMENT ON COLUMN vm_aulas_google_geo.cve_ent IS
    'Clave INEGI de dos dígitos de la entidad federativa.';
COMMENT ON COLUMN vm_aulas_google_geo.entidad IS
    'Nombre oficial de la entidad federativa, resuelto contra cvegeo.';
COMMENT ON COLUMN vm_aulas_google_geo.cvegeo_municipio IS
    'Clave INEGI de cinco dígitos de la entidad y municipio.';
COMMENT ON COLUMN vm_aulas_google_geo.municipio IS
    'Nombre oficial del municipio, resuelto contra cvegeo.';
COMMENT ON COLUMN vm_aulas_google_geo.clave_centro_de_trabajo IS
    'Clave de centro de trabajo (CCT) de la escuela con Aulas Google.';
COMMENT ON COLUMN vm_aulas_google_geo.nombre_ct IS
    'Nombre del centro de trabajo de la fila canónica más reciente del directorio.';
COMMENT ON COLUMN vm_aulas_google_geo.domicilio IS
    'Domicilio reportado por el directorio canónico.';
COMMENT ON COLUMN vm_aulas_google_geo.codigo_postal IS
    'Código postal reportado por el directorio canónico.';
COMMENT ON COLUMN vm_aulas_google_geo.telefono IS
    'Teléfono reportado por el directorio canónico.';
COMMENT ON COLUMN vm_aulas_google_geo.x IS
    'Coordenada X en metros, proyección EPSG:6368; nula sin coordenadas válidas de origen.';
COMMENT ON COLUMN vm_aulas_google_geo.y IS
    'Coordenada Y en metros, proyección EPSG:6368; nula sin coordenadas válidas de origen.';
COMMENT ON COLUMN vm_aulas_google_geo.geom IS
    'Geometría puntual EPSG:6368; nula sin coordenadas válidas de origen.';
