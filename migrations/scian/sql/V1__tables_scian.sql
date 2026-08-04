CREATE TABLE IF NOT EXISTS sectores (
    id                     SERIAL PRIMARY KEY,
    codigo                 VARCHAR(5) NOT NULL UNIQUE,
    descripcion            TEXT       NOT NULL,
    comparable_trinacional BOOLEAN    NOT NULL
);

COMMENT ON TABLE  sectores IS 'Sectores del SCIAN Mexico 2023 (primer nivel, 2 digitos)';
COMMENT ON COLUMN sectores.codigo IS 'Clave del sector; algunos agrupan un rango de claves (31-33, 48-49)';
COMMENT ON COLUMN sectores.comparable_trinacional IS 'Categoria comparable con el NAICS de EUA y Canada';

CREATE TABLE IF NOT EXISTS subsectores (
    id                     SERIAL PRIMARY KEY,
    codigo                 VARCHAR(3) NOT NULL UNIQUE,
    descripcion            TEXT       NOT NULL,
    comparable_trinacional BOOLEAN    NOT NULL,
    sector_id              INTEGER    NOT NULL REFERENCES sectores(id)
);

COMMENT ON TABLE  subsectores IS 'Subsectores del SCIAN Mexico 2023 (segundo nivel, 3 digitos)';
COMMENT ON COLUMN subsectores.comparable_trinacional IS 'Categoria comparable con el NAICS de EUA y Canada';

CREATE TABLE IF NOT EXISTS ramas (
    id                     SERIAL PRIMARY KEY,
    codigo                 VARCHAR(4) NOT NULL UNIQUE,
    descripcion            TEXT       NOT NULL,
    comparable_trinacional BOOLEAN    NOT NULL,
    subsector_id           INTEGER    NOT NULL REFERENCES subsectores(id)
);

COMMENT ON TABLE  ramas IS 'Ramas del SCIAN Mexico 2023 (tercer nivel, 4 digitos)';
COMMENT ON COLUMN ramas.comparable_trinacional IS 'Categoria comparable con el NAICS de EUA y Canada';

CREATE TABLE IF NOT EXISTS subramas (
    id                     SERIAL PRIMARY KEY,
    codigo                 VARCHAR(5) NOT NULL UNIQUE,
    descripcion            TEXT       NOT NULL,
    comparable_trinacional BOOLEAN    NOT NULL,
    rama_id                INTEGER    NOT NULL REFERENCES ramas(id)
);

COMMENT ON TABLE  subramas IS 'Subramas del SCIAN Mexico 2023 (cuarto nivel, 5 digitos)';
COMMENT ON COLUMN subramas.comparable_trinacional IS 'Categoria comparable con el NAICS de EUA y Canada';

CREATE TABLE IF NOT EXISTS clases (
    id          SERIAL PRIMARY KEY,
    codigo      VARCHAR(6) NOT NULL UNIQUE,
    descripcion TEXT       NOT NULL,
    subrama_id  INTEGER    NOT NULL REFERENCES subramas(id)
);

COMMENT ON TABLE  clases IS 'Clases de actividad del SCIAN Mexico 2023 (quinto nivel, 6 digitos)';

CREATE INDEX IF NOT EXISTS idx_subsectores_sector ON subsectores (sector_id);
CREATE INDEX IF NOT EXISTS idx_ramas_subsector    ON ramas (subsector_id);
CREATE INDEX IF NOT EXISTS idx_subramas_rama      ON subramas (rama_id);
CREATE INDEX IF NOT EXISTS idx_clases_subrama     ON clases (subrama_id);
