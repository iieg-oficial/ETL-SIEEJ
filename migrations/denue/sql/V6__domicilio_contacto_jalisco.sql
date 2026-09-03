ALTER TABLE stg_est_jal
    ADD COLUMN IF NOT EXISTS tipo_vial TEXT,
    ADD COLUMN IF NOT EXISTS nom_vial TEXT,
    ADD COLUMN IF NOT EXISTS numero_ext TEXT,
    ADD COLUMN IF NOT EXISTS cod_postal TEXT,
    ADD COLUMN IF NOT EXISTS telefono TEXT,
    ADD COLUMN IF NOT EXISTS contacto_web TEXT;

COMMENT ON COLUMN stg_est_jal.tipo_vial IS 'Tipo de vialidad (calle, avenida, boulevard, etc.)';
COMMENT ON COLUMN stg_est_jal.nom_vial IS 'Nombre de la vialidad';
COMMENT ON COLUMN stg_est_jal.numero_ext IS 'Número exterior del establecimiento';
COMMENT ON COLUMN stg_est_jal.cod_postal IS 'Código postal; TEXT para conservar los ceros a la izquierda';
COMMENT ON COLUMN stg_est_jal.telefono IS 'Teléfono de contacto tal como viene del origen, sin normalizar';
COMMENT ON COLUMN stg_est_jal.contacto_web IS 'Sitio web, correo electrónico o red social, tal como viene del origen, sin validar';

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
    te.descripcion AS tipo_establecimiento,
    e.tipo_vial,
    e.nom_vial,
    e.numero_ext,
    e.cod_postal,
    e.telefono,
    e.contacto_web
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

COMMENT ON COLUMN v_establecimientos_jalisco.tipo_vial IS 'Tipo de vialidad (calle, avenida, boulevard, etc.)';
COMMENT ON COLUMN v_establecimientos_jalisco.nom_vial IS 'Nombre de la vialidad';
COMMENT ON COLUMN v_establecimientos_jalisco.numero_ext IS 'Número exterior del establecimiento';
COMMENT ON COLUMN v_establecimientos_jalisco.cod_postal IS 'Código postal; TEXT para conservar los ceros a la izquierda';
COMMENT ON COLUMN v_establecimientos_jalisco.telefono IS 'Teléfono de contacto tal como viene del origen, sin normalizar';
COMMENT ON COLUMN v_establecimientos_jalisco.contacto_web IS 'Sitio web, correo electrónico o red social, tal como viene del origen, sin validar';
