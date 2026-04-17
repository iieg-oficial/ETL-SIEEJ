CREATE TABLE IF NOT EXISTS marginaciones_municipales (
    id                              SERIAL PRIMARY KEY,
    municipio_id                    INTEGER NOT NULL,
    grado_marginacion_id            INTEGER REFERENCES grados_marginacion(id),
    pob_total                       FLOAT,
    porc_pob15_analfabeta           FLOAT,
    pob15_sin_educ_bas              FLOAT,
    porc_viv_sin_drenaje_ni_excusado FLOAT,
    porc_viv_sin_energia            FLOAT,
    porc_viv_sin_agua_entubada      FLOAT,
    porc_viv_piso_tierra            FLOAT,
    prom_ocup_por_cuarto            FLOAT,
    porc_pob_loc_menos5000_hab      FLOAT,
    pob_ocup_hasta_2_sal_min        FLOAT,
    indice_marginacion              FLOAT,
    indice_marginacion_normalizado  FLOAT,
    lugar_contexto_nacional         INTEGER,
    fecha_actualizacion             DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS marginaciones_estatales (
    id                               SERIAL PRIMARY KEY,
    entidad_id                       INTEGER NOT NULL,
    grado_marginacion_id             INTEGER REFERENCES grados_marginacion(id),
    pob_total                        FLOAT,
    porc_pob15_analfabeta            FLOAT,
    pob15_sin_educ_bas               FLOAT,
    porc_viv_sin_drenaje_ni_excusado FLOAT,
    porc_viv_sin_energia             FLOAT,
    porc_viv_sin_agua_entubada       FLOAT,
    porc_viv_piso_tierra             FLOAT,
    porc_viv_con_hacinamiento        FLOAT,
    porc_pob_loc_menos5000_hab       FLOAT,
    pob_ocup_hasta_2_sal_min         FLOAT,
    porc_viv_sin_refrigerador        FLOAT,
    indice_marginacion               FLOAT,
    indice_marginacion_normalizado   FLOAT,
    lugar_contexto_nacional          INTEGER,
    fecha_actualizacion              DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS marginaciones_localidades (
    id                               SERIAL PRIMARY KEY,
    localidad_id                     INTEGER NOT NULL REFERENCES localidades(id),
    grado_marginacion_id             INTEGER REFERENCES grados_marginacion(id),
    pob_total                        FLOAT,
    porc_pob15_analfabeta            FLOAT,
    porc_pob15_sin_educ_basica       FLOAT,
    porc_viv_sin_drenaje_ni_excusado FLOAT,
    porc_viv_sin_energia             FLOAT,
    porc_viv_sin_agua_entubada       FLOAT,
    porc_viv_piso_tierra             FLOAT,
    prom_ocup_por_cuarto             FLOAT,
    porc_viv_sin_refrigerador        FLOAT,
    indice_marginacion               FLOAT,
    indice_marginacion_normalizado   FLOAT,
    fecha_actualizacion              DATE NOT NULL
);
