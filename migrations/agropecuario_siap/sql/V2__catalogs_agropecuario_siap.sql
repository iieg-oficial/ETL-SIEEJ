CREATE TABLE IF NOT EXISTS cat_cultivos (
    id          SERIAL PRIMARY KEY,
    codigo_siap INTEGER,
    cultivo     TEXT NOT NULL UNIQUE
);

COMMENT ON COLUMN cat_cultivos.codigo_siap IS 'Código original del cultivo en la fuente SIAP';
COMMENT ON COLUMN cat_cultivos.cultivo IS 'Nombre del cultivo agrícola';


CREATE TABLE IF NOT EXISTS cat_unidades_medida (
    id         INTEGER PRIMARY KEY,
    unidad_med TEXT NOT NULL UNIQUE
);

COMMENT ON COLUMN cat_unidades_medida.id IS 'Código que identifica la unidad de medida';
COMMENT ON COLUMN cat_unidades_medida.unidad_med IS 'Nombre que identifica la unidad de medida';


CREATE TABLE IF NOT EXISTS cat_modalidades (
    id        INTEGER PRIMARY KEY,
    modalidad TEXT NOT NULL UNIQUE
);

COMMENT ON COLUMN cat_modalidades.id IS 'Código que identifica al tipo de modalidad hídrica';
COMMENT ON COLUMN cat_modalidades.modalidad IS 'Nombre de la modalidad hídrica';


CREATE TABLE IF NOT EXISTS cat_ciclos (
    id         INTEGER PRIMARY KEY,
    tipo_ciclo TEXT NOT NULL UNIQUE
);

COMMENT ON COLUMN cat_ciclos.id IS 'Código que identifica al ciclo agrícola';
COMMENT ON COLUMN cat_ciclos.tipo_ciclo IS 'Nombre del ciclo agrícola';


CREATE TABLE IF NOT EXISTS cat_ctrs_apoyo_des_rural (
    id                  SERIAL PRIMARY KEY,
    codigo_siap         INTEGER,
    ctr_apoyo_des_rural TEXT NOT NULL UNIQUE
);

COMMENT ON COLUMN cat_ctrs_apoyo_des_rural.codigo_siap IS 'Código original del CADER en la fuente SIAP';
COMMENT ON COLUMN cat_ctrs_apoyo_des_rural.ctr_apoyo_des_rural IS 'Nombre que identifica al Centro de Apoyo al Desarrollo Rural';


CREATE TABLE IF NOT EXISTS cat_distritos_des_rural (
    id            INTEGER PRIMARY KEY,
    dis_des_rural TEXT NOT NULL UNIQUE
);

COMMENT ON COLUMN cat_distritos_des_rural.id IS 'Código que identifica al Distrito de Desarrollo Rural';
COMMENT ON COLUMN cat_distritos_des_rural.dis_des_rural IS 'Nombre que identifica al Distrito de Desarrollo Rural';
