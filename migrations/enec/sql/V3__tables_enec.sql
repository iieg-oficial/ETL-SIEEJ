-- =============================================================================
-- V3__tables_enec.sql  |  Pipeline: enec
-- Encuesta Nacional de Empresas Constructoras (ENEC), Serie 2018.
-- Dos tablas staging con las mismas 44 medidas y distinta llave:
--   stg_enec_nacional -> total nacional por actividad (23, 236, 237, 238)
--   stg_enec_entidad  -> por entidad federativa, solo sector 23
-- Los COMMENT ON reproducen el diccionario de datos de la fuente.
-- =============================================================================

CREATE TABLE IF NOT EXISTS stg_enec_nacional (
    id                                  SERIAL PRIMARY KEY,
    fecha                               DATE    NOT NULL,
    codigo_actividad                    INTEGER NOT NULL REFERENCES cat_actividad(codigo_actividad),
    dias_trabajados                     DOUBLE PRECISION,
    per_ocu_tot                         INTEGER,
    per_ocu_dependiente                 INTEGER,
    per_ocu_obreros                     INTEGER,
    per_ocu_administrativos             INTEGER,
    per_ocu_no_remunerados              INTEGER,
    per_ocu_subcontratado               INTEGER,
    horas_tot                           DOUBLE PRECISION,
    horas_dependiente                   DOUBLE PRECISION,
    horas_obreros                       DOUBLE PRECISION,
    horas_administrativos               DOUBLE PRECISION,
    horas_no_remunerados                DOUBLE PRECISION,
    horas_subcontratado                 DOUBLE PRECISION,
    remuneraciones_tot                  INTEGER,
    salarios_obreros                    INTEGER,
    sueldos_administrativos             INTEGER,
    prestaciones                        INTEGER,
    remuneracion_media_persona          DOUBLE PRECISION,
    remuneracion_media_hora             DOUBLE PRECISION,
    remuneracion_media_salarios         DOUBLE PRECISION,
    salario_medio_obreros               DOUBLE PRECISION,
    sueldo_medio_administrativos        DOUBLE PRECISION,
    gastos_tot                          INTEGER,
    gasto_materiales_contratista        INTEGER,
    gasto_materiales_subcontratista     INTEGER,
    gasto_suministro_personal           INTEGER,
    gasto_subcontratistas               INTEGER,
    gastos_otros                        INTEGER,
    consumo_materiales_contratista      INTEGER,
    consumo_materiales_subcontratista   INTEGER,
    ingresos_tot                        INTEGER,
    ingresos_contratista                INTEGER,
    ingresos_subcontratista             INTEGER,
    ingresos_administracion             INTEGER,
    ingresos_otros                      INTEGER,
    valor_produccion                    INTEGER,
    valor_produccion_edificacion        INTEGER,
    valor_produccion_agua_riego         INTEGER,
    valor_produccion_electricidad       INTEGER,
    valor_produccion_transporte         INTEGER,
    valor_produccion_petroleo           INTEGER,
    valor_produccion_otras              INTEGER,
    valor_produccion_publico            INTEGER,
    valor_produccion_privado            INTEGER,
    estatus_id                          INTEGER REFERENCES cat_estatus(id),
    fecha_actualizacion                 DATE    NOT NULL,
    CONSTRAINT uq_stg_enec_nacional UNIQUE (fecha, codigo_actividad)
);

COMMENT ON TABLE stg_enec_nacional IS
    'Encuesta Nacional de Empresas Constructoras (ENEC) del INEGI, Serie 2018: TOTAL NACIONAL con desglose por actividad de la construcción, mensual desde enero de 2018. Publica valores absolutos, no índices. Grano: un registro por periodo y actividad. El desglose por entidad federativa vive en stg_enec_entidad, que solo cubre el sector 23.';
COMMENT ON COLUMN stg_enec_nacional.id IS
    'Identificador único del registro. Asignado por la base, no proviene de la fuente.';
COMMENT ON COLUMN stg_enec_nacional.fecha IS
    'Primer día del mes de referencia de la información, derivado de los campos ANIO y MES de la fuente.';
COMMENT ON COLUMN stg_enec_nacional.codigo_actividad IS
    'Código que identifica las diversas actividades económicas bajo estudio (sector, subsector, rama o clase) dentro del clasificador SCIAN. Valores publicados: 23 construcción, 236 edificación, 237 construcción de obras de ingeniería civil, 238 trabajos especializados para la construcción. FK a cat_actividad.codigo_actividad.';
COMMENT ON COLUMN stg_enec_nacional.dias_trabajados IS
    'Días trabajados (Número de días). Es el número total de días en que la empresa permaneció abierta realizando actividades durante el mes de referencia. Se obtiene de restar a los días naturales, los días que permaneció cerrada por descanso, festividades, huelgas, vacaciones, etcétera.';
COMMENT ON COLUMN stg_enec_nacional.per_ocu_tot IS
    'Personal ocupado total (Número de personas). Comprende al total de personal que trabajó para la empresa, dependiente y no dependiente de la misma, durante el año de referencia, sujeto a su dirección y control, cubriendo como mínimo una tercera parte de la jornada laboral de la misma, considerando hombres y mujeres.';
COMMENT ON COLUMN stg_enec_nacional.per_ocu_dependiente IS
    'Personal dependiente de la razón social (Número de personas). Comprende al personal contratado directamente por esta razón social, de planta, eventual y no remunerado, sea o no sindicalizado, que trabajó para la empresa durante el mes de referencia, sujeto a su dirección y tercera parte de la jornada laboral de la misma. Considera hombres y mujeres.';
COMMENT ON COLUMN stg_enec_nacional.per_ocu_obreros IS
    'Obreros (Número de personas). Comprende al personal que realizan trabajos de albañilería, nivelación de suelos y demás trabajos relacionados con la construcción de las obras, así como el personal vinculado con tareas auxiliares a la misma, dedicado a la provisión de materiales, almacenaje, limpieza de las obras, transporte, veladores, etcétera.';
COMMENT ON COLUMN stg_enec_nacional.per_ocu_administrativos IS
    'Empleados administrativos, contables y de dirección (Número de personas). Comprende a todas las personas que trabajaron durante el periodo de referencia dependiendo contractualmente de la empresa, sujetas a su dirección y control, a cambio de una remuneración fija y periódica por desempeñar labores generales de oficina, así como de contabilidad, ejecutivas, de planeación, organización, dirección y control para la propia empresa constructora.';
COMMENT ON COLUMN stg_enec_nacional.per_ocu_no_remunerados IS
    'Propietarios, familiares y otros trabajadores no remunerados (Número de personas). Son las personas que trabajan para la empresa cubriendo como mínimo una tercera parte de la jornada laboral de la misma, sin recibir un sueldo o salario. Se consideran a los propietarios, familiares de estos, socios activos, prestadores de servicio social, personas de programas de empleo, etcétera.';
COMMENT ON COLUMN stg_enec_nacional.per_ocu_subcontratado IS
    'Personal subcontratado (Número de personas). Son las personas que trabajaron para la empresa, pero dependen contractualmente de otra razón social.';
COMMENT ON COLUMN stg_enec_nacional.horas_tot IS
    'Horas trabajadas por el personal ocupado total (Miles de horas). Es el total de horas trabajadas durante el mes de referencia por el personal ocupado dependiente o no dependiente de la razón social en la jornada laboral, comprende las horas normales y extraordinarias dedicadas a las actividades de construcción.';
COMMENT ON COLUMN stg_enec_nacional.horas_dependiente IS
    'Horas trabajadas por personal dependiente de la razón social (Miles de horas). Es el total de horas trabajadas en el año de referencia por el personal dependiente de la razón social, comprende las horas normales y extraordinarias dedicadas a las actividades.';
COMMENT ON COLUMN stg_enec_nacional.horas_obreros IS
    'Horas trabajadas por los obreros (Miles de horas). Es el total de horas trabajadas durante el mes de referencia por los obreros en la jornada laboral; comprende las horas normales y extraordinarias dedicadas a las actividades de construcción.';
COMMENT ON COLUMN stg_enec_nacional.horas_administrativos IS
    'Horas trabajadas por los empleados administrativos, contables y de dirección (Miles de horas). Es el total de horas normales y extraordinarias efectivamente trabajadas por los empleados administrativos, contables y de dirección dependientes de la razón social.';
COMMENT ON COLUMN stg_enec_nacional.horas_no_remunerados IS
    'Horas trabajadas por los propietarios, familiares y otros trabajadores no remunerados (Miles de horas). Es el total de horas normales y extraordinarias efectivamente trabajadas por los propietarios, familiares y otros trabajadores no remunerados dependientes de la razón social.';
COMMENT ON COLUMN stg_enec_nacional.horas_subcontratado IS
    'Horas trabajadas por personal suministrado por otra razón social (Miles de horas). Es el total de horas trabajadas en el periodo de referencia por el personal ocupado contratado y proporcionado por otra razón social, comprende las horas normales y extraordinarias dedicadas a las actividades.';
COMMENT ON COLUMN stg_enec_nacional.remuneraciones_tot IS
    'Remuneraciones totales (Miles de pesos corrientes). Son todos los pagos y aportaciones normales y extraordinarias, en dinero y especie antes de cualquier deducción, para retribuir el trabajo del personal dependiente de la razón social considerando obreros(as) y empleados(as) administrativos(as) tanto de planta como eventuales, en forma de salarios y sueldos, prestaciones sociales y utilidades distribuidas al personal, ya sea que este pago se calcule sobre la base de una jornada de trabajo o por la cantidad de trabajo desarrollado (destajo), o mediante un salario base que se complementa con comisiones por ventas u otras actividades.';
COMMENT ON COLUMN stg_enec_nacional.salarios_obreros IS
    'Salarios pagados a obreros (Miles de pesos corrientes). Son los pagos que realiza la empresa para retribuir el trabajo ordinario y extraordinario del personal dependiente de la razón social considerando obreros(as), empleados(as) administrativos(as) tanto de planta como eventuales, antes de cualquier deducción retenida por las y los empleadores, como son impuesto sobre la renta o sobre el producto del trabajo, las aportaciones de los y las trabajadores a los regímenes de seguridad social (IMSS, INFONAVIT) y las cuotas sindicales.';
COMMENT ON COLUMN stg_enec_nacional.sueldos_administrativos IS
    'Sueldos pagados a empleados administrativos, contables y de dirección (Miles de pesos corrientes). Son los pagos que realizó la empresa para retribuir el trabajo ordinario y extraordinario del personal dependiente de la razón social considerando obreros(as), empleados(as) administrativos(as) tanto de planta como eventuales, antes de cualquier deducción retenida por las y los empleadores, como son impuesto sobre la renta o sobre el producto del trabajo, las aportaciones de los y las trabajadores a los regímenes de seguridad social (IMSS, INFONAVIT) y las cuotas sindicales.';
COMMENT ON COLUMN stg_enec_nacional.prestaciones IS
    'Prestaciones, contribuciones y utilidades (Miles de pesos corrientes). Son los pagos efectivamente realizados tanto contractuales como extracontractuales que proporcionó la unidad económica a los obreros y empleados, como una remuneración adicional a los sueldos y salarios, ya sea en dinero o en especie, considerando contribuciones y utilidades repartidas a los trabajadores.';
COMMENT ON COLUMN stg_enec_nacional.remuneracion_media_persona IS
    'Remuneraciones medias por persona ocupada del personal dependiente de la razón social (Pesos corrientes). Es el promedio de remuneraciones pagadas al personal dependiente de la empresa por persona. Son los pagos y aportaciones, en dinero y especie, antes de cualquier deducción, que recibió en promedio cada persona remunerada durante el periodo de referencia. Resulta de dividir el monto de las remuneraciones pagadas al personal remunerado que depende de la razón social, entre el total de personal ocupado remunerado.';
COMMENT ON COLUMN stg_enec_nacional.remuneracion_media_hora IS
    'Remuneraciones medias por hora trabajada (Pesos corrientes). Es el promedio de la remuneración pagada por hora trabajada del personal remunerado (obreros y empleados).';
COMMENT ON COLUMN stg_enec_nacional.remuneracion_media_salarios IS
    'Remuneraciones medias de salarios y sueldos (Pesos corrientes). Es el promedio de los salarios y sueldos pagados a obreros y empleados.';
COMMENT ON COLUMN stg_enec_nacional.salario_medio_obreros IS
    'Salarios medios pagados a obreros (Pesos corrientes). Son los pagos que realizó la empresa para retribuir el trabajo ordinario y extraordinario de los obreros, antes de cualquier deducción retenida por los empleadores, como son: impuesto sobre la renta o sobre el producto del trabajo, las aportaciones de los trabajadores a los regímenes de seguridad social (IMSS, INFONAVIT) y las cuotas sindicales.';
COMMENT ON COLUMN stg_enec_nacional.sueldo_medio_administrativos IS
    'Sueldos medios pagados a empleados administrativos, contables y de dirección (Pesos corrientes). Son los pagos que realizó la empresa para retribuir el trabajo ordinario y extraordinario de los obreros, antes de cualquier deducción retenida por los empleadores, como son: impuesto sobre la renta o sobre el producto del trabajo, las aportaciones de los trabajadores a los regímenes de seguridad social (IMSS, INFONAVIT) y las cuotas sindicales.';
COMMENT ON COLUMN stg_enec_nacional.gastos_tot IS
    'Gastos totales por consumo de bienes y servicios (Miles de pesos corrientes). Es el valor de todos los bienes y servicios adquiridos y/o consumidos por la empresa para realizar sus operaciones en el periodo de referencia.';
COMMENT ON COLUMN stg_enec_nacional.gasto_materiales_contratista IS
    'Gasto de materiales para la construcción como contratista principal y materiales dados a subcontratistas (Miles de pesos corrientes). Compra de materiales como contratista principal y materiales dados a subcontratistas, es el importe de los materiales comprados por esta empresa en las obras que ejecutó de manera directa, constituyendo el elemento principal o auxiliar de las mismas. Por ejemplo: tabique, varilla, arena, grava, cemento, vidrio, etcétera.';
COMMENT ON COLUMN stg_enec_nacional.gasto_materiales_subcontratista IS
    'Gasto de materiales para la construcción como subcontratista (Miles de pesos corrientes). Es el importe de los materiales comprados propiedad de la empresa, en las obras que ejecutó como subcontratista para otras constructoras, constituyendo el elemento principal o auxiliar de las mismas.';
COMMENT ON COLUMN stg_enec_nacional.gasto_suministro_personal IS
    'Pago a otra razón social por el suministro de personal (Miles de pesos corrientes). Son los pagos que realizó la empresa a otra razón social que le suministró personal para el desempeño de las actividades productivas y de apoyo.';
COMMENT ON COLUMN stg_enec_nacional.gasto_subcontratistas IS
    'Pagos a subcontratistas (Miles de pesos corrientes). Es el pago efectuado por esta empresa a terceros, denominados subcontratistas, por la ejecución de una parte de la obra o bien de la totalidad de los trabajos u obras contratadas, considerando también el valor de los materiales de construcción utilizados y que son propiedad de la empresa subcontratista.';
COMMENT ON COLUMN stg_enec_nacional.gastos_otros IS
    'Otros gastos por consumo de bienes y servicios (Miles de pesos corrientes). Son los gastos de operación normal de la empresa por los bienes y servicios que consumió, y que no fueron considerados de manera específica los conceptos anteriores, pero estuvieron relacionados con la actividad.';
COMMENT ON COLUMN stg_enec_nacional.consumo_materiales_contratista IS
    'Consumo de materiales para la construcción como contratista principal y materiales dados a subcontratistas (Miles de pesos corrientes). Es el importe de los materiales consumidos por esta empresa en las obras que ejecuta de manera directa, constituyendo el elemento principal o auxiliar de las mismas. Se consideran los materiales entregados a subcontratistas.';
COMMENT ON COLUMN stg_enec_nacional.consumo_materiales_subcontratista IS
    'Consumo de materiales para la construcción como subcontratista (Miles de pesos corrientes). Es el importe de los materiales consumidos propiedad de la empresa, en las obras que ejecutó como subcontratista para otras constructoras, constituyendo el elemento principal o auxiliar de las mismas.';
COMMENT ON COLUMN stg_enec_nacional.ingresos_tot IS
    'Ingresos totales por suministro de bienes y servicios (Miles de pesos corrientes). Es el monto que obtuvo la empresa en el mes de referencia, por todas aquellas actividades de producción de bienes y servicios.';
COMMENT ON COLUMN stg_enec_nacional.ingresos_contratista IS
    'Ingresos por la ejecución de obras como contratista principal (Miles de pesos corrientes). Es el importe de los ingresos obtenidos por la ejecución de obras de construcción, de edificación, ingeniería civil o trabajos especiales (obra nueva, ampliación, remodelación o reparación) que realiza la empresa como contratista principal, que hayan sido concluidas o están en el proceso.';
COMMENT ON COLUMN stg_enec_nacional.ingresos_subcontratista IS
    'Ingresos por la ejecución de obras como subcontratista (Miles de pesos corrientes). Son las percepciones recibidas por la ejecución de obras de construcción, de edificación, ingeniería civil o trabajos especiales (obra nueva, ampliación, remodelación o reparación) que realizó la empresa para otros contratistas, que hayan sido concluidas o estén en proceso.';
COMMENT ON COLUMN stg_enec_nacional.ingresos_administracion IS
    'Ingresos por administración y supervisión de obras (Miles de pesos corrientes). Son los ingresos que recibe la empresa por los servicios a terceros, respecto de la supervisión o administración de obras, del manejo de los recursos materiales en la obra, el cumplimiento de los costos y las especificaciones técnicas establecidos durante la planeación para la construcción o entrega de obras, con la finalidad de que se respeten los tiempos programados, así como la calidad conforme a lo estipulado y la reglamentación vigente.';
COMMENT ON COLUMN stg_enec_nacional.ingresos_otros IS
    'Otros ingresos por suministro de obras y servicios (Miles de pesos corrientes). Son los ingresos que obtiene la empresa que no fueron considerados de manera específica en los conceptos anteriores, pero estuvieron relacionados con la actividad.';
COMMENT ON COLUMN stg_enec_nacional.valor_produccion IS
    'Valor de la producción generado en la entidad (Miles de pesos corrientes). Se refiere al monto o valor monetario que significa la realización de una obra o parte de esta. Independientemente de haber recibido o no el pago del (de la) dueño (a) o contratista de la obra.';
COMMENT ON COLUMN stg_enec_nacional.valor_produccion_edificacion IS
    'Valor de la producción de obras de Edificación (Miles de pesos corrientes). Comprende: Vivienda, edificios industriales, comerciales y de servicios, escuelas, hospitales y clínicas además de obras y trabajos auxiliares para la edificación.';
COMMENT ON COLUMN stg_enec_nacional.valor_produccion_agua_riego IS
    'Valor de la producción de obras de Agua, riego y saneamiento (Miles de pesos corrientes). Comprende: Construcción de sistema de agua potable, perforación de pozos de agua, obras de riego y trabajos auxiliares para el agua, riego y saneamiento.';
COMMENT ON COLUMN stg_enec_nacional.valor_produccion_electricidad IS
    'Valor de la producción de obras de Electricidad y telecomunicaciones (Miles de pesos corrientes). Comprende: Infraestructura para la generación y distribución de electricidad, infraestructura para telecomunicaciones, obras y trabajos auxiliares para electricidad y telecomunicaciones.';
COMMENT ON COLUMN stg_enec_nacional.valor_produccion_transporte IS
    'Valor de la producción de obras de Transporte y urbanización (Miles de pesos corrientes). Comprende: Obras de transporte en ciudades y urbanización, carreteras, caminos y puentes, obras ferroviarias, Infraestructura marítimo y fluvial, Obras y trabajos auxiliares para transporte.';
COMMENT ON COLUMN stg_enec_nacional.valor_produccion_petroleo IS
    'Valor de la producción de obras de Petróleo y petroquímica (Miles de pesos corrientes). Comprende: Refinerías y plantas petroleras, oleoductos y gaseoductos, obras y trabajos auxiliares para petróleo y petroquímica.';
COMMENT ON COLUMN stg_enec_nacional.valor_produccion_otras IS
    'Valor de la producción de obras de Otras construcciones (Miles de pesos corrientes). Comprende: Instalaciones en edificaciones, montaje de estructuras, trabajos de albañilería y acabados, obras y trabajos auxiliares para otras construcciones.';
COMMENT ON COLUMN stg_enec_nacional.valor_produccion_publico IS
    'Valor de la producción de obras del sector público (Miles de pesos corrientes). Son todas las obras que realiza una empresa constructora por encargo de una dependencia gubernamental en cualquiera de sus tres niveles: Federal, Estatal y Municipal.';
COMMENT ON COLUMN stg_enec_nacional.valor_produccion_privado IS
    'Valor de la producción de obras del sector privado (Miles de pesos corrientes). Son todas las obras que realiza una empresa constructora para cualquier particular o entidad privada, incluyendo las obras realizadas por las empresas y organismos de los diversos sectores económicos del país.';
COMMENT ON COLUMN stg_enec_nacional.estatus_id IS
    'FK a cat_estatus; indica si el registro corresponde a cifras definitivas, revisadas o preliminares.';
COMMENT ON COLUMN stg_enec_nacional.fecha_actualizacion IS
    'Fecha en que el pipeline cargó o actualizó el registro en esta base. No proviene de la fuente.';


CREATE TABLE IF NOT EXISTS stg_enec_entidad (
    id                                  SERIAL PRIMARY KEY,
    fecha                               DATE    NOT NULL,
    entidad_id                          INTEGER NOT NULL,
    dias_trabajados                     DOUBLE PRECISION,
    per_ocu_tot                         INTEGER,
    per_ocu_dependiente                 INTEGER,
    per_ocu_obreros                     INTEGER,
    per_ocu_administrativos             INTEGER,
    per_ocu_no_remunerados              INTEGER,
    per_ocu_subcontratado               INTEGER,
    horas_tot                           DOUBLE PRECISION,
    horas_dependiente                   DOUBLE PRECISION,
    horas_obreros                       DOUBLE PRECISION,
    horas_administrativos               DOUBLE PRECISION,
    horas_no_remunerados                DOUBLE PRECISION,
    horas_subcontratado                 DOUBLE PRECISION,
    remuneraciones_tot                  INTEGER,
    salarios_obreros                    INTEGER,
    sueldos_administrativos             INTEGER,
    prestaciones                        INTEGER,
    remuneracion_media_persona          DOUBLE PRECISION,
    remuneracion_media_hora             DOUBLE PRECISION,
    remuneracion_media_salarios         DOUBLE PRECISION,
    salario_medio_obreros               DOUBLE PRECISION,
    sueldo_medio_administrativos        DOUBLE PRECISION,
    gastos_tot                          INTEGER,
    gasto_materiales_contratista        INTEGER,
    gasto_materiales_subcontratista     INTEGER,
    gasto_suministro_personal           INTEGER,
    gasto_subcontratistas               INTEGER,
    gastos_otros                        INTEGER,
    consumo_materiales_contratista      INTEGER,
    consumo_materiales_subcontratista   INTEGER,
    ingresos_tot                        INTEGER,
    ingresos_contratista                INTEGER,
    ingresos_subcontratista             INTEGER,
    ingresos_administracion             INTEGER,
    ingresos_otros                      INTEGER,
    valor_produccion                    INTEGER,
    valor_produccion_edificacion        INTEGER,
    valor_produccion_agua_riego         INTEGER,
    valor_produccion_electricidad       INTEGER,
    valor_produccion_transporte         INTEGER,
    valor_produccion_petroleo           INTEGER,
    valor_produccion_otras              INTEGER,
    valor_produccion_publico            INTEGER,
    valor_produccion_privado            INTEGER,
    estatus_id                          INTEGER REFERENCES cat_estatus(id),
    fecha_actualizacion                 DATE    NOT NULL,
    CONSTRAINT uq_stg_enec_entidad UNIQUE (fecha, entidad_id)
);

COMMENT ON TABLE stg_enec_entidad IS
    'Encuesta Nacional de Empresas Constructoras (ENEC) del INEGI, Serie 2018: desglose por ENTIDAD FEDERATIVA, mensual desde enero de 2018. Solo cubre el sector 23 (construcción); el desglose por actividad vive en stg_enec_nacional. Publica valores absolutos, no índices. Grano: un registro por periodo y entidad. Las filas del agregado nacional que trae la fuente (CVEGEO 00) se excluyen a propósito: son idénticas a las de stg_enec_nacional con actividad 23.';
COMMENT ON COLUMN stg_enec_entidad.id IS
    'Identificador único del registro. Asignado por la base, no proviene de la fuente.';
COMMENT ON COLUMN stg_enec_entidad.fecha IS
    'Primer día del mes de referencia de la información, derivado de los campos ANIO y MES de la fuente.';
COMMENT ON COLUMN stg_enec_entidad.entidad_id IS
    'Clave de la entidad federativa (1 a 32) según el Catálogo Único de Claves de Áreas Geoestadísticas del INEGI, tomada del campo CVEGEO de la fuente. Ref. cvegeo_states.cve_ent. Incluye además la clave 33, Obra en el extranjero, que NO es una entidad federativa y no cruza contra cvegeo_states, pero sí forma parte del total nacional: sin ella la suma de las 32 entidades no cuadra con el valor de producción publicado.';
COMMENT ON COLUMN stg_enec_entidad.dias_trabajados IS
    'Días trabajados (Número de días). Es el número total de días en que la empresa permaneció abierta realizando actividades durante el mes de referencia. Se obtiene de restar a los días naturales, los días que permaneció cerrada por descanso, festividades, huelgas, vacaciones, etcétera.';
COMMENT ON COLUMN stg_enec_entidad.per_ocu_tot IS
    'Personal ocupado total (Número de personas). Comprende al total de personal que trabajó para la empresa, dependiente y no dependiente de la misma, durante el año de referencia, sujeto a su dirección y control, cubriendo como mínimo una tercera parte de la jornada laboral de la misma, considerando hombres y mujeres.';
COMMENT ON COLUMN stg_enec_entidad.per_ocu_dependiente IS
    'Personal dependiente de la razón social (Número de personas). Comprende al personal contratado directamente por esta razón social, de planta, eventual y no remunerado, sea o no sindicalizado, que trabajó para la empresa durante el mes de referencia, sujeto a su dirección y tercera parte de la jornada laboral de la misma. Considera hombres y mujeres.';
COMMENT ON COLUMN stg_enec_entidad.per_ocu_obreros IS
    'Obreros (Número de personas). Comprende al personal que realizan trabajos de albañilería, nivelación de suelos y demás trabajos relacionados con la construcción de las obras, así como el personal vinculado con tareas auxiliares a la misma, dedicado a la provisión de materiales, almacenaje, limpieza de las obras, transporte, veladores, etcétera.';
COMMENT ON COLUMN stg_enec_entidad.per_ocu_administrativos IS
    'Empleados administrativos, contables y de dirección (Número de personas). Comprende a todas las personas que trabajaron durante el periodo de referencia dependiendo contractualmente de la empresa, sujetas a su dirección y control, a cambio de una remuneración fija y periódica por desempeñar labores generales de oficina, así como de contabilidad, ejecutivas, de planeación, organización, dirección y control para la propia empresa constructora.';
COMMENT ON COLUMN stg_enec_entidad.per_ocu_no_remunerados IS
    'Propietarios, familiares y otros trabajadores no remunerados (Número de personas). Son las personas que trabajan para la empresa cubriendo como mínimo una tercera parte de la jornada laboral de la misma, sin recibir un sueldo o salario. Se consideran a los propietarios, familiares de estos, socios activos, prestadores de servicio social, personas de programas de empleo, etcétera.';
COMMENT ON COLUMN stg_enec_entidad.per_ocu_subcontratado IS
    'Personal subcontratado (Número de personas). Son las personas que trabajaron para la empresa, pero dependen contractualmente de otra razón social.';
COMMENT ON COLUMN stg_enec_entidad.horas_tot IS
    'Horas trabajadas por el personal ocupado total (Miles de horas). Es el total de horas trabajadas durante el mes de referencia por el personal ocupado dependiente o no dependiente de la razón social en la jornada laboral, comprende las horas normales y extraordinarias dedicadas a las actividades de construcción.';
COMMENT ON COLUMN stg_enec_entidad.horas_dependiente IS
    'Horas trabajadas por personal dependiente de la razón social (Miles de horas). Es el total de horas trabajadas en el año de referencia por el personal dependiente de la razón social, comprende las horas normales y extraordinarias dedicadas a las actividades.';
COMMENT ON COLUMN stg_enec_entidad.horas_obreros IS
    'Horas trabajadas por los obreros (Miles de horas). Es el total de horas trabajadas durante el mes de referencia por los obreros en la jornada laboral; comprende las horas normales y extraordinarias dedicadas a las actividades de construcción.';
COMMENT ON COLUMN stg_enec_entidad.horas_administrativos IS
    'Horas trabajadas por los empleados administrativos, contables y de dirección (Miles de horas). Es el total de horas normales y extraordinarias efectivamente trabajadas por los empleados administrativos, contables y de dirección dependientes de la razón social.';
COMMENT ON COLUMN stg_enec_entidad.horas_no_remunerados IS
    'Horas trabajadas por los propietarios, familiares y otros trabajadores no remunerados (Miles de horas). Es el total de horas normales y extraordinarias efectivamente trabajadas por los propietarios, familiares y otros trabajadores no remunerados dependientes de la razón social.';
COMMENT ON COLUMN stg_enec_entidad.horas_subcontratado IS
    'Horas trabajadas por personal suministrado por otra razón social (Miles de horas). Es el total de horas trabajadas en el periodo de referencia por el personal ocupado contratado y proporcionado por otra razón social, comprende las horas normales y extraordinarias dedicadas a las actividades.';
COMMENT ON COLUMN stg_enec_entidad.remuneraciones_tot IS
    'Remuneraciones totales (Miles de pesos corrientes). Son todos los pagos y aportaciones normales y extraordinarias, en dinero y especie antes de cualquier deducción, para retribuir el trabajo del personal dependiente de la razón social considerando obreros(as) y empleados(as) administrativos(as) tanto de planta como eventuales, en forma de salarios y sueldos, prestaciones sociales y utilidades distribuidas al personal, ya sea que este pago se calcule sobre la base de una jornada de trabajo o por la cantidad de trabajo desarrollado (destajo), o mediante un salario base que se complementa con comisiones por ventas u otras actividades.';
COMMENT ON COLUMN stg_enec_entidad.salarios_obreros IS
    'Salarios pagados a obreros (Miles de pesos corrientes). Son los pagos que realiza la empresa para retribuir el trabajo ordinario y extraordinario del personal dependiente de la razón social considerando obreros(as), empleados(as) administrativos(as) tanto de planta como eventuales, antes de cualquier deducción retenida por las y los empleadores, como son impuesto sobre la renta o sobre el producto del trabajo, las aportaciones de los y las trabajadores a los regímenes de seguridad social (IMSS, INFONAVIT) y las cuotas sindicales.';
COMMENT ON COLUMN stg_enec_entidad.sueldos_administrativos IS
    'Sueldos pagados a empleados administrativos, contables y de dirección (Miles de pesos corrientes). Son los pagos que realizó la empresa para retribuir el trabajo ordinario y extraordinario del personal dependiente de la razón social considerando obreros(as), empleados(as) administrativos(as) tanto de planta como eventuales, antes de cualquier deducción retenida por las y los empleadores, como son impuesto sobre la renta o sobre el producto del trabajo, las aportaciones de los y las trabajadores a los regímenes de seguridad social (IMSS, INFONAVIT) y las cuotas sindicales.';
COMMENT ON COLUMN stg_enec_entidad.prestaciones IS
    'Prestaciones, contribuciones y utilidades (Miles de pesos corrientes). Son los pagos efectivamente realizados tanto contractuales como extracontractuales que proporcionó la unidad económica a los obreros y empleados, como una remuneración adicional a los sueldos y salarios, ya sea en dinero o en especie, considerando contribuciones y utilidades repartidas a los trabajadores.';
COMMENT ON COLUMN stg_enec_entidad.remuneracion_media_persona IS
    'Remuneraciones medias por persona ocupada del personal dependiente de la razón social (Pesos corrientes). Es el promedio de remuneraciones pagadas al personal dependiente de la empresa por persona. Son los pagos y aportaciones, en dinero y especie, antes de cualquier deducción, que recibió en promedio cada persona remunerada durante el periodo de referencia. Resulta de dividir el monto de las remuneraciones pagadas al personal remunerado que depende de la razón social, entre el total de personal ocupado remunerado.';
COMMENT ON COLUMN stg_enec_entidad.remuneracion_media_hora IS
    'Remuneraciones medias por hora trabajada (Pesos corrientes). Es el promedio de la remuneración pagada por hora trabajada del personal remunerado (obreros y empleados).';
COMMENT ON COLUMN stg_enec_entidad.remuneracion_media_salarios IS
    'Remuneraciones medias de salarios y sueldos (Pesos corrientes). Es el promedio de los salarios y sueldos pagados a obreros y empleados.';
COMMENT ON COLUMN stg_enec_entidad.salario_medio_obreros IS
    'Salarios medios pagados a obreros (Pesos corrientes). Son los pagos que realizó la empresa para retribuir el trabajo ordinario y extraordinario de los obreros, antes de cualquier deducción retenida por los empleadores, como son: impuesto sobre la renta o sobre el producto del trabajo, las aportaciones de los trabajadores a los regímenes de seguridad social (IMSS, INFONAVIT) y las cuotas sindicales.';
COMMENT ON COLUMN stg_enec_entidad.sueldo_medio_administrativos IS
    'Sueldos medios pagados a empleados administrativos, contables y de dirección (Pesos corrientes). Son los pagos que realizó la empresa para retribuir el trabajo ordinario y extraordinario de los obreros, antes de cualquier deducción retenida por los empleadores, como son: impuesto sobre la renta o sobre el producto del trabajo, las aportaciones de los trabajadores a los regímenes de seguridad social (IMSS, INFONAVIT) y las cuotas sindicales.';
COMMENT ON COLUMN stg_enec_entidad.gastos_tot IS
    'Gastos totales por consumo de bienes y servicios (Miles de pesos corrientes). Es el valor de todos los bienes y servicios adquiridos y/o consumidos por la empresa para realizar sus operaciones en el periodo de referencia.';
COMMENT ON COLUMN stg_enec_entidad.gasto_materiales_contratista IS
    'Gasto de materiales para la construcción como contratista principal y materiales dados a subcontratistas (Miles de pesos corrientes). Compra de materiales como contratista principal y materiales dados a subcontratistas, es el importe de los materiales comprados por esta empresa en las obras que ejecutó de manera directa, constituyendo el elemento principal o auxiliar de las mismas. Por ejemplo: tabique, varilla, arena, grava, cemento, vidrio, etcétera.';
COMMENT ON COLUMN stg_enec_entidad.gasto_materiales_subcontratista IS
    'Gasto de materiales para la construcción como subcontratista (Miles de pesos corrientes). Es el importe de los materiales comprados propiedad de la empresa, en las obras que ejecutó como subcontratista para otras constructoras, constituyendo el elemento principal o auxiliar de las mismas.';
COMMENT ON COLUMN stg_enec_entidad.gasto_suministro_personal IS
    'Pago a otra razón social por el suministro de personal (Miles de pesos corrientes). Son los pagos que realizó la empresa a otra razón social que le suministró personal para el desempeño de las actividades productivas y de apoyo.';
COMMENT ON COLUMN stg_enec_entidad.gasto_subcontratistas IS
    'Pagos a subcontratistas (Miles de pesos corrientes). Es el pago efectuado por esta empresa a terceros, denominados subcontratistas, por la ejecución de una parte de la obra o bien de la totalidad de los trabajos u obras contratadas, considerando también el valor de los materiales de construcción utilizados y que son propiedad de la empresa subcontratista.';
COMMENT ON COLUMN stg_enec_entidad.gastos_otros IS
    'Otros gastos por consumo de bienes y servicios (Miles de pesos corrientes). Son los gastos de operación normal de la empresa por los bienes y servicios que consumió, y que no fueron considerados de manera específica los conceptos anteriores, pero estuvieron relacionados con la actividad.';
COMMENT ON COLUMN stg_enec_entidad.consumo_materiales_contratista IS
    'Consumo de materiales para la construcción como contratista principal y materiales dados a subcontratistas (Miles de pesos corrientes). Es el importe de los materiales consumidos por esta empresa en las obras que ejecuta de manera directa, constituyendo el elemento principal o auxiliar de las mismas. Se consideran los materiales entregados a subcontratistas.';
COMMENT ON COLUMN stg_enec_entidad.consumo_materiales_subcontratista IS
    'Consumo de materiales para la construcción como subcontratista (Miles de pesos corrientes). Es el importe de los materiales consumidos propiedad de la empresa, en las obras que ejecutó como subcontratista para otras constructoras, constituyendo el elemento principal o auxiliar de las mismas.';
COMMENT ON COLUMN stg_enec_entidad.ingresos_tot IS
    'Ingresos totales por suministro de bienes y servicios (Miles de pesos corrientes). Es el monto que obtuvo la empresa en el mes de referencia, por todas aquellas actividades de producción de bienes y servicios.';
COMMENT ON COLUMN stg_enec_entidad.ingresos_contratista IS
    'Ingresos por la ejecución de obras como contratista principal (Miles de pesos corrientes). Es el importe de los ingresos obtenidos por la ejecución de obras de construcción, de edificación, ingeniería civil o trabajos especiales (obra nueva, ampliación, remodelación o reparación) que realiza la empresa como contratista principal, que hayan sido concluidas o están en el proceso.';
COMMENT ON COLUMN stg_enec_entidad.ingresos_subcontratista IS
    'Ingresos por la ejecución de obras como subcontratista (Miles de pesos corrientes). Son las percepciones recibidas por la ejecución de obras de construcción, de edificación, ingeniería civil o trabajos especiales (obra nueva, ampliación, remodelación o reparación) que realizó la empresa para otros contratistas, que hayan sido concluidas o estén en proceso.';
COMMENT ON COLUMN stg_enec_entidad.ingresos_administracion IS
    'Ingresos por administración y supervisión de obras (Miles de pesos corrientes). Son los ingresos que recibe la empresa por los servicios a terceros, respecto de la supervisión o administración de obras, del manejo de los recursos materiales en la obra, el cumplimiento de los costos y las especificaciones técnicas establecidos durante la planeación para la construcción o entrega de obras, con la finalidad de que se respeten los tiempos programados, así como la calidad conforme a lo estipulado y la reglamentación vigente.';
COMMENT ON COLUMN stg_enec_entidad.ingresos_otros IS
    'Otros ingresos por suministro de obras y servicios (Miles de pesos corrientes). Son los ingresos que obtiene la empresa que no fueron considerados de manera específica en los conceptos anteriores, pero estuvieron relacionados con la actividad.';
COMMENT ON COLUMN stg_enec_entidad.valor_produccion IS
    'Valor de la producción generado en la entidad (Miles de pesos corrientes). Se refiere al monto o valor monetario que significa la realización de una obra o parte de esta. Independientemente de haber recibido o no el pago del (de la) dueño (a) o contratista de la obra.';
COMMENT ON COLUMN stg_enec_entidad.valor_produccion_edificacion IS
    'Valor de la producción de obras de Edificación (Miles de pesos corrientes). Comprende: Vivienda, edificios industriales, comerciales y de servicios, escuelas, hospitales y clínicas además de obras y trabajos auxiliares para la edificación.';
COMMENT ON COLUMN stg_enec_entidad.valor_produccion_agua_riego IS
    'Valor de la producción de obras de Agua, riego y saneamiento (Miles de pesos corrientes). Comprende: Construcción de sistema de agua potable, perforación de pozos de agua, obras de riego y trabajos auxiliares para el agua, riego y saneamiento.';
COMMENT ON COLUMN stg_enec_entidad.valor_produccion_electricidad IS
    'Valor de la producción de obras de Electricidad y telecomunicaciones (Miles de pesos corrientes). Comprende: Infraestructura para la generación y distribución de electricidad, infraestructura para telecomunicaciones, obras y trabajos auxiliares para electricidad y telecomunicaciones.';
COMMENT ON COLUMN stg_enec_entidad.valor_produccion_transporte IS
    'Valor de la producción de obras de Transporte y urbanización (Miles de pesos corrientes). Comprende: Obras de transporte en ciudades y urbanización, carreteras, caminos y puentes, obras ferroviarias, Infraestructura marítimo y fluvial, Obras y trabajos auxiliares para transporte.';
COMMENT ON COLUMN stg_enec_entidad.valor_produccion_petroleo IS
    'Valor de la producción de obras de Petróleo y petroquímica (Miles de pesos corrientes). Comprende: Refinerías y plantas petroleras, oleoductos y gaseoductos, obras y trabajos auxiliares para petróleo y petroquímica.';
COMMENT ON COLUMN stg_enec_entidad.valor_produccion_otras IS
    'Valor de la producción de obras de Otras construcciones (Miles de pesos corrientes). Comprende: Instalaciones en edificaciones, montaje de estructuras, trabajos de albañilería y acabados, obras y trabajos auxiliares para otras construcciones.';
COMMENT ON COLUMN stg_enec_entidad.valor_produccion_publico IS
    'Valor de la producción de obras del sector público (Miles de pesos corrientes). Son todas las obras que realiza una empresa constructora por encargo de una dependencia gubernamental en cualquiera de sus tres niveles: Federal, Estatal y Municipal.';
COMMENT ON COLUMN stg_enec_entidad.valor_produccion_privado IS
    'Valor de la producción de obras del sector privado (Miles de pesos corrientes). Son todas las obras que realiza una empresa constructora para cualquier particular o entidad privada, incluyendo las obras realizadas por las empresas y organismos de los diversos sectores económicos del país.';
COMMENT ON COLUMN stg_enec_entidad.estatus_id IS
    'FK a cat_estatus; indica si el registro corresponde a cifras definitivas, revisadas o preliminares.';
COMMENT ON COLUMN stg_enec_entidad.fecha_actualizacion IS
    'Fecha en que el pipeline cargó o actualizó el registro en esta base. No proviene de la fuente.';
