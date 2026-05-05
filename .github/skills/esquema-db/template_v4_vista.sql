-- =============================================================================
-- V4__{flujo}__vista.sql
-- Vista de integración del pipeline {flujo}.
-- Une la tabla principal con todos los catálogos para exponer datos legibles.
-- Si es SCD: filtrar por is_current = TRUE.
-- =============================================================================

CREATE OR REPLACE VIEW v_{flujo} AS
SELECT
    s.id,

    -- Catálogos desnormalizados
    et.estado_tramite,
    ts.tipo_solicitante,

    -- Columnas geográficas (descomentar si aplica)
    -- m.nombre_municipio,
    -- e.nombre_entidad,

    -- Columnas de datos principales
    s.descripcion,
    s.valor_numerico,
    s.fecha_registro,

    -- Campos SCD (descomentar si aplica)
    -- s.valid_from,
    -- s.valid_to,
    -- s.is_current,

    s.created_at

FROM stg_{flujo} s
JOIN cat_estado_tramite    et ON et.id = s.id_estado_tramite
JOIN cat_tipo_solicitante  ts ON ts.id = s.id_tipo_solicitante

-- JOIN cve_geo.municipios  m ON m.cve_mun  = s.cve_mun   -- descomentar si hay geo municipal
-- JOIN cve_geo.entidades   e ON e.cve_ent  = s.cve_ent   -- descomentar si hay geo estatal

-- Descomentar la siguiente línea si el pipeline usa SCD:
-- WHERE s.is_current = TRUE
;

COMMENT ON VIEW v_{flujo} IS 'Vista de integración del pipeline {flujo}. Expone datos desnormalizados para consulta.';
