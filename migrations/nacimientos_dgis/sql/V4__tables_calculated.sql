CREATE TABLE IF NOT EXISTS stg_tasa_fecundidad (
    fecha             DATE,
    entidad_id        CHAR(2),
    municipio_id      CHAR(5),
    pob_mujeres_15_49 INTEGER,
    nacimientos       INTEGER,
    tasa_fec_gen      NUMERIC(12,2)
);

CREATE TABLE IF NOT EXISTS stg_nacimientos_adolescentes (
    fecha                                DATE,
    entidad_id                           CHAR(2),
    municipio_id                         CHAR(5),
    nac_madres_10_14                     NUMERIC(12,2),
    tasa_esp_fec_madres_10_14            NUMERIC(12,2),
    pct_padres_18_mas_madres_10_14       NUMERIC(12,2),
    pct_edad_padre_sin_dato_madres_10_14 NUMERIC(12,2),
    nac_madres_15_19                     NUMERIC(12,2),
    tasa_esp_fec_madres_15_19            NUMERIC(12,2),
    pct_padres_25_mas_madres_15_19       NUMERIC(12,2),
    pct_edad_padre_sin_dato_madres_15_19 NUMERIC(12,2)
);
