-- Base view for the mapalab fiscalia layer.
-- Reproduces the server table seguridad_y_proteccion_ciudadana.delitos_fiscalia
-- from the normalized model (casos + catalogs). Replaces delitos_vw.

CREATE EXTENSION IF NOT EXISTS postgis;

DROP VIEW IF EXISTS delitos_vw;

CREATE OR REPLACE VIEW vw_mapalab_fiscalia AS
SELECT
    c.fecha_denuncia AS fecha,
    'Jalisco'::varchar AS entidad,
    m.nomgeo AS municipio,
    c.longitud AS x_6368,
    c.latitud AS y_6368,
    CASE ba.bien_afectado
        WHEN 'La vida y la integridad sexual' THEN 'La libertad y la seguridad sexual'
        ELSE ba.bien_afectado
    END AS bien_juridico,
    CASE d.delito
        WHEN 'Robo a carga pesada'     THEN 'Robo a vehículos de carga pesada'
        WHEN 'Robo a int de vehículos' THEN 'Robo a interior de vehículos'
        WHEN 'Robo casa habitación'    THEN 'Robo a casa habitación'
        WHEN 'Robo de motocicleta'     THEN 'Robo de motocicletas'
        ELSE d.delito
    END AS delito,
    v.violencia AS modalidad,
    CASE EXTRACT(DOW FROM c.fecha_denuncia)::int
        WHEN 0 THEN 'domingo'
        WHEN 1 THEN 'lunes'
        WHEN 2 THEN 'martes'
        WHEN 3 THEN 'miércoles'
        WHEN 4 THEN 'jueves'
        WHEN 5 THEN 'viernes'
        WHEN 6 THEN 'sábado'
    END AS dia_semana,
    CASE
        WHEN c.hora IS NULL OR c.hora = '' THEN 'No disponible'
        WHEN split_part(c.hora, ':', 1)::int BETWEEN 0  AND 5  THEN 'Madrugada 00-06 h'
        WHEN split_part(c.hora, ':', 1)::int BETWEEN 6  AND 11 THEN 'Mañana 06-12 h'
        WHEN split_part(c.hora, ':', 1)::int BETWEEN 12 AND 17 THEN 'Tarde 12-18 h'
        ELSE 'Noche 18-24 h'
    END AS rango_hora,
    CASE
        WHEN c.longitud IS NOT NULL AND c.latitud IS NOT NULL
        THEN ST_SetSRID(ST_MakePoint(c.longitud, c.latitud), 6368)
    END::geometry(Point, 6368) AS geom
FROM casos c
LEFT JOIN delitos d               ON c.delitos_id = d.id
LEFT JOIN bien_afectado ba        ON d.bien_afectado_id = ba.id
LEFT JOIN violencia v             ON c.violencia_id = v.id
LEFT JOIN cvegeo_municipalities m ON c.municipios_id = m.cve_mun AND m.cve_ent = 14;
