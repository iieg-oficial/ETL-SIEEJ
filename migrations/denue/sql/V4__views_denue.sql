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
    l.clave_localidad,
    l.localidad,
    ae.nombre_actividad_economica AS actividad_economica,
    rp.descripcion AS rango_personal,
    te.descripcion AS tipo_establecimiento
FROM establecimientos e
LEFT JOIN actualizaciones a ON e.actualizacion_id = a.id
LEFT JOIN localidades l ON e.localidad_id = l.id
LEFT JOIN cvegeo_states s ON l.entidad_id = s.cve_ent
LEFT JOIN cvegeo_municipalities m ON l.municipio_id = m.cve_mun AND l.entidad_id = m.cve_ent
LEFT JOIN actividades_economicas ae ON e.actividad_economica_id = ae.id
LEFT JOIN rangos_personal rp ON e.rango_personal_id = rp.id
LEFT JOIN tipos_establecimientos te ON e.tipo_establecimiento_id = te.id;
