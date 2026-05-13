CREATE TABLE IF NOT EXISTS stg_ganadera (
    id                    SERIAL PRIMARY KEY,
    anio                  INTEGER NOT NULL,
    entidad_id            INTEGER,
    municipio_id          INTEGER,
    distrito_des_rural_id INTEGER REFERENCES cat_distritos_des_rural(id),
    especie_id            INTEGER REFERENCES cat_especies(id),
    producto_id           INTEGER REFERENCES cat_productos(id),
    volumen_produccion    FLOAT,
    peso_sacrificio       FLOAT,
    precio_med_rural      FLOAT,
    valor_produccion      FLOAT,
    animales_sacrificados FLOAT,
    CONSTRAINT uq_stg_ganadera UNIQUE (
        anio, entidad_id, municipio_id, distrito_des_rural_id,
        especie_id, producto_id
    )
);

COMMENT ON COLUMN stg_ganadera.entidad_id IS 'Clave de la entidad federativa (ref. cvegeo_states)';
COMMENT ON COLUMN stg_ganadera.municipio_id IS 'Clave municipal (ref. cvegeo_municipalities)';
COMMENT ON COLUMN stg_ganadera.distrito_des_rural_id IS 'Código que identifica al Distrito de Desarrollo Rural';
COMMENT ON COLUMN stg_ganadera.especie_id IS 'Código que identifica la especie ganadera';
COMMENT ON COLUMN stg_ganadera.producto_id IS 'Código que identifica el producto ganadero';
COMMENT ON COLUMN stg_ganadera.volumen_produccion IS 'Volumen de producción. Unidad de medida: toneladas';
COMMENT ON COLUMN stg_ganadera.peso_sacrificio IS 'Peso en canal de los animales sacrificados. Unidad de medida: toneladas';
COMMENT ON COLUMN stg_ganadera.precio_med_rural IS 'Precio medio rural. Unidad de medida: pesos por tonelada';
COMMENT ON COLUMN stg_ganadera.valor_produccion IS 'Valor de la producción expresado en pesos corrientes nacionales';
COMMENT ON COLUMN stg_ganadera.animales_sacrificados IS 'Número de animales sacrificados en el periodo';
