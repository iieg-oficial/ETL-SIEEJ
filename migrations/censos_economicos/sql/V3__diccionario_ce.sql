-- Censos Economicos: tabla de diccionario de datos

CREATE TABLE stg_ce_diccionario_datos (
    id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    column_name VARCHAR(20) NOT NULL,
    description TEXT,
    data_type VARCHAR(50),
    length VARCHAR(20),
    valid_codes TEXT,
    CONSTRAINT uq_stg_ce_diccionario_key UNIQUE (year, column_name)
);
