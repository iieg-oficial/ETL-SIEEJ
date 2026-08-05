-- =============================================================================
-- V3__tables_emim.sql  |  Pipeline: emim
-- Tabla staging de la Encuesta Mensual de la Industria Manufacturera (EMIM),
-- Serie 2018, VALORES ABSOLUTOS por entidad federativa y subsector.
-- =============================================================================

CREATE TABLE IF NOT EXISTS stg_emim (
    id                  SERIAL PRIMARY KEY,
    fecha               DATE    NOT NULL,
    entidad_id          INTEGER NOT NULL,
    codigo_actividad    TEXT    NOT NULL REFERENCES cat_actividad(codigo_actividad),
    per_ocu_tot         INTEGER,
    horas_trabajadas    DOUBLE PRECISION,
    remuneraciones      BIGINT,
    valor_produccion    BIGINT,
    valor_ventas        BIGINT,
    estatus_id          INTEGER REFERENCES cat_estatus(id),
    fecha_actualizacion DATE    NOT NULL,
    CONSTRAINT uq_stg_emim UNIQUE (fecha, entidad_id, codigo_actividad)
);

COMMENT ON TABLE stg_emim IS
    'Encuesta Mensual de la Industria Manufacturera (EMIM) del INEGI, Serie 2018, información mensual desde enero de 2018. La unidad de observación es el establecimiento manufacturero. A DIFERENCIA de EMEC y EMS, este conjunto publica VALORES ABSOLUTOS y no índices base 2018 = 100. Grano: un registro por periodo, entidad federativa y actividad manufacturera (el sector 31-33 y sus 21 subsectores).';

COMMENT ON COLUMN stg_emim.id IS
    'Identificador único del registro. Asignado por la base, no proviene de la fuente.';
COMMENT ON COLUMN stg_emim.fecha IS
    'Primer día del mes de referencia de la información, derivado de los campos ANIO y MES de la fuente.';
COMMENT ON COLUMN stg_emim.entidad_id IS
    'Clave de la entidad federativa (1 a 32) según el Catálogo Único de Claves de Áreas Geoestadísticas del INEGI, tomada directamente del campo CODIGO_ENTIDAD de la fuente. Ref. cvegeo_states.cve_ent.';
COMMENT ON COLUMN stg_emim.codigo_actividad IS
    'Código que identifica las diversas actividades económicas bajo estudio (sector, subsector, rama o clase). El valor que se presenta es un código dentro del clasificador SCIAN 2018. Es TEXTO: el sector manufacturero se publica como el rango "31-33". FK a cat_actividad.codigo_actividad.';
COMMENT ON COLUMN stg_emim.per_ocu_tot IS
    'Personal ocupado total, en NÚMERO DE PERSONAS. Comprende al personal ocupado dependiente de la razón social más el personal no dependiente de la razón social. Considera hombres y mujeres.';
COMMENT ON COLUMN stg_emim.horas_trabajadas IS
    'Horas trabajadas por el personal ocupado total, en MILES DE HORAS. Comprende las horas normales y extraordinarias efectivamente trabajadas por el personal ocupado total. Considera las horas trabajadas por los hombres y las mujeres.';
COMMENT ON COLUMN stg_emim.remuneraciones IS
    'Remuneraciones pagadas al personal dependiente de la razón social, en MILES DE PESOS CORRIENTES. Son todos los pagos y aportaciones normales y extraordinarias que realizó el establecimiento, en dinero y especie, antes de cualquier deducción, para retribuir el trabajo del personal remunerado dependiente de la razón social, en forma de salarios, sueldos, prestaciones sociales y utilidades repartidas, ya sea que este pago se calcule sobre la base de una jornada de trabajo o por la cantidad de trabajo desarrollado (destajo) o mediante un salario base que se complementa con comisiones por ventas u otros conceptos como: bonos, premios, compensaciones, etc.';
COMMENT ON COLUMN stg_emim.valor_produccion IS
    'Total de valor de producción de los productos elaborados, en MILES DE PESOS CORRIENTES. Es el valor de los productos elaborados por el establecimiento con materias primas propias, ya sea en la propia unidad económica o mediante la contratación de servicios de maquila.';
COMMENT ON COLUMN stg_emim.valor_ventas IS
    'Total de valor de ventas de los productos elaborados, en MILES DE PESOS CORRIENTES. Es el ingreso por la venta de los productos elaborados por el establecimiento con materias primas propias.';
COMMENT ON COLUMN stg_emim.estatus_id IS
    'FK a cat_estatus; indica si el registro corresponde a cifras definitivas, revisadas o preliminares.';
COMMENT ON COLUMN stg_emim.fecha_actualizacion IS
    'Fecha en que el pipeline cargó o actualizó el registro en esta base. No proviene de la fuente.';
