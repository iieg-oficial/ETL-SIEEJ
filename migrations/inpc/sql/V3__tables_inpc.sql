CREATE TABLE IF NOT EXISTS inpc_ciudades (
    id                  SERIAL PRIMARY KEY,
    ciudad_id           INTEGER NOT NULL REFERENCES ciudades(id),
    fecha               DATE NOT NULL,
    objeto_gasto_id     INTEGER NOT NULL REFERENCES objetos_gasto(id),
    indice_de_precios   FLOAT,
    fecha_actualizacion DATE NOT NULL,
    CONSTRAINT uq_inpc_ciudades UNIQUE (ciudad_id, fecha, objeto_gasto_id)
);

CREATE TABLE IF NOT EXISTS inpc_entidades (
    id                  SERIAL PRIMARY KEY,
    entidad_id          INTEGER NOT NULL,
    fecha               DATE NOT NULL,
    objeto_gasto_id     INTEGER NOT NULL REFERENCES objetos_gasto(id),
    indice_de_precios   FLOAT,
    fecha_actualizacion DATE NOT NULL,
    CONSTRAINT uq_inpc_entidades UNIQUE (entidad_id, fecha, objeto_gasto_id)
);

CREATE TABLE IF NOT EXISTS inpc_nacional (
    id                  SERIAL PRIMARY KEY,
    fecha               DATE NOT NULL,
    objeto_gasto_id     INTEGER NOT NULL REFERENCES objetos_gasto(id),
    indice_de_precios   FLOAT,
    fecha_actualizacion DATE NOT NULL,
    CONSTRAINT uq_inpc_nacional UNIQUE (fecha, objeto_gasto_id)
);
