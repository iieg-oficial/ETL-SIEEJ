CREATE TABLE IF NOT EXISTS cat_serie_global (
    id     SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    tipo   TEXT NOT NULL
);

COMMENT ON TABLE cat_serie_global IS
    'Las 15 series sin desglose geográfico que SHF agrupa bajo la columna "Global" del archivo de datos abiertos.';
COMMENT ON COLUMN cat_serie_global.id IS
    'Identificador interno de la serie.';
COMMENT ON COLUMN cat_serie_global.nombre IS
    'Nombre de la serie tal como lo publica SHF (por ejemplo "Nacional", "Casa sola", "ZM Guadalajara").';
COMMENT ON COLUMN cat_serie_global.tipo IS
    'Concepto que agrupa a la serie: nacional, condicion (nueva/usada), tipo_vivienda, segmento o zona_metropolitana. '
    'SHF mezcla los cinco conceptos en una sola columna; esta clasificación permite consultarlos por separado.';
