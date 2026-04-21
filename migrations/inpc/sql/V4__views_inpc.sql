CREATE OR REPLACE VIEW v_inpc_ciudades AS
SELECT
    ic.id,
    c.ciudad,
    c.entidad,
    og.objeto_gasto,
    ic.fecha,
    ic.indice_de_precios,
    ic.fecha_actualizacion
FROM inpc_ciudades ic
LEFT JOIN ciudades c
    ON ic.ciudad_id = c.id
LEFT JOIN objetos_gasto og
    ON ic.objeto_gasto_id = og.id;

CREATE OR REPLACE VIEW v_inpc_entidades AS
SELECT
    ie.id,
    cs.nom_ent AS entidad,
    cs.cve_ent,
    og.objeto_gasto,
    ie.fecha,
    ie.indice_de_precios,
    ie.fecha_actualizacion
FROM inpc_entidades ie
LEFT JOIN cvegeo_states cs
    ON ie.entidad_id = cs.cve_ent
LEFT JOIN objetos_gasto og
    ON ie.objeto_gasto_id = og.id;

CREATE OR REPLACE VIEW v_inpc_nacional AS
SELECT
    n.id,
    og.objeto_gasto,
    n.fecha,
    n.indice_de_precios,
    n.fecha_actualizacion
FROM inpc_nacional n
LEFT JOIN objetos_gasto og
    ON n.objeto_gasto_id = og.id;
