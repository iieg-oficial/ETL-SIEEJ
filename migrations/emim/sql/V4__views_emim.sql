-- =============================================================================
-- V4__views_emim.sql  |  Pipeline: emim
-- vw_emim          -> las 32 entidades federativas
-- vw_emim_jalisco  -> solo Jalisco (cve_ent = 14)
-- =============================================================================

CREATE OR REPLACE VIEW vw_emim AS
SELECT
    se.fecha,
    se.entidad_id,
    e.nom_ent       AS entidad,
    se.codigo_actividad,
    ca.descripcion  AS actividad_descripcion,
    se.per_ocu_tot,
    se.horas_trabajadas,
    se.remuneraciones,
    se.valor_produccion,
    se.valor_ventas,
    se.estatus_id,
    ce.estatus,
    se.fecha_actualizacion
FROM stg_emim se
LEFT JOIN cvegeo_states e  ON e.cve_ent           = se.entidad_id
LEFT JOIN cat_actividad ca ON ca.codigo_actividad = se.codigo_actividad
LEFT JOIN cat_estatus ce   ON ce.id               = se.estatus_id;

COMMENT ON VIEW vw_emim IS
    'Vista desnormalizada de la Encuesta Mensual de la Industria Manufacturera (EMIM) del INEGI, Serie 2018, para las 32 entidades federativas, con periodicidad mensual desde enero de 2018. Publica valores absolutos, no índices.';
COMMENT ON COLUMN vw_emim.fecha IS
    'Primer día del mes de referencia de la información.';
COMMENT ON COLUMN vw_emim.entidad_id IS
    'Clave de la entidad federativa (1 a 32) según el Catálogo Único de Claves de Áreas Geoestadísticas del INEGI.';
COMMENT ON COLUMN vw_emim.entidad IS
    'Nombre de la entidad federativa a la que corresponden las cifras.';
COMMENT ON COLUMN vw_emim.codigo_actividad IS
    'Código de la actividad manufacturera en el clasificador SCIAN 2018. El sector se publica como el rango "31-33".';
COMMENT ON COLUMN vw_emim.actividad_descripcion IS
    'Nombre de la actividad manufacturera según el clasificador SCIAN 2018 (ej. Industria alimentaria).';
COMMENT ON COLUMN vw_emim.per_ocu_tot IS
    'Personal ocupado total, en NÚMERO DE PERSONAS: personal dependiente más no dependiente de la razón social. Considera hombres y mujeres.';
COMMENT ON COLUMN vw_emim.horas_trabajadas IS
    'Horas normales y extraordinarias efectivamente trabajadas por el personal ocupado total, en MILES DE HORAS.';
COMMENT ON COLUMN vw_emim.remuneraciones IS
    'Remuneraciones pagadas al personal dependiente de la razón social, en MILES DE PESOS CORRIENTES: todos los pagos y aportaciones, en dinero y especie, antes de cualquier deducción.';
COMMENT ON COLUMN vw_emim.valor_produccion IS
    'Total de valor de producción de los productos elaborados por el establecimiento con materias primas propias, en MILES DE PESOS CORRIENTES.';
COMMENT ON COLUMN vw_emim.valor_ventas IS
    'Total de valor de ventas, en MILES DE PESOS CORRIENTES: ingreso por la venta de los productos elaborados por el establecimiento con materias primas propias.';
COMMENT ON COLUMN vw_emim.estatus_id IS
    'Identificador del estatus de los datos en cat_estatus.';
COMMENT ON COLUMN vw_emim.estatus IS
    'Estatus de los datos: Cifras definitivas, Cifras revisadas o Cifras preliminares.';
COMMENT ON COLUMN vw_emim.fecha_actualizacion IS
    'Fecha en que el pipeline cargó o actualizó el registro en esta base.';


CREATE OR REPLACE VIEW vw_emim_jalisco AS
SELECT
    se.fecha,
    se.codigo_actividad,
    ca.descripcion  AS actividad_descripcion,
    se.per_ocu_tot,
    se.horas_trabajadas,
    se.remuneraciones,
    se.valor_produccion,
    se.valor_ventas,
    se.estatus_id,
    ce.estatus,
    se.fecha_actualizacion
FROM stg_emim se
LEFT JOIN cat_actividad ca ON ca.codigo_actividad = se.codigo_actividad
LEFT JOIN cat_estatus ce   ON ce.id               = se.estatus_id
WHERE se.entidad_id = 14;

COMMENT ON VIEW vw_emim_jalisco IS
    'Misma información que vw_emim, acotada a Jalisco (clave de entidad 14). La entidad se omite de las columnas porque es constante.';
COMMENT ON COLUMN vw_emim_jalisco.fecha IS
    'Primer día del mes de referencia de la información.';
COMMENT ON COLUMN vw_emim_jalisco.codigo_actividad IS
    'Código de la actividad manufacturera en el clasificador SCIAN 2018. El sector se publica como el rango "31-33".';
COMMENT ON COLUMN vw_emim_jalisco.actividad_descripcion IS
    'Nombre de la actividad manufacturera según el clasificador SCIAN 2018 (ej. Industria alimentaria).';
COMMENT ON COLUMN vw_emim_jalisco.per_ocu_tot IS
    'Personal ocupado total, en NÚMERO DE PERSONAS: personal dependiente más no dependiente de la razón social. Considera hombres y mujeres.';
COMMENT ON COLUMN vw_emim_jalisco.horas_trabajadas IS
    'Horas normales y extraordinarias efectivamente trabajadas por el personal ocupado total, en MILES DE HORAS.';
COMMENT ON COLUMN vw_emim_jalisco.remuneraciones IS
    'Remuneraciones pagadas al personal dependiente de la razón social, en MILES DE PESOS CORRIENTES: todos los pagos y aportaciones, en dinero y especie, antes de cualquier deducción.';
COMMENT ON COLUMN vw_emim_jalisco.valor_produccion IS
    'Total de valor de producción de los productos elaborados por el establecimiento con materias primas propias, en MILES DE PESOS CORRIENTES.';
COMMENT ON COLUMN vw_emim_jalisco.valor_ventas IS
    'Total de valor de ventas, en MILES DE PESOS CORRIENTES: ingreso por la venta de los productos elaborados por el establecimiento con materias primas propias.';
COMMENT ON COLUMN vw_emim_jalisco.estatus_id IS
    'Identificador del estatus de los datos en cat_estatus.';
COMMENT ON COLUMN vw_emim_jalisco.estatus IS
    'Estatus de los datos: Cifras definitivas, Cifras revisadas o Cifras preliminares.';
COMMENT ON COLUMN vw_emim_jalisco.fecha_actualizacion IS
    'Fecha en que el pipeline cargó o actualizó el registro en esta base.';
