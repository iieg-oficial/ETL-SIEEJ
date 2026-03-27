CREATE TABLE IF NOT EXISTS poblacion (
    id                  SERIAL PRIMARY KEY,
    entidad_id          INTEGER NOT NULL,
    municipio_id        INTEGER NOT NULL,
    localidad_id        INTEGER REFERENCES localidades (id),
    fuente_id           INTEGER NOT NULL REFERENCES fuentes (id),
    total               INTEGER NOT NULL,
    total_mujeres       INTEGER,
    total_hombres       INTEGER,
    viviendas_habitadas INTEGER
);
