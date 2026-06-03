-- V4__{flujo}__vista.sql
-- Vista de integración del pipeline {flujo}.
-- Une la tabla principal con todos los catálogos para exponer datos legibles.
-- Si es SCD: filtrar por is_current = TRUE.

CREATE OR REPLACE VIEW v_{flujo} AS
SELECT
    s.id,

    -- Catálogos desnormalizados
    et.estado_tramite,
    ts.tipo_solicitante,

    -- Columnas de datos principales
    s.descripcion,
    s.valor_numerico,
    s.fecha_registro,

    s.created_at

FROM stg_{flujo} s
JOIN cat_estado_tramite    et ON et.id = s.id_estado_tramite
JOIN cat_tipo_solicitante  ts ON ts.id = s.id_tipo_solicitante

-- WHERE s.is_current = TRUE
;

COMMENT ON VIEW v_{flujo} IS 'Vista de integración del pipeline {flujo}. Expone datos desnormalizados para consulta.';
