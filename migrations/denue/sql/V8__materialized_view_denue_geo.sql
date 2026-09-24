CREATE MATERIALIZED VIEW vm_denue_geo AS
SELECT
    e.id AS fid,
    DATE '2025-01-01' AS fecha_periodo_seleccion,
    LPAD(l.entidad_id::text, 2, '0')::varchar(2) AS cve_ent,
    m.nom_ent AS entidad,
    (LPAD(l.entidad_id::text, 2, '0') || LPAD(l.municipio_id::text, 3, '0'))::varchar(5) AS cvegeo_municipio,
    m.nomgeo AS municipio,
    e.nombre_establecimiento AS unidad_economica,
    e.clee,
    e.fecha_alta AS fecha_alta_denue,
    e.tipo_vial,
    e.nom_vial AS nombre_vial,
    e.numero_ext AS numero_exterior,
    e.cod_postal AS codigo_postal,
    e.telefono::varchar AS telefono,
    e.contacto_web,
    sec.sector AS sector_economico,
    sub.subsector AS subsector_economico,
    r.rama AS rama_economica,
    sr.subrama AS subrama_economica,
    ca.clase AS actividad_economica,
    rp.descripcion AS rango_personal_ocupado,
    m.geom_iieg,
    m.geom_inegi
FROM stg_est_jal AS e
INNER JOIN cat_actualizaciones AS a
    ON a.id = e.actualizacion_id
LEFT JOIN cat_localidades AS l
    ON l.id = e.localidad_id
LEFT JOIN cvegeo_municipalities AS m
    ON m.cve_ent = l.entidad_id
    AND m.cve_mun = l.municipio_id
LEFT JOIN cat_sectores AS sec
    ON sec.id = e.sector_id
LEFT JOIN cat_subsectores AS sub
    ON sub.id = e.subsector_id
LEFT JOIN cat_ramas AS r
    ON r.id = e.rama_id
LEFT JOIN cat_subramas AS sr
    ON sr.id = e.subrama_id
LEFT JOIN cat_clases_actividad AS ca
    ON ca.id = e.clase_actividad_id
LEFT JOIN cat_rangos_personal AS rp
    ON rp.id = e.rango_personal_id
WHERE a.fecha_actualizacion = DATE '2026-05-01'
WITH NO DATA;

CREATE UNIQUE INDEX ix_vm_denue_geo_fid
    ON vm_denue_geo (fid);

CREATE INDEX ix_vm_denue_geo_geom_iieg
    ON vm_denue_geo USING GIST (geom_iieg);

CREATE INDEX ix_vm_denue_geo_geom_inegi
    ON vm_denue_geo USING GIST (geom_inegi);

COMMENT ON MATERIALIZED VIEW vm_denue_geo IS
    'Establecimientos DENUE de Jalisco del corte estadistico 2025, para consumo GIS.';
COMMENT ON COLUMN vm_denue_geo.fid IS 'Identificador unico del establecimiento DENUE.';
COMMENT ON COLUMN vm_denue_geo.fecha_periodo_seleccion IS
    'Fecha estatica de referencia del corte estadistico 2025.';
COMMENT ON COLUMN vm_denue_geo.cve_ent IS 'Clave INEGI de la entidad federativa, con dos digitos.';
COMMENT ON COLUMN vm_denue_geo.entidad IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vm_denue_geo.cvegeo_municipio IS 'Clave INEGI compuesta de entidad y municipio, con cinco digitos.';
COMMENT ON COLUMN vm_denue_geo.municipio IS 'Nombre del municipio.';
COMMENT ON COLUMN vm_denue_geo.unidad_economica IS 'Nombre de la unidad economica.';
COMMENT ON COLUMN vm_denue_geo.clee IS 'Clave Unica de Establecimiento (CLEE).';
COMMENT ON COLUMN vm_denue_geo.fecha_alta_denue IS 'Fecha de alta del establecimiento en DENUE.';
COMMENT ON COLUMN vm_denue_geo.tipo_vial IS 'Tipo de vialidad.';
COMMENT ON COLUMN vm_denue_geo.nombre_vial IS 'Nombre de la vialidad.';
COMMENT ON COLUMN vm_denue_geo.numero_exterior IS 'Numero exterior.';
COMMENT ON COLUMN vm_denue_geo.codigo_postal IS 'Codigo postal.';
COMMENT ON COLUMN vm_denue_geo.telefono IS 'Telefono de contacto.';
COMMENT ON COLUMN vm_denue_geo.contacto_web IS 'Sitio web, correo electronico o red social de contacto.';
COMMENT ON COLUMN vm_denue_geo.sector_economico IS 'Nombre del sector economico SCIAN.';
COMMENT ON COLUMN vm_denue_geo.subsector_economico IS 'Nombre del subsector economico SCIAN.';
COMMENT ON COLUMN vm_denue_geo.rama_economica IS 'Nombre de la rama economica SCIAN.';
COMMENT ON COLUMN vm_denue_geo.subrama_economica IS 'Nombre de la subrama economica SCIAN.';
COMMENT ON COLUMN vm_denue_geo.actividad_economica IS 'Nombre de la clase de actividad economica SCIAN.';
COMMENT ON COLUMN vm_denue_geo.rango_personal_ocupado IS 'Descripcion del rango de personal ocupado.';
COMMENT ON COLUMN vm_denue_geo.geom_iieg IS
    'Geometria municipal del marco geoestadistico IIEG, SRID 6368.';
COMMENT ON COLUMN vm_denue_geo.geom_inegi IS
    'Geometria municipal del marco geoestadistico INEGI, SRID 6368.';
