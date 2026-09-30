CREATE OR REPLACE VIEW vw_directorio_centros_trabajo AS
SELECT
    d.clave_ct,
    d.nombre_ct,
    t.turno,
    n.nivel,
    p.programa,
    s.sostenimiento,
    me.medio,
    r.region,
    e.nom_ent AS entidad,
    m.nomgeo AS municipio,
    l.localidad,
    c.colonia,
    d.domicilio,
    d.codigo_postal,
    d.telefono,
    d.director,
    d.zona_escolar,
    d.sector,
    d.longitud,
    d.latitud,
    d.escuelas,
    d.hombres_matriculados,
    d.mujeres_matriculadas,
    d.total_matriculados,
    d.total_docentes_directivo,
    d.fecha_corte,
    d.fecha_actualizacion_fuente,
    d.fecha_actualizacion
FROM stg_directorio_centros_trabajo d
LEFT JOIN cat_turnos t ON t.id = d.turno_id
LEFT JOIN cat_niveles n ON n.id = d.nivel_id
LEFT JOIN cat_programas p ON p.id = d.programa_id
LEFT JOIN cat_sostenimientos s ON s.id = d.sostenimiento_id
LEFT JOIN cat_medios me ON me.id = d.medio_id
LEFT JOIN cat_regiones r ON r.id = d.region_id
LEFT JOIN cat_localidades l ON l.id = d.localidad_id
LEFT JOIN cat_colonias c ON c.id = d.colonia_id
LEFT JOIN cvegeo_states e ON e.cve_ent = d.entidad_id
LEFT JOIN cvegeo_municipalities m ON m.cve_mun = d.municipio_id AND m.cve_ent = d.entidad_id;

CREATE OR REPLACE VIEW vw_escuelas_programas_estrategicos AS
SELECT
    ep.clave_ct,
    pe.programa_estrategico,
    ep.fecha_corte,
    ep.fecha_actualizacion_fuente,
    ep.fecha_actualizacion
FROM stg_escuelas_programas_estrategicos ep
LEFT JOIN cat_programas_estrategicos pe ON pe.id = ep.programa_estrategico_id;

CREATE OR REPLACE VIEW vw_aulas_google AS
SELECT
    a.clave_ct,
    a.nombre_ct,
    a.inmueble,
    ro.region_operativa,
    e.nom_ent AS entidad,
    m.nomgeo AS municipio,
    a.aulas_asignadas,
    a.fecha_corte,
    a.fecha_actualizacion_fuente,
    a.fecha_actualizacion
FROM stg_aulas_google a
LEFT JOIN cat_regiones_operativas ro ON ro.id = a.region_operativa_id
LEFT JOIN cvegeo_states e ON e.cve_ent = a.entidad_id
LEFT JOIN cvegeo_municipalities m ON m.cve_mun = a.municipio_id AND m.cve_ent = a.entidad_id;
