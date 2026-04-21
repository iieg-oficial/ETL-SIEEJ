CREATE TABLE IF NOT EXISTS paises (
    id   SERIAL PRIMARY KEY,
    codigo_pais VARCHAR(3) NOT NULL UNIQUE,
    nombre_pais TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS periodos (
    id                 INTEGER PRIMARY KEY,
    anio               INTEGER NOT NULL,
    trimestre          INTEGER NOT NULL,
    etiqueta_trimestre VARCHAR(7) NOT NULL
);

CREATE TABLE IF NOT EXISTS tipos_flujos_comerciales (
    id    INTEGER PRIMARY KEY,
    flujo TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS productos (
    id          INTEGER PRIMARY KEY,
    descripcion TEXT NOT NULL
);
