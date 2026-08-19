-- =============================================================================
-- V3__tables_emec.sql  |  Pipeline: emec
-- Tabla staging de la Encuesta Mensual sobre Empresas Comerciales (EMEC),
-- Serie 2018, índices base 2018 = 100, cobertura por entidad federativa.
-- =============================================================================

CREATE TABLE IF NOT EXISTS stg_emec (
    id                       SERIAL PRIMARY KEY,
    fecha                    DATE    NOT NULL,
    entidad_id               INTEGER NOT NULL,
    codigo_actividad         INTEGER NOT NULL REFERENCES cat_actividad(codigo_actividad),
    per_ocu_tot              DOUBLE PRECISION,
    remuneraciones_tot       DOUBLE PRECISION,
    remuneraciones_media     DOUBLE PRECISION,
    ind_ingresos_bienes_serv DOUBLE PRECISION,
    ind_compras_reventa      DOUBLE PRECISION,
    estatus_id               INTEGER REFERENCES cat_estatus(id),
    fecha_actualizacion      DATE    NOT NULL,
    CONSTRAINT uq_stg_emec UNIQUE (fecha, entidad_id, codigo_actividad)
);

COMMENT ON TABLE stg_emec IS
    'Encuesta Mensual sobre Empresas Comerciales (EMEC) del INEGI, Serie 2018, información mensual desde enero de 2008. Proporciona información estadística económica de coyuntura sobre las unidades económicas de los sectores de comercio al por mayor y al por menor. Todas las variables son ÍNDICES con base 2018 = 100, no valores absolutos. Grano: un registro por periodo, entidad federativa y actividad económica.';

COMMENT ON COLUMN stg_emec.id IS
    'Identificador único del registro. Asignado por la base, no proviene de la fuente.';
COMMENT ON COLUMN stg_emec.fecha IS
    'Primer día del mes de referencia de la información, derivado de los campos ANIO y MES de la fuente.';
COMMENT ON COLUMN stg_emec.entidad_id IS
    'Clave de la entidad federativa (1 a 32) según el Catálogo Único de Claves de Áreas Geoestadísticas del INEGI, derivada del nombre publicado en la columna ENTIDAD. Ref. cvegeo_states.cve_ent.';
COMMENT ON COLUMN stg_emec.codigo_actividad IS
    'Código que identifica las diversas actividades económicas bajo estudio. El valor que se presenta es un código dentro del clasificador SCIAN 2013. FK a cat_actividad.codigo_actividad.';
COMMENT ON COLUMN stg_emec.per_ocu_tot IS
    'Personal ocupado total - Índice (Índice Base 2018 = 100): Total de personal dependiente de la razón social. Comprende al personal contratado directamente por esta razón social; de planta, eventual y no remunerado que trabajó para la empresa comercial sujeto a su dirección y control, cubriendo como mínimo una tercera parte de la jornada laboral de la misma. Incluye: al personal asimilable a salarios; al personal que trabajó fuera de la empresa comercial bajo su control laboral y legal; trabajadores en huelga; personas con licencia por enfermedad, vacaciones o permiso temporal; propietarios, socios, familiares y trabajadores a destajo. Excluye: pensionados y jubilados. Total de personal no dependiente de la razón social. Son todas las personas que trabajaron para la empresa comercial, pero que son ajenas a la razón social y realizaron labores sustantivas en la comercialización de bienes, administración y contabilidad, entre otras, cubriendo como mínimo una tercera parte de la jornada laboral de la misma.';
COMMENT ON COLUMN stg_emec.remuneraciones_tot IS
    'Remuneraciones totales - Índice (Índice Base 2018 = 100): Son todos los pagos y aportaciones en dinero y especie antes de cualquier deducción, para retribuir el trabajo del personal dependiente de la razón social, en forma de sueldos, salarios y prestaciones sociales, ya sea que este pago se calcule sobre la base de una jornada de trabajo o por la cantidad de trabajo desarrollado (destajo). Incluye: el pago realizado al personal con licencia y permiso temporal.';
COMMENT ON COLUMN stg_emec.remuneraciones_media IS
    'Remuneración media - Índice (Índice Base 2018 = 100): Las remuneraciones medias son resultado del cálculo del Remuneraciones totales entre el Total de personal remunerado dependiente de la razón social.';
COMMENT ON COLUMN stg_emec.ind_ingresos_bienes_serv IS
    'Ingresos totales por suministro de bienes y servicios - Índice (Índice Base 2018 = 100): Es el monto que obtuvo la empresa por todas aquellas actividades de producción, comercialización o prestación de servicios que realizó durante el mes de referencia. Excluye: los ingresos financieros, subsidios y cuotas. Valoración: La valoración de los ingresos por bienes y servicios debe realizarse de acuerdo con el valor de facturación, considerando todos los impuestos cargados al comprador, excepto el IVA, y deben deducirse todas las concesiones otorgadas a los clientes, tales como: descuentos, bonificaciones y devoluciones; así como los fletes, seguros y almacenamiento de los productos suministrados por esta empresa cuando se facturen de manera independiente.';
COMMENT ON COLUMN stg_emec.ind_compras_reventa IS
    'Mercancías compradas para su reventa sin transformación - Índice (Índice Base 2018 = 100): Es el valor de las mercancías que compró la empresa comercial para venderlas en las mismas condiciones en que las adquirió. Incluye: las mercancías para reventa que recibió de otros establecimientos de la misma empresa. Excluye: las mercancías recibidas en consignación.';
COMMENT ON COLUMN stg_emec.estatus_id IS
    'FK a cat_estatus; indica si el registro corresponde a cifras definitivas, revisadas o preliminares.';
COMMENT ON COLUMN stg_emec.fecha_actualizacion IS
    'Fecha en que el pipeline cargó o actualizó el registro en esta base. No proviene de la fuente.';
