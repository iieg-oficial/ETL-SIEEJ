CREATE TABLE IF NOT EXISTS iim_municipal (
    id                  SERIAL PRIMARY KEY,
    municipio_id        INTEGER NOT NULL,
    viv_totales         INTEGER,
    por_viv_remesas     FLOAT,
    por_viv_emigrantes  FLOAT,
    por_viv_reto        FLOAT,
    iim_dp2             FLOAT,
    grado_iim           TEXT,
    lugar_contexto_nacional INTEGER,
    fecha               INTEGER NOT NULL,
    CONSTRAINT uq_iim_municipal UNIQUE (municipio_id, fecha)
);

CREATE TABLE IF NOT EXISTS iim_estatal (
    id                  SERIAL PRIMARY KEY,
    entidad_id          INTEGER NOT NULL,
    viv_totales         INTEGER,
    por_viv_remesas     FLOAT,
    por_viv_emigrantes  FLOAT,
    por_viv_reto        FLOAT,
    iim_dp2             FLOAT,
    grado_iim           TEXT,
    lugar_contexto_nacional INTEGER,
    fecha               INTEGER NOT NULL,
    CONSTRAINT uq_iim_estatal UNIQUE (entidad_id, fecha)
);
