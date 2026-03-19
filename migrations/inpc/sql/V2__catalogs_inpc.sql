CREATE TABLE IF NOT EXISTS ciudades (
    id   SERIAL PRIMARY KEY,
    ciudad VARCHAR(100) NOT NULL UNIQUE,
    entidad VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS objetos_gasto (
    id          INTEGER PRIMARY KEY,
    objeto_gasto VARCHAR(100) NOT NULL UNIQUE
);
