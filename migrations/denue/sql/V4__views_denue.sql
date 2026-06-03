CREATE OR REPLACE VIEW v_establecimientos AS
SELECT
    e.entidad_id,
    s.nom_ent AS entidad,
    a.fecha_actualizacion,
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
    e.num_establecimientos
FROM stg_est_ent e
LEFT JOIN cat_actualizaciones a ON e.actualizacion_id = a.id
LEFT JOIN cvegeo_states s ON e.entidad_id = s.cve_ent
LEFT JOIN cat_sectores sec ON e.sector_id = sec.id
LEFT JOIN cat_subsectores sub ON e.subsector_id = sub.id
LEFT JOIN cat_ramas r ON e.rama_id = r.id
LEFT JOIN cat_subramas sr ON e.subrama_id = sr.id
LEFT JOIN cat_clases_actividad ca ON e.clase_actividad_id = ca.id;

COMMENT ON VIEW v_establecimientos IS 'Resumen de establecimientos DENUE por entidad y actividad económica con catálogos resueltos';
COMMENT ON COLUMN v_establecimientos.entidad_id IS 'Clave de la entidad federativa (1-32)';
COMMENT ON COLUMN v_establecimientos.entidad IS 'Nombre de la entidad federativa';
COMMENT ON COLUMN v_establecimientos.fecha_actualizacion IS 'Fecha de actualización del periodo DENUE';
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
COMMENT ON COLUMN v_establecimientos.num_establecimientos IS 'Número de establecimientos';
