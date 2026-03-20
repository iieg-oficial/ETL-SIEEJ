CREATE TABLE IF NOT EXISTS flujo_comercio (
    id              SERIAL PRIMARY KEY,
    pais_id         INTEGER NOT NULL REFERENCES paises(id),
    entidad_id      INTEGER NOT NULL,
    periodo_id      INTEGER NOT NULL REFERENCES periodos(id),
    tipo_flujo_id   INTEGER NOT NULL REFERENCES tipos_flujos_comerciales(id),
    producto_id     INTEGER NOT NULL REFERENCES productos(id),
    valor_comercio  FLOAT NOT NULL
);
