CREATE OR REPLACE VIEW v_establecimientos_jalisco AS
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
    m.nomgeo AS municipio,
    l.localidad_id,
    l.localidad,
    sec.sector,
    sub.subsector,
    r.rama,
    sr.subrama,
    ca.clase AS clase_actividad,
    rp.descripcion AS rango_personal,
    te.descripcion AS tipo_establecimiento
FROM stg_est_jal e
LEFT JOIN cat_actualizaciones a ON e.actualizacion_id = a.id
LEFT JOIN cat_localidades l ON e.localidad_id = l.id
LEFT JOIN cvegeo_municipalities m ON l.municipio_id = m.cve_mun AND l.entidad_id = m.cve_ent
LEFT JOIN cat_sectores sec ON e.sector_id = sec.id
LEFT JOIN cat_subsectores sub ON e.subsector_id = sub.id
LEFT JOIN cat_ramas r ON e.rama_id = r.id
LEFT JOIN cat_subramas sr ON e.subrama_id = sr.id
LEFT JOIN cat_clases_actividad ca ON e.clase_actividad_id = ca.id
LEFT JOIN cat_rangos_personal rp ON e.rango_personal_id = rp.id
LEFT JOIN cat_tipos_establecimientos te ON e.tipo_establecimiento_id = te.id
WHERE l.entidad_id = 14;

COMMENT ON VIEW v_establecimientos_jalisco IS 'Vista de establecimientos DENUE filtrada para Jalisco (entidad 14) con catálogos resueltos';
COMMENT ON COLUMN v_establecimientos_jalisco.id IS 'Identificador DENUE del establecimiento';
COMMENT ON COLUMN v_establecimientos_jalisco.fecha_actualizacion IS 'Fecha de actualización del periodo DENUE';
COMMENT ON COLUMN v_establecimientos_jalisco.clee IS 'Clave Única de Establecimiento (CLEE)';
COMMENT ON COLUMN v_establecimientos_jalisco.nombre_establecimiento IS 'Nombre del establecimiento';
COMMENT ON COLUMN v_establecimientos_jalisco.razon_social IS 'Razón social';
COMMENT ON COLUMN v_establecimientos_jalisco.latitud IS 'Latitud geográfica';
COMMENT ON COLUMN v_establecimientos_jalisco.longitud IS 'Longitud geográfica';
COMMENT ON COLUMN v_establecimientos_jalisco.fecha_alta IS 'Fecha de alta en DENUE';
COMMENT ON COLUMN v_establecimientos_jalisco.nombre_asentamiento IS 'Nombre del asentamiento humano';
COMMENT ON COLUMN v_establecimientos_jalisco.ageb IS 'Área geoestadística básica (AGEB)';
COMMENT ON COLUMN v_establecimientos_jalisco.municipio IS 'Nombre del municipio';
COMMENT ON COLUMN v_establecimientos_jalisco.localidad_id IS 'Clave de la localidad';
COMMENT ON COLUMN v_establecimientos_jalisco.localidad IS 'Nombre de la localidad';
COMMENT ON COLUMN v_establecimientos_jalisco.sector IS 'Nombre del sector económico';
COMMENT ON COLUMN v_establecimientos_jalisco.subsector IS 'Nombre del subsector económico';
COMMENT ON COLUMN v_establecimientos_jalisco.rama IS 'Nombre de la rama económica';
COMMENT ON COLUMN v_establecimientos_jalisco.subrama IS 'Nombre de la subrama económica';
COMMENT ON COLUMN v_establecimientos_jalisco.clase_actividad IS 'Nombre de la clase de actividad económica';
COMMENT ON COLUMN v_establecimientos_jalisco.rango_personal IS 'Rango de personal ocupado';
COMMENT ON COLUMN v_establecimientos_jalisco.tipo_establecimiento IS 'Tipo de unidad económica (fijo o semifijo)';
