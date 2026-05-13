CREATE TABLE IF NOT EXISTS stg_agricola (
    id                      SERIAL PRIMARY KEY,
    anio                    INTEGER NOT NULL,
    entidad_id              INTEGER,
    municipio_id            INTEGER,
    distrito_des_rural_id   INTEGER REFERENCES cat_distritos_des_rural(id),
    ctr_apoyo_des_rural_id  INTEGER REFERENCES cat_ctrs_apoyo_des_rural(id),
    tipo_ciclo_id           INTEGER REFERENCES cat_ciclos(id),
    modalidad_id            INTEGER REFERENCES cat_modalidades(id),
    unidad_med_id           INTEGER REFERENCES cat_unidades_medida(id),
    cultivo_id              INTEGER REFERENCES cat_cultivos(id),
    sup_sembrada            FLOAT,
    sup_cosechada           FLOAT,
    sup_siniestrada         FLOAT,
    volumen_produccion      FLOAT,
    rendimiento             FLOAT,
    precio_med_rural        FLOAT,
    valor_produccion        FLOAT,
    CONSTRAINT uq_stg_agricola UNIQUE (
        anio, entidad_id, municipio_id, distrito_des_rural_id,
        ctr_apoyo_des_rural_id, cultivo_id, tipo_ciclo_id, modalidad_id
    )
);

COMMENT ON COLUMN stg_agricola.distrito_des_rural_id IS 'Código que identifica al Distrito de Desarrollo Rural';
COMMENT ON COLUMN stg_agricola.ctr_apoyo_des_rural_id IS 'Código que identifica al Centro de Apoyo al Desarrollo Rural';
COMMENT ON COLUMN stg_agricola.tipo_ciclo_id IS 'Código que identifica al ciclo agrícola';
COMMENT ON COLUMN stg_agricola.modalidad_id IS 'Código que identifica al tipo de modalidad hídrica';
COMMENT ON COLUMN stg_agricola.unidad_med_id IS 'Código que identifica la unidad de medida';
COMMENT ON COLUMN stg_agricola.cultivo_id IS 'Código que identifica al cultivo agrícola';
COMMENT ON COLUMN stg_agricola.sup_sembrada IS 'Superficie sembrada del cultivo. La unidad de medida son hectáreas';
COMMENT ON COLUMN stg_agricola.sup_cosechada IS 'Superficie cosechada del cultivo';
COMMENT ON COLUMN stg_agricola.sup_siniestrada IS 'Superficie siniestrada del cultivo. La unidad de medida son hectáreas';
COMMENT ON COLUMN stg_agricola.volumen_produccion IS 'Volumen de producción de la superficie cosechada cuya unidad de medida son las toneladas, con excepción del maguey pulquero y trigo ornamental, con una métrica de miles de litros y gruesas, respectivamente.';
COMMENT ON COLUMN stg_agricola.rendimiento IS 'La unidad de medida son toneladas por hectárea, con excepción de los cultivos que tienen otra métrica la cual se señala en el nombre del cultivo (gruesa, manojo, planta, entre otros).';
COMMENT ON COLUMN stg_agricola.precio_med_rural IS 'Precio medio rural, la unidad de medida son pesos por tonelada, con excepción de los cultivos que tienen otra métrica la cual se señala en el nombre del cultivo (gruesa, manojo, planta, entre otros).';
COMMENT ON COLUMN stg_agricola.valor_produccion IS 'Valor expresado en pesos corrientes nacionales.';
