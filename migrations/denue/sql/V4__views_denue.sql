CREATE OR REPLACE VIEW v_establecimientos AS
SELECT
    e.id,
    a.fecha_actualizacion,
    e.clee,
    e.nombre_establecimiento,
    e.razon_social,
    e.latitud,
    e.longitud,
    e.fecha_alta,
    e.nombre_asentamiento,
    e.ageb,
    s.nom_ent AS entidad,
    m.nomgeo AS municipio,
    l.localidad_id,
    l.localidad,
    sec.codigo AS sector_codigo,
    sec.sector,
    sub.codigo AS subsector_codigo,
    sub.subsector,
    r.codigo AS rama_codigo,
    r.rama,
    sr.codigo AS subrama_codigo,
    sr.subrama,
    ca.codigo AS clase_actividad_codigo,
    ca.clase AS clase_actividad,
    rp.descripcion AS rango_personal,
    te.descripcion AS tipo_establecimiento
FROM stg_est_jal e
LEFT JOIN cat_actualizaciones a ON e.actualizacion_id = a.id
LEFT JOIN cat_localidades l ON e.localidad_id = l.id
LEFT JOIN cvegeo_states s ON l.entidad_id = s.cve_ent
LEFT JOIN cvegeo_municipalities m ON l.municipio_id = m.cve_mun AND l.entidad_id = m.cve_ent
LEFT JOIN cat_sectores sec ON e.sector_id = sec.id
LEFT JOIN cat_subsectores sub ON e.subsector_id = sub.id
LEFT JOIN cat_ramas r ON e.rama_id = r.id
LEFT JOIN cat_subramas sr ON e.subrama_id = sr.id
LEFT JOIN cat_clases_actividad ca ON e.clase_actividad_id = ca.id
LEFT JOIN cat_rangos_personal rp ON e.rango_personal_id = rp.id
LEFT JOIN cat_tipos_establecimientos te ON e.tipo_establecimiento_id = te.id;

COMMENT ON VIEW v_establecimientos IS 'Vista detallada de establecimientos DENUE de Jalisco con catálogos resueltos';
COMMENT ON COLUMN v_establecimientos.id IS 'Identificador DENUE del establecimiento';
COMMENT ON COLUMN v_establecimientos.fecha_actualizacion IS 'Fecha de actualización del periodo DENUE';
COMMENT ON COLUMN v_establecimientos.clee IS 'Clave Única de Establecimiento (CLEE)';
COMMENT ON COLUMN v_establecimientos.nombre_establecimiento IS 'Nombre del establecimiento';
COMMENT ON COLUMN v_establecimientos.razon_social IS 'Razón social';
COMMENT ON COLUMN v_establecimientos.latitud IS 'Latitud geográfica';
COMMENT ON COLUMN v_establecimientos.longitud IS 'Longitud geográfica';
COMMENT ON COLUMN v_establecimientos.fecha_alta IS 'Fecha de alta en DENUE';
COMMENT ON COLUMN v_establecimientos.nombre_asentamiento IS 'Nombre del asentamiento humano';
COMMENT ON COLUMN v_establecimientos.ageb IS 'Área geoestadística básica (AGEB)';
COMMENT ON COLUMN v_establecimientos.entidad IS 'Nombre de la entidad federativa';
COMMENT ON COLUMN v_establecimientos.municipio IS 'Nombre del municipio';
COMMENT ON COLUMN v_establecimientos.localidad_id IS 'Clave de la localidad';
COMMENT ON COLUMN v_establecimientos.localidad IS 'Nombre de la localidad';
COMMENT ON COLUMN v_establecimientos.sector_codigo IS 'Código SCIAN del sector';
COMMENT ON COLUMN v_establecimientos.sector IS 'Nombre del sector económico';
COMMENT ON COLUMN v_establecimientos.subsector_codigo IS 'Código SCIAN del subsector';
COMMENT ON COLUMN v_establecimientos.subsector IS 'Nombre del subsector económico';
COMMENT ON COLUMN v_establecimientos.rama_codigo IS 'Código SCIAN de la rama';
COMMENT ON COLUMN v_establecimientos.rama IS 'Nombre de la rama económica';
COMMENT ON COLUMN v_establecimientos.subrama_codigo IS 'Código SCIAN de la subrama';
COMMENT ON COLUMN v_establecimientos.subrama IS 'Nombre de la subrama económica';
COMMENT ON COLUMN v_establecimientos.clase_actividad_codigo IS 'Código SCIAN de la clase de actividad';
COMMENT ON COLUMN v_establecimientos.clase_actividad IS 'Nombre de la clase de actividad económica';
COMMENT ON COLUMN v_establecimientos.rango_personal IS 'Rango de personal ocupado';
COMMENT ON COLUMN v_establecimientos.tipo_establecimiento IS 'Tipo de unidad económica (fijo o semifijo)';
