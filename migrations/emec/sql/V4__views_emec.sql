-- =============================================================================
-- V4__views_emec.sql  |  Pipeline: emec
-- vw_emec          -> las 32 entidades federativas
-- vw_emec_jalisco  -> solo Jalisco (cve_ent = 14)
-- =============================================================================

CREATE OR REPLACE VIEW vw_emec AS
SELECT
    se.fecha,
    se.entidad_id,
    e.nom_ent                    AS entidad,
    se.codigo_actividad,
    ca.descripcion               AS actividad_descripcion,
    se.per_ocu_tot,
    se.remuneraciones_tot,
    se.remuneraciones_media,
    se.ind_ingresos_bienes_serv,
    se.ind_compras_reventa,
    se.estatus_id,
    ce.estatus,
    se.fecha_actualizacion
FROM stg_emec se
LEFT JOIN cvegeo_states e  ON e.cve_ent           = se.entidad_id
LEFT JOIN cat_actividad ca ON ca.codigo_actividad = se.codigo_actividad
LEFT JOIN cat_estatus ce   ON ce.id               = se.estatus_id;

COMMENT ON VIEW vw_emec IS
    'Vista desnormalizada de la Encuesta Mensual sobre Empresas Comerciales (EMEC) del INEGI, Serie 2018, para las 32 entidades federativas, con periodicidad mensual desde enero de 2008. Todas las variables son índices con base 2018 = 100.';
COMMENT ON COLUMN vw_emec.fecha IS
    'Primer día del mes de referencia de la información.';
COMMENT ON COLUMN vw_emec.entidad_id IS
    'Clave de la entidad federativa (1 a 32) según el Catálogo Único de Claves de Áreas Geoestadísticas del INEGI.';
COMMENT ON COLUMN vw_emec.entidad IS
    'Nombre de la entidad federativa a la que corresponden las cifras.';
COMMENT ON COLUMN vw_emec.codigo_actividad IS
    'Código que identifica las diversas actividades económicas bajo estudio. El valor que se presenta es un código dentro del clasificador SCIAN 2013.';
COMMENT ON COLUMN vw_emec.actividad_descripcion IS
    'Nombre de la actividad económica según el clasificador SCIAN 2013 (ej. Comercio al por mayor, Comercio al por menor).';
COMMENT ON COLUMN vw_emec.per_ocu_tot IS
    'Personal ocupado total - Índice (Índice Base 2018 = 100): total de personal dependiente y no dependiente de la razón social que trabajó para la empresa comercial cubriendo como mínimo una tercera parte de la jornada laboral. Excluye pensionados y jubilados.';
COMMENT ON COLUMN vw_emec.remuneraciones_tot IS
    'Remuneraciones totales - Índice (Índice Base 2018 = 100): todos los pagos y aportaciones en dinero y especie, antes de cualquier deducción, para retribuir el trabajo del personal dependiente de la razón social.';
COMMENT ON COLUMN vw_emec.remuneraciones_media IS
    'Remuneración media - Índice (Índice Base 2018 = 100): resultado de dividir las remuneraciones totales entre el total de personal remunerado dependiente de la razón social.';
COMMENT ON COLUMN vw_emec.ind_ingresos_bienes_serv IS
    'Ingresos totales por suministro de bienes y servicios - Índice (Índice Base 2018 = 100): monto obtenido por la empresa por sus actividades de producción, comercialización o prestación de servicios en el mes de referencia. Excluye ingresos financieros, subsidios y cuotas.';
COMMENT ON COLUMN vw_emec.ind_compras_reventa IS
    'Mercancías compradas para su reventa sin transformación - Índice (Índice Base 2018 = 100): valor de las mercancías que compró la empresa comercial para venderlas en las mismas condiciones en que las adquirió. Excluye las mercancías recibidas en consignación.';
COMMENT ON COLUMN vw_emec.estatus_id IS
    'Identificador del estatus de los datos en cat_estatus.';
COMMENT ON COLUMN vw_emec.estatus IS
    'Estatus de los datos: Cifras definitivas, Cifras revisadas o Cifras preliminares.';
COMMENT ON COLUMN vw_emec.fecha_actualizacion IS
    'Fecha en que el pipeline cargó o actualizó el registro en esta base.';


CREATE OR REPLACE VIEW vw_emec_jalisco AS
SELECT
    se.fecha,
    se.codigo_actividad,
    ca.descripcion               AS actividad_descripcion,
    se.per_ocu_tot,
    se.remuneraciones_tot,
    se.remuneraciones_media,
    se.ind_ingresos_bienes_serv,
    se.ind_compras_reventa,
    se.estatus_id,
    ce.estatus,
    se.fecha_actualizacion
FROM stg_emec se
LEFT JOIN cat_actividad ca ON ca.codigo_actividad = se.codigo_actividad
LEFT JOIN cat_estatus ce   ON ce.id               = se.estatus_id
WHERE se.entidad_id = 14;

COMMENT ON VIEW vw_emec_jalisco IS
    'Misma información que vw_emec, acotada a Jalisco (clave de entidad 14). La entidad se omite de las columnas porque es constante.';
COMMENT ON COLUMN vw_emec_jalisco.fecha IS
    'Primer día del mes de referencia de la información.';
COMMENT ON COLUMN vw_emec_jalisco.codigo_actividad IS
    'Código que identifica las diversas actividades económicas bajo estudio. El valor que se presenta es un código dentro del clasificador SCIAN 2013.';
COMMENT ON COLUMN vw_emec_jalisco.actividad_descripcion IS
    'Nombre de la actividad económica según el clasificador SCIAN 2013 (ej. Comercio al por mayor, Comercio al por menor).';
COMMENT ON COLUMN vw_emec_jalisco.per_ocu_tot IS
    'Personal ocupado total - Índice (Índice Base 2018 = 100): total de personal dependiente y no dependiente de la razón social que trabajó para la empresa comercial cubriendo como mínimo una tercera parte de la jornada laboral. Excluye pensionados y jubilados.';
COMMENT ON COLUMN vw_emec_jalisco.remuneraciones_tot IS
    'Remuneraciones totales - Índice (Índice Base 2018 = 100): todos los pagos y aportaciones en dinero y especie, antes de cualquier deducción, para retribuir el trabajo del personal dependiente de la razón social.';
COMMENT ON COLUMN vw_emec_jalisco.remuneraciones_media IS
    'Remuneración media - Índice (Índice Base 2018 = 100): resultado de dividir las remuneraciones totales entre el total de personal remunerado dependiente de la razón social.';
COMMENT ON COLUMN vw_emec_jalisco.ind_ingresos_bienes_serv IS
    'Ingresos totales por suministro de bienes y servicios - Índice (Índice Base 2018 = 100): monto obtenido por la empresa por sus actividades de producción, comercialización o prestación de servicios en el mes de referencia. Excluye ingresos financieros, subsidios y cuotas.';
COMMENT ON COLUMN vw_emec_jalisco.ind_compras_reventa IS
    'Mercancías compradas para su reventa sin transformación - Índice (Índice Base 2018 = 100): valor de las mercancías que compró la empresa comercial para venderlas en las mismas condiciones en que las adquirió. Excluye las mercancías recibidas en consignación.';
COMMENT ON COLUMN vw_emec_jalisco.estatus_id IS
    'Identificador del estatus de los datos en cat_estatus.';
COMMENT ON COLUMN vw_emec_jalisco.estatus IS
    'Estatus de los datos: Cifras definitivas, Cifras revisadas o Cifras preliminares.';
COMMENT ON COLUMN vw_emec_jalisco.fecha_actualizacion IS
    'Fecha en que el pipeline cargó o actualizó el registro en esta base.';
