CREATE OR REPLACE VIEW vw_puntos_activacion_reto AS
SELECT
    p.clave_punto,
    e.nom_ent AS entidad,
    m.nomgeo AS municipio,
    r.region,
    p.nombre_espacio,
    p.dias_horarios,
    a.actividad,
    p.cantidad_usuarios,
    p.longitud,
    p.latitud,
    p.fecha_corte,
    p.fecha_actualizacion_fuente,
    p.fecha_actualizacion
FROM stg_puntos_activacion_reto p
LEFT JOIN cat_regiones r ON r.id = p.region_id
LEFT JOIN cat_actividades a ON a.id = p.actividad_id
LEFT JOIN cvegeo_states e ON e.cve_ent = p.entidad_id
LEFT JOIN cvegeo_municipalities m ON m.cve_mun = p.municipio_id AND m.cve_ent = p.entidad_id;
