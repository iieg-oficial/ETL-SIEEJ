CREATE OR REPLACE VIEW v_centros_educativos AS
SELECT
    c.clave_centro_trabajo,
    c.nombre_centro_trabajo,
    c.fecha_actualizacion,
    t.turno,
    te.tipo_educativo,
    ne.nivel_educativo,
    se.servicio_educativo,
    tc.tipo_control,
    ts.tipo_sostenimiento,
    s.nom_ent AS entidad,
    m.nomgeo AS municipio,
    l.clave_localidad,
    l.localidad,
    d.domicilio,
    d.numero_exterior,
    d.codigo_postal,
    d.entre_calle,
    d.y_calle,
    d.calle_posterior,
    col.colonia,
    c.total_alumnos_hombres,
    c.total_alumnas_mujeres,
    c.total_docentes_hombres,
    c.total_docentes_mujeres,
    c.aulas_en_uso,
    c.aulas_existentes,
    c.latitud,
    c.longitud
FROM centros c
LEFT JOIN turnos t ON c.turno_id = t.id
LEFT JOIN tipos_educativos te ON c.tipos_educativos_id = te.id
LEFT JOIN niveles_educativos ne ON c.nivel_educativo_id = ne.id
LEFT JOIN servicios_educativos se ON c.servicio_educativo_id = se.id
LEFT JOIN tipos_controles tc ON c.tipo_control_id = tc.id
LEFT JOIN tipos_sostenimiento ts ON c.tipo_sostenimiento_id = ts.id
LEFT JOIN cvegeo_states s ON c.entidad_id = s.cve_ent
LEFT JOIN cvegeo_municipalities m ON c.municipio_id = m.cve_mun AND c.entidad_id = m.cve_ent
LEFT JOIN localidades l ON c.localidades_id = l.id
LEFT JOIN domicilios d ON c.domicilios_id = d.id
LEFT JOIN colonias col ON c.colonias_id = col.id;