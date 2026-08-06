-- =============================================================================
-- V3__tables_ems.sql  |  Pipeline: ems
-- Tabla staging de la Encuesta Mensual de Servicios (EMS), Serie 2018,
-- índices base 2018 = 100, cobertura por entidad federativa.
-- =============================================================================

CREATE TABLE IF NOT EXISTS stg_ems (
    id                       SERIAL PRIMARY KEY,
    fecha                    DATE    NOT NULL,
    entidad_id               INTEGER NOT NULL,
    codigo_actividad         INTEGER NOT NULL REFERENCES cat_actividad(codigo_actividad),
    ind_ingresos_bienes_serv DOUBLE PRECISION,
    ind_gastos_consumo       DOUBLE PRECISION,
    per_ocu_tot              DOUBLE PRECISION,
    per_ocu_dependiente      DOUBLE PRECISION,
    per_ocu_no_dependiente   DOUBLE PRECISION,
    remuneraciones_tot       DOUBLE PRECISION,
    estatus_id               INTEGER REFERENCES cat_estatus(id),
    fecha_actualizacion      DATE    NOT NULL,
    CONSTRAINT uq_stg_ems UNIQUE (fecha, entidad_id, codigo_actividad)
);

COMMENT ON TABLE stg_ems IS
    'Encuesta Mensual de Servicios (EMS) del INEGI, Serie 2018, información mensual desde enero de 2013. Proporciona información estadística económica de coyuntura sobre las unidades económicas de los servicios privados no financieros. Todas las variables son ÍNDICES con base 2018 = 100, no valores absolutos. Grano: un registro por periodo, entidad federativa y sector de servicios.';

COMMENT ON COLUMN stg_ems.id IS
    'Identificador único del registro. Asignado por la base, no proviene de la fuente.';
COMMENT ON COLUMN stg_ems.fecha IS
    'Primer día del mes de referencia de la información, derivado de los campos ANIO y MES de la fuente.';
COMMENT ON COLUMN stg_ems.entidad_id IS
    'Clave de la entidad federativa (1 a 32) según el Catálogo Único de Claves de Áreas Geoestadísticas del INEGI, tomada directamente del campo CVEGEO de la fuente. Ref. cvegeo_states.cve_ent.';
COMMENT ON COLUMN stg_ems.codigo_actividad IS
    'Código que identifica las diversas actividades económicas bajo estudio (sector, subsector, rama o clase). El valor que se presenta es un código dentro del clasificador SCIAN 2018. FK a cat_actividad.codigo_actividad.';
COMMENT ON COLUMN stg_ems.ind_ingresos_bienes_serv IS
    'Ingresos totales por suministro de bienes y servicios - Índice (Índice Base 2018 = 100): Es el monto generado por la prestación de servicios durante el mes de referencia. Excluye: los ingresos financieros, subsidios y cuotas.';
COMMENT ON COLUMN stg_ems.ind_gastos_consumo IS
    'Gastos totales por consumo de bienes y servicios - Índice (Índice Base 2018 = 100): Es el importe destinado al consumo de bienes y servicios para realizar la actividad económica. Excluye: los gastos fiscales, financieros y de inversión.';
COMMENT ON COLUMN stg_ems.per_ocu_tot IS
    'Personal ocupado total - Índice (Índice Base 2018 = 100): Comprende al personal dependiente de la razón social y no dependiente (suministrado por otra razón social y de honorarios o comisiones).';
COMMENT ON COLUMN stg_ems.per_ocu_dependiente IS
    'Personal ocupado dependiente de la razón social - Índice (Índice Base 2018 = 100): Comprende al personal contratado directamente por esta razón social; de planta, eventual y no remunerado que trabajó para el establecimiento sujeto a su dirección y control, cubriendo como mínimo una tercera parte de la jornada laboral del mismo. Incluye: al personal que trabajó fuera del establecimiento bajo su control laboral y legal; trabajadoras y trabajadores en huelga; personas con licencia por enfermedad, vacaciones o permiso temporal; propietarias y propietarios, las y los socios, familiares y las y los trabajadores a destajo. Excluye: las y los pensionados y las y los jubilados.';
COMMENT ON COLUMN stg_ems.per_ocu_no_dependiente IS
    'Personal no dependiente de la razón social - Índice (Índice Base 2018 = 100): Son las personas que trabajaron para el establecimiento, pero dependen contractualmente de otra razón social. Excluye: al personal que trabaja como parte de un servicio contratado: vigilancia, mantenimiento y limpieza, entre otros.';
COMMENT ON COLUMN stg_ems.remuneraciones_tot IS
    'Remuneraciones totales - Índice (Índice Base 2018 = 100): Son todos los pagos para retribuir el trabajo del personal dependiente y no dependiente de la razón social.';
COMMENT ON COLUMN stg_ems.estatus_id IS
    'FK a cat_estatus; indica si el registro corresponde a cifras definitivas, revisadas o preliminares.';
COMMENT ON COLUMN stg_ems.fecha_actualizacion IS
    'Fecha en que el pipeline cargó o actualizó el registro en esta base. No proviene de la fuente.';
