CREATE TABLE IF NOT EXISTS stg_participacion (
    id SERIAL PRIMARY KEY,
    entidad_id INTEGER NOT NULL,
    municipio_id INTEGER NOT NULL,
    porc_participacion FLOAT NOT NULL,
    anio INTEGER NOT NULL
);
