-- =============================================================================
-- V4__views_ems.sql  |  Pipeline: ems
-- vw_ems          -> las 32 entidades federativas
-- vw_ems_jalisco  -> solo Jalisco (cve_ent = 14)
-- =============================================================================

CREATE OR REPLACE VIEW vw_ems AS
SELECT
    se.fecha,
    se.entidad_id,
    e.nom_ent                    AS entidad,
    se.codigo_actividad,
    ca.descripcion               AS actividad_descripcion,
    se.ind_ingresos_bienes_serv,
    se.ind_gastos_consumo,
    se.per_ocu_tot,
    se.per_ocu_dependiente,
    se.per_ocu_no_dependiente,
    se.remuneraciones_tot,
    se.estatus_id,
    ce.estatus,
    se.fecha_actualizacion
FROM stg_ems se
LEFT JOIN cvegeo_states e  ON e.cve_ent           = se.entidad_id
LEFT JOIN cat_actividad ca ON ca.codigo_actividad = se.codigo_actividad
LEFT JOIN cat_estatus ce   ON ce.id               = se.estatus_id;

COMMENT ON VIEW vw_ems IS
    'Vista desnormalizada de la Encuesta Mensual de Servicios (EMS) del INEGI, Serie 2018, para las 32 entidades federativas, con periodicidad mensual desde enero de 2013. Todas las variables son índices con base 2018 = 100.';
COMMENT ON COLUMN vw_ems.fecha IS
    'Primer día del mes de referencia de la información.';
COMMENT ON COLUMN vw_ems.entidad_id IS
    'Clave de la entidad federativa (1 a 32) según el Catálogo Único de Claves de Áreas Geoestadísticas del INEGI.';
COMMENT ON COLUMN vw_ems.entidad IS
    'Nombre de la entidad federativa a la que corresponden las cifras.';
COMMENT ON COLUMN vw_ems.codigo_actividad IS
    'Código que identifica el sector de servicios bajo estudio, dentro del clasificador SCIAN 2018.';
COMMENT ON COLUMN vw_ems.actividad_descripcion IS
    'Nombre del sector de servicios según el clasificador SCIAN 2018 (ej. Servicios educativos).';
COMMENT ON COLUMN vw_ems.ind_ingresos_bienes_serv IS
    'Ingresos totales por suministro de bienes y servicios - Índice (Índice Base 2018 = 100): monto generado por la prestación de servicios durante el mes de referencia. Excluye ingresos financieros, subsidios y cuotas.';
COMMENT ON COLUMN vw_ems.ind_gastos_consumo IS
    'Gastos totales por consumo de bienes y servicios - Índice (Índice Base 2018 = 100): importe destinado al consumo de bienes y servicios para realizar la actividad económica. Excluye gastos fiscales, financieros y de inversión.';
COMMENT ON COLUMN vw_ems.per_ocu_tot IS
    'Personal ocupado total - Índice (Índice Base 2018 = 100): personal dependiente y no dependiente de la razón social.';
COMMENT ON COLUMN vw_ems.per_ocu_dependiente IS
    'Personal ocupado dependiente de la razón social - Índice (Índice Base 2018 = 100): personal contratado directamente por la razón social. Excluye pensionados y jubilados.';
COMMENT ON COLUMN vw_ems.per_ocu_no_dependiente IS
    'Personal no dependiente de la razón social - Índice (Índice Base 2018 = 100): personas que trabajaron para el establecimiento pero dependen contractualmente de otra razón social.';
COMMENT ON COLUMN vw_ems.remuneraciones_tot IS
    'Remuneraciones totales - Índice (Índice Base 2018 = 100): todos los pagos para retribuir el trabajo del personal dependiente y no dependiente de la razón social.';
COMMENT ON COLUMN vw_ems.estatus_id IS
    'Identificador del estatus de los datos en cat_estatus.';
COMMENT ON COLUMN vw_ems.estatus IS
    'Estatus de los datos: Cifras definitivas, Cifras revisadas o Cifras preliminares.';
COMMENT ON COLUMN vw_ems.fecha_actualizacion IS
    'Fecha en que el pipeline cargó o actualizó el registro en esta base.';


CREATE OR REPLACE VIEW vw_ems_jalisco AS
SELECT
    se.fecha,
    se.codigo_actividad,
    ca.descripcion               AS actividad_descripcion,
    se.ind_ingresos_bienes_serv,
    se.ind_gastos_consumo,
    se.per_ocu_tot,
    se.per_ocu_dependiente,
    se.per_ocu_no_dependiente,
    se.remuneraciones_tot,
    se.estatus_id,
    ce.estatus,
    se.fecha_actualizacion
FROM stg_ems se
LEFT JOIN cat_actividad ca ON ca.codigo_actividad = se.codigo_actividad
LEFT JOIN cat_estatus ce   ON ce.id               = se.estatus_id
WHERE se.entidad_id = 14;

COMMENT ON VIEW vw_ems_jalisco IS
    'Misma información que vw_ems, acotada a Jalisco (clave de entidad 14). La entidad se omite de las columnas porque es constante.';
COMMENT ON COLUMN vw_ems_jalisco.fecha IS
    'Primer día del mes de referencia de la información.';
COMMENT ON COLUMN vw_ems_jalisco.codigo_actividad IS
    'Código que identifica el sector de servicios bajo estudio, dentro del clasificador SCIAN 2018.';
COMMENT ON COLUMN vw_ems_jalisco.actividad_descripcion IS
    'Nombre del sector de servicios según el clasificador SCIAN 2018 (ej. Servicios educativos).';
COMMENT ON COLUMN vw_ems_jalisco.ind_ingresos_bienes_serv IS
    'Ingresos totales por suministro de bienes y servicios - Índice (Índice Base 2018 = 100): monto generado por la prestación de servicios durante el mes de referencia. Excluye ingresos financieros, subsidios y cuotas.';
COMMENT ON COLUMN vw_ems_jalisco.ind_gastos_consumo IS
    'Gastos totales por consumo de bienes y servicios - Índice (Índice Base 2018 = 100): importe destinado al consumo de bienes y servicios para realizar la actividad económica. Excluye gastos fiscales, financieros y de inversión.';
COMMENT ON COLUMN vw_ems_jalisco.per_ocu_tot IS
    'Personal ocupado total - Índice (Índice Base 2018 = 100): personal dependiente y no dependiente de la razón social.';
COMMENT ON COLUMN vw_ems_jalisco.per_ocu_dependiente IS
    'Personal ocupado dependiente de la razón social - Índice (Índice Base 2018 = 100): personal contratado directamente por la razón social. Excluye pensionados y jubilados.';
COMMENT ON COLUMN vw_ems_jalisco.per_ocu_no_dependiente IS
    'Personal no dependiente de la razón social - Índice (Índice Base 2018 = 100): personas que trabajaron para el establecimiento pero dependen contractualmente de otra razón social.';
COMMENT ON COLUMN vw_ems_jalisco.remuneraciones_tot IS
    'Remuneraciones totales - Índice (Índice Base 2018 = 100): todos los pagos para retribuir el trabajo del personal dependiente y no dependiente de la razón social.';
COMMENT ON COLUMN vw_ems_jalisco.estatus_id IS
    'Identificador del estatus de los datos en cat_estatus.';
COMMENT ON COLUMN vw_ems_jalisco.estatus IS
    'Estatus de los datos: Cifras definitivas, Cifras revisadas o Cifras preliminares.';
COMMENT ON COLUMN vw_ems_jalisco.fecha_actualizacion IS
    'Fecha en que el pipeline cargó o actualizó el registro en esta base.';
