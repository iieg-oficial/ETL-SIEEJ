CREATE TABLE IF NOT EXISTS grupos_edafologicos (
    id SERIAL PRIMARY KEY,
    clave VARCHAR(20) NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    CONSTRAINT uq_grupos_edafologicos_clave UNIQUE (clave)
);

CREATE TABLE IF NOT EXISTS calificadores_edafologicos (
    id SERIAL PRIMARY KEY,
    clave VARCHAR(20) NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    CONSTRAINT uq_calificadores_edafologicos_clave UNIQUE (clave)
);

CREATE TABLE IF NOT EXISTS fuentes_limites_municipales (
    id INTEGER PRIMARY KEY,
    clave VARCHAR(20) NOT NULL,
    nombre_fuente VARCHAR(120) NOT NULL,
    descripcion TEXT NOT NULL,
    version VARCHAR(120) NOT NULL,
    procedencia TEXT,
    CONSTRAINT uq_fuentes_limites_municipales_clave UNIQUE (clave)
);
