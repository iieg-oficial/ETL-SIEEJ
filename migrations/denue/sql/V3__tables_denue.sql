CREATE TABLE IF NOT EXISTS establecimientos (
    id INTEGER NOT NULL,
    actualizacion_id INTEGER NOT NULL REFERENCES actualizaciones(id),
    nombre_establecimiento TEXT NOT NULL,
    razon_social TEXT,
    latitud FLOAT,
    longitud FLOAT,
    fecha_alta DATE,
    nombre_asentamiento TEXT,
    ageb TEXT,
    localidad_id INTEGER REFERENCES localidades(id),
    actividad_economica_id INTEGER REFERENCES actividades_economicas(id),
    rango_personal_id INTEGER REFERENCES rangos_personal(id),
    tipo_establecimiento_id INTEGER REFERENCES tipos_establecimientos(id),
    PRIMARY KEY (id, actualizacion_id)
);
