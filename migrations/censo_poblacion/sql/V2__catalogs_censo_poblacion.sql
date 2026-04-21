CREATE TABLE IF NOT EXISTS localidades (
    id      INTEGER PRIMARY KEY,
    localidad TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fuentes (
    id          INTEGER PRIMARY KEY,
    descripcion TEXT    NOT NULL,
    fecha       INTEGER NOT NULL
);
