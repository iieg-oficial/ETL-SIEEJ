CREATE TABLE IF NOT EXISTS cat_especies (
    id      INTEGER PRIMARY KEY,
    especie TEXT NOT NULL UNIQUE
);

COMMENT ON COLUMN cat_especies.id IS 'Código que identifica la especie ganadera en la fuente SIAP';
COMMENT ON COLUMN cat_especies.especie IS 'Nombre de la especie ganadera';


CREATE TABLE IF NOT EXISTS cat_productos (
    id       INTEGER PRIMARY KEY,
    producto TEXT NOT NULL
);

COMMENT ON COLUMN cat_productos.id IS 'Código que identifica el producto ganadero en la fuente SIAP';
COMMENT ON COLUMN cat_productos.producto IS 'Nombre del producto ganadero';


CREATE TABLE IF NOT EXISTS cat_distritos_des_rural (
    id            INTEGER PRIMARY KEY,
    dis_des_rural TEXT NOT NULL UNIQUE
);

COMMENT ON COLUMN cat_distritos_des_rural.id IS 'Código que identifica al Distrito de Desarrollo Rural';
COMMENT ON COLUMN cat_distritos_des_rural.dis_des_rural IS 'Nombre que identifica al Distrito de Desarrollo Rural';
