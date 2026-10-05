-- Tabla de bitácora: registra cambios de catálogo y eventos relevantes del pipeline.

CREATE TABLE IF NOT EXISTS bitacora (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    tipo_cambio VARCHAR(50) NOT NULL,
    tabla_afectada VARCHAR(100),
    descripcion TEXT NOT NULL,
    referencia VARCHAR(100)
);

COMMENT ON TABLE bitacora IS
    'Bitácora de cambios de catálogo y eventos relevantes del pipeline fiscalia.';
COMMENT ON COLUMN bitacora.id IS 'Identificador autoincremental del registro.';
COMMENT ON COLUMN bitacora.fecha IS 'Fecha en la que se detectó o aplicó el cambio.';
COMMENT ON COLUMN bitacora.tipo_cambio IS 'Tipo de cambio, p. ej. catalogo.';
COMMENT ON COLUMN bitacora.tabla_afectada IS 'Nombre de la tabla afectada por el cambio.';
COMMENT ON COLUMN bitacora.descripcion IS 'Descripción del cambio realizado.';
COMMENT ON COLUMN bitacora.referencia IS 'Referencia externa, p. ej. issue #332.';

INSERT INTO bitacora (fecha, tipo_cambio, tabla_afectada, descripcion, referencia)
VALUES (
    '2026-09-22',
    'catalogo',
    'delitos',
    'Se agregó el nuevo delito ''Violencia vicaria'' (id 17) al catálogo delitos, bajo el bien afectado ''La familia''. Detectado en el corte 01-08-2026, no existía en el catálogo previo y provocaba NotNullViolation en casos.delitos_id.',
    'issue #332'
);
