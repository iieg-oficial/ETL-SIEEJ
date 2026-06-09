CREATE UNLOGGED TABLE IF NOT EXISTS stg_nacimientos (
    id                   SERIAL PRIMARY KEY,
    anio                 SMALLINT    NOT NULL,
    cve_geo              INTEGER     NOT NULL,
    edad_madre           SMALLINT    NOT NULL,
    tot_nac              INTEGER     NOT NULL,
    nac_padre_conocido   INTEGER     NOT NULL,
    nac_padre_18_mas     INTEGER     NOT NULL,
    nac_padre_25_mas     INTEGER     NOT NULL,
    fecha_actualizacion  DATE        NOT NULL,
    CONSTRAINT uq_nacimientos_anio_geo_edad
        UNIQUE (anio, cve_geo, edad_madre)
);
