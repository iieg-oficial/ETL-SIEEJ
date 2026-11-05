CREATE OR REPLACE VIEW vw_academias_deportivas AS
SELECT
    e.nom_ent AS entidad,
    m.nomgeo AS municipio,
    d.deporte,
    a.deporte_nombre_largo,
    t.tipo,
    a.beneficiarios_total,
    a.beneficiarios_hombres,
    a.beneficiarios_mujeres,
    a.domicilio,
    a.horarios,
    a.longitud,
    a.latitud,
    a.fecha_corte,
    a.fecha_actualizacion_fuente,
    a.fecha_actualizacion
FROM stg_academias_deportivas a
JOIN cat_deportes d ON d.id = a.deporte_id
JOIN cat_tipos_academia t ON t.id = a.tipo_id
LEFT JOIN cvegeo_states e ON e.cve_ent = a.entidad_id
LEFT JOIN cvegeo_municipalities m ON m.cve_mun = a.municipio_id AND m.cve_ent = a.entidad_id;

CREATE OR REPLACE VIEW vw_polideportivos AS
SELECT
    e.nom_ent AS entidad,
    m.nomgeo AS municipio,
    p.nombre_centro,
    p.domicilio,
    p.horarios,
    (
        SELECT STRING_AGG(d.deporte, ', ' ORDER BY d.deporte)
        FROM polideportivo_deportes pd
        JOIN cat_deportes d ON d.id = pd.deporte_id
        WHERE pd.polideportivo_id = p.id
    ) AS deportes,
    p.servicios,
    p.longitud,
    p.latitud,
    p.fecha_corte,
    p.fecha_actualizacion_fuente,
    p.fecha_actualizacion
FROM stg_polideportivos p
LEFT JOIN cvegeo_states e ON e.cve_ent = p.entidad_id
LEFT JOIN cvegeo_municipalities m ON m.cve_mun = p.municipio_id AND m.cve_ent = p.entidad_id;

CREATE OR REPLACE VIEW vw_polideportivo_deportes AS
SELECT
    m.nomgeo AS municipio,
    p.nombre_centro,
    d.deporte,
    p.fecha_corte
FROM polideportivo_deportes pd
JOIN stg_polideportivos p ON p.id = pd.polideportivo_id
JOIN cat_deportes d ON d.id = pd.deporte_id
LEFT JOIN cvegeo_municipalities m ON m.cve_mun = p.municipio_id AND m.cve_ent = p.entidad_id;
