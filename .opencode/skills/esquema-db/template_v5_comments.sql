-- Table comments for AI Agent context retrieval.
-- Each COMMENT ON TABLE describes the purpose and source of the table.
-- Each COMMENT ON COLUMN describes the meaning, format, and relationships of the column.

-- Catalogs
COMMENT ON TABLE cat_{catalogo} IS 'Descripción del catálogo y su propósito en el pipeline.';
COMMENT ON COLUMN cat_{catalogo}.id IS 'Identificador único del catálogo.';
COMMENT ON COLUMN cat_{catalogo}.{columna} IS 'Descripción de la columna.';

-- Staging table
COMMENT ON TABLE stg_{flujo} IS 'Descripción de la tabla de staging, su contenido y fuente de datos.';
COMMENT ON COLUMN stg_{flujo}.id IS 'Identificador único autogenerado para cada registro.';
COMMENT ON COLUMN stg_{flujo}.{columna} IS 'Descripción de la columna, su formato y relaciones.';
