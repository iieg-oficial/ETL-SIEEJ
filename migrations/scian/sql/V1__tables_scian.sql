CREATE TABLE IF NOT EXISTS sectores (
    id                     SERIAL PRIMARY KEY,
    codigo                 VARCHAR(5) NOT NULL UNIQUE,
    descripcion            TEXT       NOT NULL,
    comparable_trinacional BOOLEAN    NOT NULL
);

CREATE TABLE IF NOT EXISTS subsectores (
    id                     SERIAL PRIMARY KEY,
    codigo                 VARCHAR(3) NOT NULL UNIQUE,
    descripcion            TEXT       NOT NULL,
    comparable_trinacional BOOLEAN    NOT NULL,
    sector_id              INTEGER    NOT NULL REFERENCES sectores(id)
);

CREATE TABLE IF NOT EXISTS ramas (
    id                     SERIAL PRIMARY KEY,
    codigo                 VARCHAR(4) NOT NULL UNIQUE,
    descripcion            TEXT       NOT NULL,
    comparable_trinacional BOOLEAN    NOT NULL,
    subsector_id           INTEGER    NOT NULL REFERENCES subsectores(id)
);

CREATE TABLE IF NOT EXISTS subramas (
    id                     SERIAL PRIMARY KEY,
    codigo                 VARCHAR(5) NOT NULL UNIQUE,
    descripcion            TEXT       NOT NULL,
    comparable_trinacional BOOLEAN    NOT NULL,
    rama_id                INTEGER    NOT NULL REFERENCES ramas(id)
);

CREATE TABLE IF NOT EXISTS clases (
    id          SERIAL PRIMARY KEY,
    codigo      VARCHAR(6) NOT NULL UNIQUE,
    descripcion TEXT       NOT NULL,
    subrama_id  INTEGER    NOT NULL REFERENCES subramas(id)
);

CREATE INDEX IF NOT EXISTS idx_subsectores_sector ON subsectores (sector_id);
CREATE INDEX IF NOT EXISTS idx_ramas_subsector    ON ramas (subsector_id);
CREATE INDEX IF NOT EXISTS idx_subramas_rama      ON subramas (rama_id);
CREATE INDEX IF NOT EXISTS idx_clases_subrama     ON clases (subrama_id);
