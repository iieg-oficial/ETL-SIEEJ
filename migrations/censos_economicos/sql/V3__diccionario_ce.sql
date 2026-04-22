-- Censos Economicos: tabla de diccionario de datos

CREATE TABLE ce_diccionarios_datos (
    id SERIAL PRIMARY KEY,
    anio INTEGER NOT NULL,
    nombre_columna VARCHAR(20) NOT NULL,
    descripcion TEXT,
    tipo_dato VARCHAR(50),
    longitud VARCHAR(20),
    codigos_validos TEXT,
    CONSTRAINT uq_ce_diccionarios_datos_clave UNIQUE (anio, nombre_columna)
);
