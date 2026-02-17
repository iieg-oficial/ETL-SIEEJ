CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS cvegeo_municipalities (
    id SERIAL PRIMARY KEY,
    cvegeo INTEGER NOT NULL,
    cve_ent INTEGER NOT NULL,
    cve_mun INTEGER NOT NULL,
    nomgeo VARCHAR NOT NULL,
    nom_ent VARCHAR NOT NULL,
    geometry geometry(MULTIPOLYGON, 6372)
);

CREATE TABLE IF NOT EXISTS cvegeo_states (
    id SERIAL PRIMARY KEY,
    cve_ent INTEGER NOT NULL,
    nom_ent VARCHAR NOT NULL,
    geometry geometry(MULTIPOLYGON, 6372)
);
