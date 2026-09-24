CREATE TABLE IF NOT EXISTS cat_publicaciones (
    id          SERIAL    PRIMARY KEY,
    fecha_corte DATE      NOT NULL UNIQUE,
    archivo     TEXT      NOT NULL,
    url         TEXT      NOT NULL,
    modificado  TIMESTAMP NOT NULL
);

COMMENT ON TABLE cat_publicaciones IS
    'Cortes mensuales del Registro Estatal de Fosas Clandestinas publicados por la Fiscalía Especial en Personas Desaparecidas.';
COMMENT ON COLUMN cat_publicaciones.id IS 'Identificador de la publicación.';
COMMENT ON COLUMN cat_publicaciones.fecha_corte IS 'Mes de corte de los datos (primer día del mes), tomado del nombre del archivo.';
COMMENT ON COLUMN cat_publicaciones.archivo IS 'Nombre del PDF en el servidor de la Fiscalía.';
COMMENT ON COLUMN cat_publicaciones.url IS 'URL de descarga del PDF.';
COMMENT ON COLUMN cat_publicaciones.modificado IS 'Fecha de modificación del PDF según el listado del servidor.';
