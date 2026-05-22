CREATE OR REPLACE VIEW v_establecimientos AS
SELECT
    e.id,
    a.fecha_actualizacion,
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
FROM stg_establecimientos e
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
