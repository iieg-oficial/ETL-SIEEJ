CREATE TABLE IF NOT EXISTS grados_marginacion (
    id INTEGER PRIMARY KEY,
    grado_marginacion TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS localidades (
    id              SERIAL PRIMARY KEY,
    cve_geo_id      INTEGER NOT NULL UNIQUE,
    clave_localidad INTEGER NOT NULL,
    municipio_id    INTEGER NOT NULL,
    entidad_id      INTEGER NOT NULL,
    localidad       TEXT,
    CONSTRAINT uq_localidades_clave UNIQUE (municipio_id, entidad_id, clave_localidad)
);
