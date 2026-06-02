CREATE OR REPLACE VIEW v_directorio_escuelas AS
SELECT
    d.anio,
    d.clave_ct,
    d.nombre_ct,
    t.nombre_turno,
    d.domicilio,
    d.localidad_id,
    d.nombre_localidad,
    d.colonia_id,
    d.nombre_colonia,
    s.nom_ent AS entidad,
    m.nomgeo AS municipio,
    d.nombre_municipio,
    me.medio,
    d.director,
    d.codigo_postal,
    d.telefono,
    d.zona_escolar,
    d.sector,
    cs.sostenimiento,
    cc.id AS codigo_sostenimiento,
    n.nivel,
    p.programa,
    r.id AS region_id,
    r.nombre_region,
    d.longitud,
    d.latitud,
    d.escuelas,
    d.hombres_matriculados,
    d.mujeres_matriculadas,
    d.total_matriculados,
    d.total_docentes_directivo,
    d.fecha_actualizacion
FROM stg_directorio_escuelas d
LEFT JOIN cat_turnos t ON d.turno_id = t.id
LEFT JOIN cat_codigos_sostenimiento cc ON d.codigo_sostenimiento_id = cc.id
LEFT JOIN cat_sostenimientos cs ON cc.sostenimiento_id = cs.id
LEFT JOIN cat_niveles n ON d.nivel_id = n.id
LEFT JOIN cat_programas p ON d.programa_id = p.id
LEFT JOIN cat_regiones r ON d.region_id = r.id
LEFT JOIN cat_medios me ON d.medio_id = me.id
LEFT JOIN cvegeo_states s ON d.entidad_id = s.cve_ent
LEFT JOIN cvegeo_municipalities m ON d.entidad_id = m.cve_ent AND d.municipio_id = m.cve_mun;

CREATE OR REPLACE VIEW v_estadistica_escuelas AS
SELECT
    e.anio,
    np.nivel_programa,
    s.sostenimiento,
    e.escuelas,
    e.matricula,
    e.docentes,
    e.fecha_actualizacion
FROM stg_estadistica_escuelas e
LEFT JOIN cat_niveles_programa np ON e.nivel_programa_id = np.id
LEFT JOIN cat_sostenimientos s ON e.sostenimiento_id = s.id;
