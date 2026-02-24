CREATE TABLE IF NOT EXISTS casos (
    id SERIAL PRIMARY KEY,
    delitos_id INTEGER NOT NULL REFERENCES delitos(id),
    violencia_id INTEGER REFERENCES violencia(id),
    zonas_geograficas_id INTEGER REFERENCES zonas_geograficas(id),
    municipios_id INTEGER,
    colonias_id INTEGER REFERENCES colonias(id),
    calles_id INTEGER REFERENCES calles(id),
    cruces_id INTEGER REFERENCES cruces(id),
    hora VARCHAR(5),
    longitud FLOAT NOT NULL,
    latitud FLOAT NOT NULL,
    fecha_denuncia DATE NOT NULL,
    fecha_actualizacion DATE NOT NULL,
    CONSTRAINT uq_casos_natural_key UNIQUE (delitos_id, fecha_denuncia, longitud, latitud)
);
