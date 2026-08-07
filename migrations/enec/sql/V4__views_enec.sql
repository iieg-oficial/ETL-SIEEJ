-- =============================================================================
-- V4__views_enec.sql  |  Pipeline: enec
-- vw_enec_nacional -> total nacional por actividad de la construcción
-- vw_enec_entidad  -> las 32 entidades federativas + obra en el extranjero
-- vw_enec_jalisco  -> solo Jalisco (cve_ent = 14)
-- =============================================================================

CREATE OR REPLACE VIEW vw_enec_nacional AS
SELECT
    sn.fecha,
    sn.codigo_actividad,
    ca.descripcion                  AS actividad_descripcion,
    sn.dias_trabajados,
    sn.per_ocu_tot,
    sn.per_ocu_dependiente,
    sn.per_ocu_obreros,
    sn.per_ocu_administrativos,
    sn.per_ocu_no_remunerados,
    sn.per_ocu_subcontratado,
    sn.horas_tot,
    sn.horas_dependiente,
    sn.horas_obreros,
    sn.horas_administrativos,
    sn.horas_no_remunerados,
    sn.horas_subcontratado,
    sn.remuneraciones_tot,
    sn.salarios_obreros,
    sn.sueldos_administrativos,
    sn.prestaciones,
    sn.remuneracion_media_persona,
    sn.remuneracion_media_hora,
    sn.remuneracion_media_salarios,
    sn.salario_medio_obreros,
    sn.sueldo_medio_administrativos,
    sn.gastos_tot,
    sn.gasto_materiales_contratista,
    sn.gasto_materiales_subcontratista,
    sn.gasto_suministro_personal,
    sn.gasto_subcontratistas,
    sn.gastos_otros,
    sn.consumo_materiales_contratista,
    sn.consumo_materiales_subcontratista,
    sn.ingresos_tot,
    sn.ingresos_contratista,
    sn.ingresos_subcontratista,
    sn.ingresos_administracion,
    sn.ingresos_otros,
    sn.valor_produccion,
    sn.valor_produccion_edificacion,
    sn.valor_produccion_agua_riego,
    sn.valor_produccion_electricidad,
    sn.valor_produccion_transporte,
    sn.valor_produccion_petroleo,
    sn.valor_produccion_otras,
    sn.valor_produccion_publico,
    sn.valor_produccion_privado,
    ce.estatus,
    sn.fecha_actualizacion
FROM stg_enec_nacional sn
LEFT JOIN cat_actividad ca ON ca.codigo_actividad = sn.codigo_actividad
LEFT JOIN cat_estatus ce   ON ce.id               = sn.estatus_id;

COMMENT ON VIEW vw_enec_nacional IS
    'Vista desnormalizada del total nacional de la Encuesta Nacional de Empresas Constructoras (ENEC) del INEGI, Serie 2018, con desglose por actividad de la construcción y periodicidad mensual desde enero de 2018. Publica valores absolutos, no índices.';
COMMENT ON COLUMN vw_enec_nacional.fecha IS
    'Primer día del mes de referencia de la información.';
COMMENT ON COLUMN vw_enec_nacional.codigo_actividad IS
    'Código de la actividad de la construcción en el clasificador SCIAN (23, 236, 237, 238).';
COMMENT ON COLUMN vw_enec_nacional.actividad_descripcion IS
    'Nombre de la actividad de la construcción (ej. Construcción, Edificación).';
COMMENT ON COLUMN vw_enec_nacional.dias_trabajados IS
    'Días trabajados (Número de días). Es el número total de días en que la empresa permaneció abierta realizando actividades durante el mes de referencia. Se obtiene de restar a los días naturales, los días que permaneció cerrada por descanso, festividades, huelgas, vacaciones, etcétera.';
COMMENT ON COLUMN vw_enec_nacional.per_ocu_tot IS
    'Personal ocupado total (Número de personas). Comprende al total de personal que trabajó para la empresa, dependiente y no dependiente de la misma, durante el año de referencia, sujeto a su dirección y control, cubriendo como mínimo una tercera parte de la jornada laboral de la misma, considerando hombres y mujeres.';
COMMENT ON COLUMN vw_enec_nacional.per_ocu_dependiente IS
    'Personal dependiente de la razón social (Número de personas). Comprende al personal contratado directamente por esta razón social, de planta, eventual y no remunerado, sea o no sindicalizado, que trabajó para la empresa durante el mes de referencia, sujeto a su dirección y tercera parte de la jornada laboral de la misma. Considera hombres y mujeres.';
COMMENT ON COLUMN vw_enec_nacional.per_ocu_obreros IS
    'Obreros (Número de personas). Comprende al personal que realizan trabajos de albañilería, nivelación de suelos y demás trabajos relacionados con la construcción de las obras, así como el personal vinculado con tareas auxiliares a la misma, dedicado a la provisión de materiales, almacenaje, limpieza de las obras, transporte, veladores, etcétera.';
COMMENT ON COLUMN vw_enec_nacional.per_ocu_administrativos IS
    'Empleados administrativos, contables y de dirección (Número de personas). Comprende a todas las personas que trabajaron durante el periodo de referencia dependiendo contractualmente de la empresa, sujetas a su dirección y control, a cambio de una remuneración fija y periódica por desempeñar labores generales de oficina, así como de contabilidad, ejecutivas, de planeación, organización, dirección y control para la propia empresa constructora.';
COMMENT ON COLUMN vw_enec_nacional.per_ocu_no_remunerados IS
    'Propietarios, familiares y otros trabajadores no remunerados (Número de personas). Son las personas que trabajan para la empresa cubriendo como mínimo una tercera parte de la jornada laboral de la misma, sin recibir un sueldo o salario. Se consideran a los propietarios, familiares de estos, socios activos, prestadores de servicio social, personas de programas de empleo, etcétera.';
COMMENT ON COLUMN vw_enec_nacional.per_ocu_subcontratado IS
    'Personal subcontratado (Número de personas). Son las personas que trabajaron para la empresa, pero dependen contractualmente de otra razón social.';
COMMENT ON COLUMN vw_enec_nacional.horas_tot IS
    'Horas trabajadas por el personal ocupado total (Miles de horas). Es el total de horas trabajadas durante el mes de referencia por el personal ocupado dependiente o no dependiente de la razón social en la jornada laboral, comprende las horas normales y extraordinarias dedicadas a las actividades de construcción.';
COMMENT ON COLUMN vw_enec_nacional.horas_dependiente IS
    'Horas trabajadas por personal dependiente de la razón social (Miles de horas). Es el total de horas trabajadas en el año de referencia por el personal dependiente de la razón social, comprende las horas normales y extraordinarias dedicadas a las actividades.';
COMMENT ON COLUMN vw_enec_nacional.horas_obreros IS
    'Horas trabajadas por los obreros (Miles de horas). Es el total de horas trabajadas durante el mes de referencia por los obreros en la jornada laboral; comprende las horas normales y extraordinarias dedicadas a las actividades de construcción.';
COMMENT ON COLUMN vw_enec_nacional.horas_administrativos IS
    'Horas trabajadas por los empleados administrativos, contables y de dirección (Miles de horas). Es el total de horas normales y extraordinarias efectivamente trabajadas por los empleados administrativos, contables y de dirección dependientes de la razón social.';
COMMENT ON COLUMN vw_enec_nacional.horas_no_remunerados IS
    'Horas trabajadas por los propietarios, familiares y otros trabajadores no remunerados (Miles de horas). Es el total de horas normales y extraordinarias efectivamente trabajadas por los propietarios, familiares y otros trabajadores no remunerados dependientes de la razón social.';
COMMENT ON COLUMN vw_enec_nacional.horas_subcontratado IS
    'Horas trabajadas por personal suministrado por otra razón social (Miles de horas). Es el total de horas trabajadas en el periodo de referencia por el personal ocupado contratado y proporcionado por otra razón social, comprende las horas normales y extraordinarias dedicadas a las actividades.';
COMMENT ON COLUMN vw_enec_nacional.remuneraciones_tot IS
    'Remuneraciones totales (Miles de pesos corrientes). Son todos los pagos y aportaciones normales y extraordinarias, en dinero y especie antes de cualquier deducción, para retribuir el trabajo del personal dependiente de la razón social considerando obreros(as) y empleados(as) administrativos(as) tanto de planta como eventuales, en forma de salarios y sueldos, prestaciones sociales y utilidades distribuidas al personal, ya sea que este pago se calcule sobre la base de una jornada de trabajo o por la cantidad de trabajo desarrollado (destajo), o mediante un salario base que se complementa con comisiones por ventas u otras actividades.';
COMMENT ON COLUMN vw_enec_nacional.salarios_obreros IS
    'Salarios pagados a obreros (Miles de pesos corrientes). Son los pagos que realiza la empresa para retribuir el trabajo ordinario y extraordinario del personal dependiente de la razón social considerando obreros(as), empleados(as) administrativos(as) tanto de planta como eventuales, antes de cualquier deducción retenida por las y los empleadores, como son impuesto sobre la renta o sobre el producto del trabajo, las aportaciones de los y las trabajadores a los regímenes de seguridad social (IMSS, INFONAVIT) y las cuotas sindicales.';
COMMENT ON COLUMN vw_enec_nacional.sueldos_administrativos IS
    'Sueldos pagados a empleados administrativos, contables y de dirección (Miles de pesos corrientes). Son los pagos que realizó la empresa para retribuir el trabajo ordinario y extraordinario del personal dependiente de la razón social considerando obreros(as), empleados(as) administrativos(as) tanto de planta como eventuales, antes de cualquier deducción retenida por las y los empleadores, como son impuesto sobre la renta o sobre el producto del trabajo, las aportaciones de los y las trabajadores a los regímenes de seguridad social (IMSS, INFONAVIT) y las cuotas sindicales.';
COMMENT ON COLUMN vw_enec_nacional.prestaciones IS
    'Prestaciones, contribuciones y utilidades (Miles de pesos corrientes). Son los pagos efectivamente realizados tanto contractuales como extracontractuales que proporcionó la unidad económica a los obreros y empleados, como una remuneración adicional a los sueldos y salarios, ya sea en dinero o en especie, considerando contribuciones y utilidades repartidas a los trabajadores.';
COMMENT ON COLUMN vw_enec_nacional.remuneracion_media_persona IS
    'Remuneraciones medias por persona ocupada del personal dependiente de la razón social (Pesos corrientes). Es el promedio de remuneraciones pagadas al personal dependiente de la empresa por persona. Son los pagos y aportaciones, en dinero y especie, antes de cualquier deducción, que recibió en promedio cada persona remunerada durante el periodo de referencia. Resulta de dividir el monto de las remuneraciones pagadas al personal remunerado que depende de la razón social, entre el total de personal ocupado remunerado.';
COMMENT ON COLUMN vw_enec_nacional.remuneracion_media_hora IS
    'Remuneraciones medias por hora trabajada (Pesos corrientes). Es el promedio de la remuneración pagada por hora trabajada del personal remunerado (obreros y empleados).';
COMMENT ON COLUMN vw_enec_nacional.remuneracion_media_salarios IS
    'Remuneraciones medias de salarios y sueldos (Pesos corrientes). Es el promedio de los salarios y sueldos pagados a obreros y empleados.';
COMMENT ON COLUMN vw_enec_nacional.salario_medio_obreros IS
    'Salarios medios pagados a obreros (Pesos corrientes). Son los pagos que realizó la empresa para retribuir el trabajo ordinario y extraordinario de los obreros, antes de cualquier deducción retenida por los empleadores, como son: impuesto sobre la renta o sobre el producto del trabajo, las aportaciones de los trabajadores a los regímenes de seguridad social (IMSS, INFONAVIT) y las cuotas sindicales.';
COMMENT ON COLUMN vw_enec_nacional.sueldo_medio_administrativos IS
    'Sueldos medios pagados a empleados administrativos, contables y de dirección (Pesos corrientes). Son los pagos que realizó la empresa para retribuir el trabajo ordinario y extraordinario de los obreros, antes de cualquier deducción retenida por los empleadores, como son: impuesto sobre la renta o sobre el producto del trabajo, las aportaciones de los trabajadores a los regímenes de seguridad social (IMSS, INFONAVIT) y las cuotas sindicales.';
COMMENT ON COLUMN vw_enec_nacional.gastos_tot IS
    'Gastos totales por consumo de bienes y servicios (Miles de pesos corrientes). Es el valor de todos los bienes y servicios adquiridos y/o consumidos por la empresa para realizar sus operaciones en el periodo de referencia.';
COMMENT ON COLUMN vw_enec_nacional.gasto_materiales_contratista IS
    'Gasto de materiales para la construcción como contratista principal y materiales dados a subcontratistas (Miles de pesos corrientes). Compra de materiales como contratista principal y materiales dados a subcontratistas, es el importe de los materiales comprados por esta empresa en las obras que ejecutó de manera directa, constituyendo el elemento principal o auxiliar de las mismas. Por ejemplo: tabique, varilla, arena, grava, cemento, vidrio, etcétera.';
COMMENT ON COLUMN vw_enec_nacional.gasto_materiales_subcontratista IS
    'Gasto de materiales para la construcción como subcontratista (Miles de pesos corrientes). Es el importe de los materiales comprados propiedad de la empresa, en las obras que ejecutó como subcontratista para otras constructoras, constituyendo el elemento principal o auxiliar de las mismas.';
COMMENT ON COLUMN vw_enec_nacional.gasto_suministro_personal IS
    'Pago a otra razón social por el suministro de personal (Miles de pesos corrientes). Son los pagos que realizó la empresa a otra razón social que le suministró personal para el desempeño de las actividades productivas y de apoyo.';
COMMENT ON COLUMN vw_enec_nacional.gasto_subcontratistas IS
    'Pagos a subcontratistas (Miles de pesos corrientes). Es el pago efectuado por esta empresa a terceros, denominados subcontratistas, por la ejecución de una parte de la obra o bien de la totalidad de los trabajos u obras contratadas, considerando también el valor de los materiales de construcción utilizados y que son propiedad de la empresa subcontratista.';
COMMENT ON COLUMN vw_enec_nacional.gastos_otros IS
    'Otros gastos por consumo de bienes y servicios (Miles de pesos corrientes). Son los gastos de operación normal de la empresa por los bienes y servicios que consumió, y que no fueron considerados de manera específica los conceptos anteriores, pero estuvieron relacionados con la actividad.';
COMMENT ON COLUMN vw_enec_nacional.consumo_materiales_contratista IS
    'Consumo de materiales para la construcción como contratista principal y materiales dados a subcontratistas (Miles de pesos corrientes). Es el importe de los materiales consumidos por esta empresa en las obras que ejecuta de manera directa, constituyendo el elemento principal o auxiliar de las mismas. Se consideran los materiales entregados a subcontratistas.';
COMMENT ON COLUMN vw_enec_nacional.consumo_materiales_subcontratista IS
    'Consumo de materiales para la construcción como subcontratista (Miles de pesos corrientes). Es el importe de los materiales consumidos propiedad de la empresa, en las obras que ejecutó como subcontratista para otras constructoras, constituyendo el elemento principal o auxiliar de las mismas.';
COMMENT ON COLUMN vw_enec_nacional.ingresos_tot IS
    'Ingresos totales por suministro de bienes y servicios (Miles de pesos corrientes). Es el monto que obtuvo la empresa en el mes de referencia, por todas aquellas actividades de producción de bienes y servicios.';
COMMENT ON COLUMN vw_enec_nacional.ingresos_contratista IS
    'Ingresos por la ejecución de obras como contratista principal (Miles de pesos corrientes). Es el importe de los ingresos obtenidos por la ejecución de obras de construcción, de edificación, ingeniería civil o trabajos especiales (obra nueva, ampliación, remodelación o reparación) que realiza la empresa como contratista principal, que hayan sido concluidas o están en el proceso.';
COMMENT ON COLUMN vw_enec_nacional.ingresos_subcontratista IS
    'Ingresos por la ejecución de obras como subcontratista (Miles de pesos corrientes). Son las percepciones recibidas por la ejecución de obras de construcción, de edificación, ingeniería civil o trabajos especiales (obra nueva, ampliación, remodelación o reparación) que realizó la empresa para otros contratistas, que hayan sido concluidas o estén en proceso.';
COMMENT ON COLUMN vw_enec_nacional.ingresos_administracion IS
    'Ingresos por administración y supervisión de obras (Miles de pesos corrientes). Son los ingresos que recibe la empresa por los servicios a terceros, respecto de la supervisión o administración de obras, del manejo de los recursos materiales en la obra, el cumplimiento de los costos y las especificaciones técnicas establecidos durante la planeación para la construcción o entrega de obras, con la finalidad de que se respeten los tiempos programados, así como la calidad conforme a lo estipulado y la reglamentación vigente.';
COMMENT ON COLUMN vw_enec_nacional.ingresos_otros IS
    'Otros ingresos por suministro de obras y servicios (Miles de pesos corrientes). Son los ingresos que obtiene la empresa que no fueron considerados de manera específica en los conceptos anteriores, pero estuvieron relacionados con la actividad.';
COMMENT ON COLUMN vw_enec_nacional.valor_produccion IS
    'Valor de la producción generado en la entidad (Miles de pesos corrientes). Se refiere al monto o valor monetario que significa la realización de una obra o parte de esta. Independientemente de haber recibido o no el pago del (de la) dueño (a) o contratista de la obra.';
COMMENT ON COLUMN vw_enec_nacional.valor_produccion_edificacion IS
    'Valor de la producción de obras de Edificación (Miles de pesos corrientes). Comprende: Vivienda, edificios industriales, comerciales y de servicios, escuelas, hospitales y clínicas además de obras y trabajos auxiliares para la edificación.';
COMMENT ON COLUMN vw_enec_nacional.valor_produccion_agua_riego IS
    'Valor de la producción de obras de Agua, riego y saneamiento (Miles de pesos corrientes). Comprende: Construcción de sistema de agua potable, perforación de pozos de agua, obras de riego y trabajos auxiliares para el agua, riego y saneamiento.';
COMMENT ON COLUMN vw_enec_nacional.valor_produccion_electricidad IS
    'Valor de la producción de obras de Electricidad y telecomunicaciones (Miles de pesos corrientes). Comprende: Infraestructura para la generación y distribución de electricidad, infraestructura para telecomunicaciones, obras y trabajos auxiliares para electricidad y telecomunicaciones.';
COMMENT ON COLUMN vw_enec_nacional.valor_produccion_transporte IS
    'Valor de la producción de obras de Transporte y urbanización (Miles de pesos corrientes). Comprende: Obras de transporte en ciudades y urbanización, carreteras, caminos y puentes, obras ferroviarias, Infraestructura marítimo y fluvial, Obras y trabajos auxiliares para transporte.';
COMMENT ON COLUMN vw_enec_nacional.valor_produccion_petroleo IS
    'Valor de la producción de obras de Petróleo y petroquímica (Miles de pesos corrientes). Comprende: Refinerías y plantas petroleras, oleoductos y gaseoductos, obras y trabajos auxiliares para petróleo y petroquímica.';
COMMENT ON COLUMN vw_enec_nacional.valor_produccion_otras IS
    'Valor de la producción de obras de Otras construcciones (Miles de pesos corrientes). Comprende: Instalaciones en edificaciones, montaje de estructuras, trabajos de albañilería y acabados, obras y trabajos auxiliares para otras construcciones.';
COMMENT ON COLUMN vw_enec_nacional.valor_produccion_publico IS
    'Valor de la producción de obras del sector público (Miles de pesos corrientes). Son todas las obras que realiza una empresa constructora por encargo de una dependencia gubernamental en cualquiera de sus tres niveles: Federal, Estatal y Municipal.';
COMMENT ON COLUMN vw_enec_nacional.valor_produccion_privado IS
    'Valor de la producción de obras del sector privado (Miles de pesos corrientes). Son todas las obras que realiza una empresa constructora para cualquier particular o entidad privada, incluyendo las obras realizadas por las empresas y organismos de los diversos sectores económicos del país.';
COMMENT ON COLUMN vw_enec_nacional.estatus IS
    'Estatus de los datos: Cifras definitivas, Cifras revisadas o Cifras preliminares.';
COMMENT ON COLUMN vw_enec_nacional.fecha_actualizacion IS
    'Fecha en que el pipeline cargó o actualizó el registro en esta base.';


CREATE OR REPLACE VIEW vw_enec_entidad AS
SELECT
    se.fecha,
    se.entidad_id,
    CASE se.entidad_id
        WHEN 33 THEN 'Obra en el extranjero'
        ELSE e.nom_ent
    END                             AS entidad,
    se.dias_trabajados,
    se.per_ocu_tot,
    se.per_ocu_dependiente,
    se.per_ocu_obreros,
    se.per_ocu_administrativos,
    se.per_ocu_no_remunerados,
    se.per_ocu_subcontratado,
    se.horas_tot,
    se.horas_dependiente,
    se.horas_obreros,
    se.horas_administrativos,
    se.horas_no_remunerados,
    se.horas_subcontratado,
    se.remuneraciones_tot,
    se.salarios_obreros,
    se.sueldos_administrativos,
    se.prestaciones,
    se.remuneracion_media_persona,
    se.remuneracion_media_hora,
    se.remuneracion_media_salarios,
    se.salario_medio_obreros,
    se.sueldo_medio_administrativos,
    se.gastos_tot,
    se.gasto_materiales_contratista,
    se.gasto_materiales_subcontratista,
    se.gasto_suministro_personal,
    se.gasto_subcontratistas,
    se.gastos_otros,
    se.consumo_materiales_contratista,
    se.consumo_materiales_subcontratista,
    se.ingresos_tot,
    se.ingresos_contratista,
    se.ingresos_subcontratista,
    se.ingresos_administracion,
    se.ingresos_otros,
    se.valor_produccion,
    se.valor_produccion_edificacion,
    se.valor_produccion_agua_riego,
    se.valor_produccion_electricidad,
    se.valor_produccion_transporte,
    se.valor_produccion_petroleo,
    se.valor_produccion_otras,
    se.valor_produccion_publico,
    se.valor_produccion_privado,
    ce.estatus,
    se.fecha_actualizacion
FROM stg_enec_entidad se
LEFT JOIN cvegeo_states e ON e.cve_ent = se.entidad_id
LEFT JOIN cat_estatus ce  ON ce.id     = se.estatus_id;

COMMENT ON VIEW vw_enec_entidad IS
    'Vista desnormalizada del desglose por entidad federativa de la Encuesta Nacional de Empresas Constructoras (ENEC) del INEGI, Serie 2018, mensual desde enero de 2018. Cubre solo el sector 23 (construcción). Incluye la clave 33, Obra en el extranjero, que no es una entidad federativa pero sí forma parte del total nacional; se etiqueta con un CASE porque no cruza contra cvegeo_states.';
COMMENT ON COLUMN vw_enec_entidad.fecha IS
    'Primer día del mes de referencia de la información.';
COMMENT ON COLUMN vw_enec_entidad.entidad_id IS
    'Clave de la entidad federativa (1 a 32), más la clave 33 para la obra ejecutada en el extranjero.';
COMMENT ON COLUMN vw_enec_entidad.entidad IS
    'Nombre de la entidad federativa, u Obra en el extranjero para la clave 33.';
COMMENT ON COLUMN vw_enec_entidad.dias_trabajados IS
    'Días trabajados (Número de días). Es el número total de días en que la empresa permaneció abierta realizando actividades durante el mes de referencia. Se obtiene de restar a los días naturales, los días que permaneció cerrada por descanso, festividades, huelgas, vacaciones, etcétera.';
COMMENT ON COLUMN vw_enec_entidad.per_ocu_tot IS
    'Personal ocupado total (Número de personas). Comprende al total de personal que trabajó para la empresa, dependiente y no dependiente de la misma, durante el año de referencia, sujeto a su dirección y control, cubriendo como mínimo una tercera parte de la jornada laboral de la misma, considerando hombres y mujeres.';
COMMENT ON COLUMN vw_enec_entidad.per_ocu_dependiente IS
    'Personal dependiente de la razón social (Número de personas). Comprende al personal contratado directamente por esta razón social, de planta, eventual y no remunerado, sea o no sindicalizado, que trabajó para la empresa durante el mes de referencia, sujeto a su dirección y tercera parte de la jornada laboral de la misma. Considera hombres y mujeres.';
COMMENT ON COLUMN vw_enec_entidad.per_ocu_obreros IS
    'Obreros (Número de personas). Comprende al personal que realizan trabajos de albañilería, nivelación de suelos y demás trabajos relacionados con la construcción de las obras, así como el personal vinculado con tareas auxiliares a la misma, dedicado a la provisión de materiales, almacenaje, limpieza de las obras, transporte, veladores, etcétera.';
COMMENT ON COLUMN vw_enec_entidad.per_ocu_administrativos IS
    'Empleados administrativos, contables y de dirección (Número de personas). Comprende a todas las personas que trabajaron durante el periodo de referencia dependiendo contractualmente de la empresa, sujetas a su dirección y control, a cambio de una remuneración fija y periódica por desempeñar labores generales de oficina, así como de contabilidad, ejecutivas, de planeación, organización, dirección y control para la propia empresa constructora.';
COMMENT ON COLUMN vw_enec_entidad.per_ocu_no_remunerados IS
    'Propietarios, familiares y otros trabajadores no remunerados (Número de personas). Son las personas que trabajan para la empresa cubriendo como mínimo una tercera parte de la jornada laboral de la misma, sin recibir un sueldo o salario. Se consideran a los propietarios, familiares de estos, socios activos, prestadores de servicio social, personas de programas de empleo, etcétera.';
COMMENT ON COLUMN vw_enec_entidad.per_ocu_subcontratado IS
    'Personal subcontratado (Número de personas). Son las personas que trabajaron para la empresa, pero dependen contractualmente de otra razón social.';
COMMENT ON COLUMN vw_enec_entidad.horas_tot IS
    'Horas trabajadas por el personal ocupado total (Miles de horas). Es el total de horas trabajadas durante el mes de referencia por el personal ocupado dependiente o no dependiente de la razón social en la jornada laboral, comprende las horas normales y extraordinarias dedicadas a las actividades de construcción.';
COMMENT ON COLUMN vw_enec_entidad.horas_dependiente IS
    'Horas trabajadas por personal dependiente de la razón social (Miles de horas). Es el total de horas trabajadas en el año de referencia por el personal dependiente de la razón social, comprende las horas normales y extraordinarias dedicadas a las actividades.';
COMMENT ON COLUMN vw_enec_entidad.horas_obreros IS
    'Horas trabajadas por los obreros (Miles de horas). Es el total de horas trabajadas durante el mes de referencia por los obreros en la jornada laboral; comprende las horas normales y extraordinarias dedicadas a las actividades de construcción.';
COMMENT ON COLUMN vw_enec_entidad.horas_administrativos IS
    'Horas trabajadas por los empleados administrativos, contables y de dirección (Miles de horas). Es el total de horas normales y extraordinarias efectivamente trabajadas por los empleados administrativos, contables y de dirección dependientes de la razón social.';
COMMENT ON COLUMN vw_enec_entidad.horas_no_remunerados IS
    'Horas trabajadas por los propietarios, familiares y otros trabajadores no remunerados (Miles de horas). Es el total de horas normales y extraordinarias efectivamente trabajadas por los propietarios, familiares y otros trabajadores no remunerados dependientes de la razón social.';
COMMENT ON COLUMN vw_enec_entidad.horas_subcontratado IS
    'Horas trabajadas por personal suministrado por otra razón social (Miles de horas). Es el total de horas trabajadas en el periodo de referencia por el personal ocupado contratado y proporcionado por otra razón social, comprende las horas normales y extraordinarias dedicadas a las actividades.';
COMMENT ON COLUMN vw_enec_entidad.remuneraciones_tot IS
    'Remuneraciones totales (Miles de pesos corrientes). Son todos los pagos y aportaciones normales y extraordinarias, en dinero y especie antes de cualquier deducción, para retribuir el trabajo del personal dependiente de la razón social considerando obreros(as) y empleados(as) administrativos(as) tanto de planta como eventuales, en forma de salarios y sueldos, prestaciones sociales y utilidades distribuidas al personal, ya sea que este pago se calcule sobre la base de una jornada de trabajo o por la cantidad de trabajo desarrollado (destajo), o mediante un salario base que se complementa con comisiones por ventas u otras actividades.';
COMMENT ON COLUMN vw_enec_entidad.salarios_obreros IS
    'Salarios pagados a obreros (Miles de pesos corrientes). Son los pagos que realiza la empresa para retribuir el trabajo ordinario y extraordinario del personal dependiente de la razón social considerando obreros(as), empleados(as) administrativos(as) tanto de planta como eventuales, antes de cualquier deducción retenida por las y los empleadores, como son impuesto sobre la renta o sobre el producto del trabajo, las aportaciones de los y las trabajadores a los regímenes de seguridad social (IMSS, INFONAVIT) y las cuotas sindicales.';
COMMENT ON COLUMN vw_enec_entidad.sueldos_administrativos IS
    'Sueldos pagados a empleados administrativos, contables y de dirección (Miles de pesos corrientes). Son los pagos que realizó la empresa para retribuir el trabajo ordinario y extraordinario del personal dependiente de la razón social considerando obreros(as), empleados(as) administrativos(as) tanto de planta como eventuales, antes de cualquier deducción retenida por las y los empleadores, como son impuesto sobre la renta o sobre el producto del trabajo, las aportaciones de los y las trabajadores a los regímenes de seguridad social (IMSS, INFONAVIT) y las cuotas sindicales.';
COMMENT ON COLUMN vw_enec_entidad.prestaciones IS
    'Prestaciones, contribuciones y utilidades (Miles de pesos corrientes). Son los pagos efectivamente realizados tanto contractuales como extracontractuales que proporcionó la unidad económica a los obreros y empleados, como una remuneración adicional a los sueldos y salarios, ya sea en dinero o en especie, considerando contribuciones y utilidades repartidas a los trabajadores.';
COMMENT ON COLUMN vw_enec_entidad.remuneracion_media_persona IS
    'Remuneraciones medias por persona ocupada del personal dependiente de la razón social (Pesos corrientes). Es el promedio de remuneraciones pagadas al personal dependiente de la empresa por persona. Son los pagos y aportaciones, en dinero y especie, antes de cualquier deducción, que recibió en promedio cada persona remunerada durante el periodo de referencia. Resulta de dividir el monto de las remuneraciones pagadas al personal remunerado que depende de la razón social, entre el total de personal ocupado remunerado.';
COMMENT ON COLUMN vw_enec_entidad.remuneracion_media_hora IS
    'Remuneraciones medias por hora trabajada (Pesos corrientes). Es el promedio de la remuneración pagada por hora trabajada del personal remunerado (obreros y empleados).';
COMMENT ON COLUMN vw_enec_entidad.remuneracion_media_salarios IS
    'Remuneraciones medias de salarios y sueldos (Pesos corrientes). Es el promedio de los salarios y sueldos pagados a obreros y empleados.';
COMMENT ON COLUMN vw_enec_entidad.salario_medio_obreros IS
    'Salarios medios pagados a obreros (Pesos corrientes). Son los pagos que realizó la empresa para retribuir el trabajo ordinario y extraordinario de los obreros, antes de cualquier deducción retenida por los empleadores, como son: impuesto sobre la renta o sobre el producto del trabajo, las aportaciones de los trabajadores a los regímenes de seguridad social (IMSS, INFONAVIT) y las cuotas sindicales.';
COMMENT ON COLUMN vw_enec_entidad.sueldo_medio_administrativos IS
    'Sueldos medios pagados a empleados administrativos, contables y de dirección (Pesos corrientes). Son los pagos que realizó la empresa para retribuir el trabajo ordinario y extraordinario de los obreros, antes de cualquier deducción retenida por los empleadores, como son: impuesto sobre la renta o sobre el producto del trabajo, las aportaciones de los trabajadores a los regímenes de seguridad social (IMSS, INFONAVIT) y las cuotas sindicales.';
COMMENT ON COLUMN vw_enec_entidad.gastos_tot IS
    'Gastos totales por consumo de bienes y servicios (Miles de pesos corrientes). Es el valor de todos los bienes y servicios adquiridos y/o consumidos por la empresa para realizar sus operaciones en el periodo de referencia.';
COMMENT ON COLUMN vw_enec_entidad.gasto_materiales_contratista IS
    'Gasto de materiales para la construcción como contratista principal y materiales dados a subcontratistas (Miles de pesos corrientes). Compra de materiales como contratista principal y materiales dados a subcontratistas, es el importe de los materiales comprados por esta empresa en las obras que ejecutó de manera directa, constituyendo el elemento principal o auxiliar de las mismas. Por ejemplo: tabique, varilla, arena, grava, cemento, vidrio, etcétera.';
COMMENT ON COLUMN vw_enec_entidad.gasto_materiales_subcontratista IS
    'Gasto de materiales para la construcción como subcontratista (Miles de pesos corrientes). Es el importe de los materiales comprados propiedad de la empresa, en las obras que ejecutó como subcontratista para otras constructoras, constituyendo el elemento principal o auxiliar de las mismas.';
COMMENT ON COLUMN vw_enec_entidad.gasto_suministro_personal IS
    'Pago a otra razón social por el suministro de personal (Miles de pesos corrientes). Son los pagos que realizó la empresa a otra razón social que le suministró personal para el desempeño de las actividades productivas y de apoyo.';
COMMENT ON COLUMN vw_enec_entidad.gasto_subcontratistas IS
    'Pagos a subcontratistas (Miles de pesos corrientes). Es el pago efectuado por esta empresa a terceros, denominados subcontratistas, por la ejecución de una parte de la obra o bien de la totalidad de los trabajos u obras contratadas, considerando también el valor de los materiales de construcción utilizados y que son propiedad de la empresa subcontratista.';
COMMENT ON COLUMN vw_enec_entidad.gastos_otros IS
    'Otros gastos por consumo de bienes y servicios (Miles de pesos corrientes). Son los gastos de operación normal de la empresa por los bienes y servicios que consumió, y que no fueron considerados de manera específica los conceptos anteriores, pero estuvieron relacionados con la actividad.';
COMMENT ON COLUMN vw_enec_entidad.consumo_materiales_contratista IS
    'Consumo de materiales para la construcción como contratista principal y materiales dados a subcontratistas (Miles de pesos corrientes). Es el importe de los materiales consumidos por esta empresa en las obras que ejecuta de manera directa, constituyendo el elemento principal o auxiliar de las mismas. Se consideran los materiales entregados a subcontratistas.';
COMMENT ON COLUMN vw_enec_entidad.consumo_materiales_subcontratista IS
    'Consumo de materiales para la construcción como subcontratista (Miles de pesos corrientes). Es el importe de los materiales consumidos propiedad de la empresa, en las obras que ejecutó como subcontratista para otras constructoras, constituyendo el elemento principal o auxiliar de las mismas.';
COMMENT ON COLUMN vw_enec_entidad.ingresos_tot IS
    'Ingresos totales por suministro de bienes y servicios (Miles de pesos corrientes). Es el monto que obtuvo la empresa en el mes de referencia, por todas aquellas actividades de producción de bienes y servicios.';
COMMENT ON COLUMN vw_enec_entidad.ingresos_contratista IS
    'Ingresos por la ejecución de obras como contratista principal (Miles de pesos corrientes). Es el importe de los ingresos obtenidos por la ejecución de obras de construcción, de edificación, ingeniería civil o trabajos especiales (obra nueva, ampliación, remodelación o reparación) que realiza la empresa como contratista principal, que hayan sido concluidas o están en el proceso.';
COMMENT ON COLUMN vw_enec_entidad.ingresos_subcontratista IS
    'Ingresos por la ejecución de obras como subcontratista (Miles de pesos corrientes). Son las percepciones recibidas por la ejecución de obras de construcción, de edificación, ingeniería civil o trabajos especiales (obra nueva, ampliación, remodelación o reparación) que realizó la empresa para otros contratistas, que hayan sido concluidas o estén en proceso.';
COMMENT ON COLUMN vw_enec_entidad.ingresos_administracion IS
    'Ingresos por administración y supervisión de obras (Miles de pesos corrientes). Son los ingresos que recibe la empresa por los servicios a terceros, respecto de la supervisión o administración de obras, del manejo de los recursos materiales en la obra, el cumplimiento de los costos y las especificaciones técnicas establecidos durante la planeación para la construcción o entrega de obras, con la finalidad de que se respeten los tiempos programados, así como la calidad conforme a lo estipulado y la reglamentación vigente.';
COMMENT ON COLUMN vw_enec_entidad.ingresos_otros IS
    'Otros ingresos por suministro de obras y servicios (Miles de pesos corrientes). Son los ingresos que obtiene la empresa que no fueron considerados de manera específica en los conceptos anteriores, pero estuvieron relacionados con la actividad.';
COMMENT ON COLUMN vw_enec_entidad.valor_produccion IS
    'Valor de la producción generado en la entidad (Miles de pesos corrientes). Se refiere al monto o valor monetario que significa la realización de una obra o parte de esta. Independientemente de haber recibido o no el pago del (de la) dueño (a) o contratista de la obra.';
COMMENT ON COLUMN vw_enec_entidad.valor_produccion_edificacion IS
    'Valor de la producción de obras de Edificación (Miles de pesos corrientes). Comprende: Vivienda, edificios industriales, comerciales y de servicios, escuelas, hospitales y clínicas además de obras y trabajos auxiliares para la edificación.';
COMMENT ON COLUMN vw_enec_entidad.valor_produccion_agua_riego IS
    'Valor de la producción de obras de Agua, riego y saneamiento (Miles de pesos corrientes). Comprende: Construcción de sistema de agua potable, perforación de pozos de agua, obras de riego y trabajos auxiliares para el agua, riego y saneamiento.';
COMMENT ON COLUMN vw_enec_entidad.valor_produccion_electricidad IS
    'Valor de la producción de obras de Electricidad y telecomunicaciones (Miles de pesos corrientes). Comprende: Infraestructura para la generación y distribución de electricidad, infraestructura para telecomunicaciones, obras y trabajos auxiliares para electricidad y telecomunicaciones.';
COMMENT ON COLUMN vw_enec_entidad.valor_produccion_transporte IS
    'Valor de la producción de obras de Transporte y urbanización (Miles de pesos corrientes). Comprende: Obras de transporte en ciudades y urbanización, carreteras, caminos y puentes, obras ferroviarias, Infraestructura marítimo y fluvial, Obras y trabajos auxiliares para transporte.';
COMMENT ON COLUMN vw_enec_entidad.valor_produccion_petroleo IS
    'Valor de la producción de obras de Petróleo y petroquímica (Miles de pesos corrientes). Comprende: Refinerías y plantas petroleras, oleoductos y gaseoductos, obras y trabajos auxiliares para petróleo y petroquímica.';
COMMENT ON COLUMN vw_enec_entidad.valor_produccion_otras IS
    'Valor de la producción de obras de Otras construcciones (Miles de pesos corrientes). Comprende: Instalaciones en edificaciones, montaje de estructuras, trabajos de albañilería y acabados, obras y trabajos auxiliares para otras construcciones.';
COMMENT ON COLUMN vw_enec_entidad.valor_produccion_publico IS
    'Valor de la producción de obras del sector público (Miles de pesos corrientes). Son todas las obras que realiza una empresa constructora por encargo de una dependencia gubernamental en cualquiera de sus tres niveles: Federal, Estatal y Municipal.';
COMMENT ON COLUMN vw_enec_entidad.valor_produccion_privado IS
    'Valor de la producción de obras del sector privado (Miles de pesos corrientes). Son todas las obras que realiza una empresa constructora para cualquier particular o entidad privada, incluyendo las obras realizadas por las empresas y organismos de los diversos sectores económicos del país.';
COMMENT ON COLUMN vw_enec_entidad.estatus IS
    'Estatus de los datos: Cifras definitivas, Cifras revisadas o Cifras preliminares.';
COMMENT ON COLUMN vw_enec_entidad.fecha_actualizacion IS
    'Fecha en que el pipeline cargó o actualizó el registro en esta base.';


CREATE OR REPLACE VIEW vw_enec_jalisco AS
SELECT
    se.fecha,
    se.dias_trabajados,
    se.per_ocu_tot,
    se.per_ocu_dependiente,
    se.per_ocu_obreros,
    se.per_ocu_administrativos,
    se.per_ocu_no_remunerados,
    se.per_ocu_subcontratado,
    se.horas_tot,
    se.horas_dependiente,
    se.horas_obreros,
    se.horas_administrativos,
    se.horas_no_remunerados,
    se.horas_subcontratado,
    se.remuneraciones_tot,
    se.salarios_obreros,
    se.sueldos_administrativos,
    se.prestaciones,
    se.remuneracion_media_persona,
    se.remuneracion_media_hora,
    se.remuneracion_media_salarios,
    se.salario_medio_obreros,
    se.sueldo_medio_administrativos,
    se.gastos_tot,
    se.gasto_materiales_contratista,
    se.gasto_materiales_subcontratista,
    se.gasto_suministro_personal,
    se.gasto_subcontratistas,
    se.gastos_otros,
    se.consumo_materiales_contratista,
    se.consumo_materiales_subcontratista,
    se.ingresos_tot,
    se.ingresos_contratista,
    se.ingresos_subcontratista,
    se.ingresos_administracion,
    se.ingresos_otros,
    se.valor_produccion,
    se.valor_produccion_edificacion,
    se.valor_produccion_agua_riego,
    se.valor_produccion_electricidad,
    se.valor_produccion_transporte,
    se.valor_produccion_petroleo,
    se.valor_produccion_otras,
    se.valor_produccion_publico,
    se.valor_produccion_privado,
    ce.estatus,
    se.fecha_actualizacion
FROM stg_enec_entidad se
LEFT JOIN cat_estatus ce ON ce.id = se.estatus_id
WHERE se.entidad_id = 14;

COMMENT ON VIEW vw_enec_jalisco IS
    'Misma información que vw_enec_entidad, acotada a Jalisco (clave de entidad 14). La entidad se omite de las columnas porque es constante.';
COMMENT ON COLUMN vw_enec_jalisco.fecha IS
    'Primer día del mes de referencia de la información.';
COMMENT ON COLUMN vw_enec_jalisco.dias_trabajados IS
    'Días trabajados (Número de días). Es el número total de días en que la empresa permaneció abierta realizando actividades durante el mes de referencia. Se obtiene de restar a los días naturales, los días que permaneció cerrada por descanso, festividades, huelgas, vacaciones, etcétera.';
COMMENT ON COLUMN vw_enec_jalisco.per_ocu_tot IS
    'Personal ocupado total (Número de personas). Comprende al total de personal que trabajó para la empresa, dependiente y no dependiente de la misma, durante el año de referencia, sujeto a su dirección y control, cubriendo como mínimo una tercera parte de la jornada laboral de la misma, considerando hombres y mujeres.';
COMMENT ON COLUMN vw_enec_jalisco.per_ocu_dependiente IS
    'Personal dependiente de la razón social (Número de personas). Comprende al personal contratado directamente por esta razón social, de planta, eventual y no remunerado, sea o no sindicalizado, que trabajó para la empresa durante el mes de referencia, sujeto a su dirección y tercera parte de la jornada laboral de la misma. Considera hombres y mujeres.';
COMMENT ON COLUMN vw_enec_jalisco.per_ocu_obreros IS
    'Obreros (Número de personas). Comprende al personal que realizan trabajos de albañilería, nivelación de suelos y demás trabajos relacionados con la construcción de las obras, así como el personal vinculado con tareas auxiliares a la misma, dedicado a la provisión de materiales, almacenaje, limpieza de las obras, transporte, veladores, etcétera.';
COMMENT ON COLUMN vw_enec_jalisco.per_ocu_administrativos IS
    'Empleados administrativos, contables y de dirección (Número de personas). Comprende a todas las personas que trabajaron durante el periodo de referencia dependiendo contractualmente de la empresa, sujetas a su dirección y control, a cambio de una remuneración fija y periódica por desempeñar labores generales de oficina, así como de contabilidad, ejecutivas, de planeación, organización, dirección y control para la propia empresa constructora.';
COMMENT ON COLUMN vw_enec_jalisco.per_ocu_no_remunerados IS
    'Propietarios, familiares y otros trabajadores no remunerados (Número de personas). Son las personas que trabajan para la empresa cubriendo como mínimo una tercera parte de la jornada laboral de la misma, sin recibir un sueldo o salario. Se consideran a los propietarios, familiares de estos, socios activos, prestadores de servicio social, personas de programas de empleo, etcétera.';
COMMENT ON COLUMN vw_enec_jalisco.per_ocu_subcontratado IS
    'Personal subcontratado (Número de personas). Son las personas que trabajaron para la empresa, pero dependen contractualmente de otra razón social.';
COMMENT ON COLUMN vw_enec_jalisco.horas_tot IS
    'Horas trabajadas por el personal ocupado total (Miles de horas). Es el total de horas trabajadas durante el mes de referencia por el personal ocupado dependiente o no dependiente de la razón social en la jornada laboral, comprende las horas normales y extraordinarias dedicadas a las actividades de construcción.';
COMMENT ON COLUMN vw_enec_jalisco.horas_dependiente IS
    'Horas trabajadas por personal dependiente de la razón social (Miles de horas). Es el total de horas trabajadas en el año de referencia por el personal dependiente de la razón social, comprende las horas normales y extraordinarias dedicadas a las actividades.';
COMMENT ON COLUMN vw_enec_jalisco.horas_obreros IS
    'Horas trabajadas por los obreros (Miles de horas). Es el total de horas trabajadas durante el mes de referencia por los obreros en la jornada laboral; comprende las horas normales y extraordinarias dedicadas a las actividades de construcción.';
COMMENT ON COLUMN vw_enec_jalisco.horas_administrativos IS
    'Horas trabajadas por los empleados administrativos, contables y de dirección (Miles de horas). Es el total de horas normales y extraordinarias efectivamente trabajadas por los empleados administrativos, contables y de dirección dependientes de la razón social.';
COMMENT ON COLUMN vw_enec_jalisco.horas_no_remunerados IS
    'Horas trabajadas por los propietarios, familiares y otros trabajadores no remunerados (Miles de horas). Es el total de horas normales y extraordinarias efectivamente trabajadas por los propietarios, familiares y otros trabajadores no remunerados dependientes de la razón social.';
COMMENT ON COLUMN vw_enec_jalisco.horas_subcontratado IS
    'Horas trabajadas por personal suministrado por otra razón social (Miles de horas). Es el total de horas trabajadas en el periodo de referencia por el personal ocupado contratado y proporcionado por otra razón social, comprende las horas normales y extraordinarias dedicadas a las actividades.';
COMMENT ON COLUMN vw_enec_jalisco.remuneraciones_tot IS
    'Remuneraciones totales (Miles de pesos corrientes). Son todos los pagos y aportaciones normales y extraordinarias, en dinero y especie antes de cualquier deducción, para retribuir el trabajo del personal dependiente de la razón social considerando obreros(as) y empleados(as) administrativos(as) tanto de planta como eventuales, en forma de salarios y sueldos, prestaciones sociales y utilidades distribuidas al personal, ya sea que este pago se calcule sobre la base de una jornada de trabajo o por la cantidad de trabajo desarrollado (destajo), o mediante un salario base que se complementa con comisiones por ventas u otras actividades.';
COMMENT ON COLUMN vw_enec_jalisco.salarios_obreros IS
    'Salarios pagados a obreros (Miles de pesos corrientes). Son los pagos que realiza la empresa para retribuir el trabajo ordinario y extraordinario del personal dependiente de la razón social considerando obreros(as), empleados(as) administrativos(as) tanto de planta como eventuales, antes de cualquier deducción retenida por las y los empleadores, como son impuesto sobre la renta o sobre el producto del trabajo, las aportaciones de los y las trabajadores a los regímenes de seguridad social (IMSS, INFONAVIT) y las cuotas sindicales.';
COMMENT ON COLUMN vw_enec_jalisco.sueldos_administrativos IS
    'Sueldos pagados a empleados administrativos, contables y de dirección (Miles de pesos corrientes). Son los pagos que realizó la empresa para retribuir el trabajo ordinario y extraordinario del personal dependiente de la razón social considerando obreros(as), empleados(as) administrativos(as) tanto de planta como eventuales, antes de cualquier deducción retenida por las y los empleadores, como son impuesto sobre la renta o sobre el producto del trabajo, las aportaciones de los y las trabajadores a los regímenes de seguridad social (IMSS, INFONAVIT) y las cuotas sindicales.';
COMMENT ON COLUMN vw_enec_jalisco.prestaciones IS
    'Prestaciones, contribuciones y utilidades (Miles de pesos corrientes). Son los pagos efectivamente realizados tanto contractuales como extracontractuales que proporcionó la unidad económica a los obreros y empleados, como una remuneración adicional a los sueldos y salarios, ya sea en dinero o en especie, considerando contribuciones y utilidades repartidas a los trabajadores.';
COMMENT ON COLUMN vw_enec_jalisco.remuneracion_media_persona IS
    'Remuneraciones medias por persona ocupada del personal dependiente de la razón social (Pesos corrientes). Es el promedio de remuneraciones pagadas al personal dependiente de la empresa por persona. Son los pagos y aportaciones, en dinero y especie, antes de cualquier deducción, que recibió en promedio cada persona remunerada durante el periodo de referencia. Resulta de dividir el monto de las remuneraciones pagadas al personal remunerado que depende de la razón social, entre el total de personal ocupado remunerado.';
COMMENT ON COLUMN vw_enec_jalisco.remuneracion_media_hora IS
    'Remuneraciones medias por hora trabajada (Pesos corrientes). Es el promedio de la remuneración pagada por hora trabajada del personal remunerado (obreros y empleados).';
COMMENT ON COLUMN vw_enec_jalisco.remuneracion_media_salarios IS
    'Remuneraciones medias de salarios y sueldos (Pesos corrientes). Es el promedio de los salarios y sueldos pagados a obreros y empleados.';
COMMENT ON COLUMN vw_enec_jalisco.salario_medio_obreros IS
    'Salarios medios pagados a obreros (Pesos corrientes). Son los pagos que realizó la empresa para retribuir el trabajo ordinario y extraordinario de los obreros, antes de cualquier deducción retenida por los empleadores, como son: impuesto sobre la renta o sobre el producto del trabajo, las aportaciones de los trabajadores a los regímenes de seguridad social (IMSS, INFONAVIT) y las cuotas sindicales.';
COMMENT ON COLUMN vw_enec_jalisco.sueldo_medio_administrativos IS
    'Sueldos medios pagados a empleados administrativos, contables y de dirección (Pesos corrientes). Son los pagos que realizó la empresa para retribuir el trabajo ordinario y extraordinario de los obreros, antes de cualquier deducción retenida por los empleadores, como son: impuesto sobre la renta o sobre el producto del trabajo, las aportaciones de los trabajadores a los regímenes de seguridad social (IMSS, INFONAVIT) y las cuotas sindicales.';
COMMENT ON COLUMN vw_enec_jalisco.gastos_tot IS
    'Gastos totales por consumo de bienes y servicios (Miles de pesos corrientes). Es el valor de todos los bienes y servicios adquiridos y/o consumidos por la empresa para realizar sus operaciones en el periodo de referencia.';
COMMENT ON COLUMN vw_enec_jalisco.gasto_materiales_contratista IS
    'Gasto de materiales para la construcción como contratista principal y materiales dados a subcontratistas (Miles de pesos corrientes). Compra de materiales como contratista principal y materiales dados a subcontratistas, es el importe de los materiales comprados por esta empresa en las obras que ejecutó de manera directa, constituyendo el elemento principal o auxiliar de las mismas. Por ejemplo: tabique, varilla, arena, grava, cemento, vidrio, etcétera.';
COMMENT ON COLUMN vw_enec_jalisco.gasto_materiales_subcontratista IS
    'Gasto de materiales para la construcción como subcontratista (Miles de pesos corrientes). Es el importe de los materiales comprados propiedad de la empresa, en las obras que ejecutó como subcontratista para otras constructoras, constituyendo el elemento principal o auxiliar de las mismas.';
COMMENT ON COLUMN vw_enec_jalisco.gasto_suministro_personal IS
    'Pago a otra razón social por el suministro de personal (Miles de pesos corrientes). Son los pagos que realizó la empresa a otra razón social que le suministró personal para el desempeño de las actividades productivas y de apoyo.';
COMMENT ON COLUMN vw_enec_jalisco.gasto_subcontratistas IS
    'Pagos a subcontratistas (Miles de pesos corrientes). Es el pago efectuado por esta empresa a terceros, denominados subcontratistas, por la ejecución de una parte de la obra o bien de la totalidad de los trabajos u obras contratadas, considerando también el valor de los materiales de construcción utilizados y que son propiedad de la empresa subcontratista.';
COMMENT ON COLUMN vw_enec_jalisco.gastos_otros IS
    'Otros gastos por consumo de bienes y servicios (Miles de pesos corrientes). Son los gastos de operación normal de la empresa por los bienes y servicios que consumió, y que no fueron considerados de manera específica los conceptos anteriores, pero estuvieron relacionados con la actividad.';
COMMENT ON COLUMN vw_enec_jalisco.consumo_materiales_contratista IS
    'Consumo de materiales para la construcción como contratista principal y materiales dados a subcontratistas (Miles de pesos corrientes). Es el importe de los materiales consumidos por esta empresa en las obras que ejecuta de manera directa, constituyendo el elemento principal o auxiliar de las mismas. Se consideran los materiales entregados a subcontratistas.';
COMMENT ON COLUMN vw_enec_jalisco.consumo_materiales_subcontratista IS
    'Consumo de materiales para la construcción como subcontratista (Miles de pesos corrientes). Es el importe de los materiales consumidos propiedad de la empresa, en las obras que ejecutó como subcontratista para otras constructoras, constituyendo el elemento principal o auxiliar de las mismas.';
COMMENT ON COLUMN vw_enec_jalisco.ingresos_tot IS
    'Ingresos totales por suministro de bienes y servicios (Miles de pesos corrientes). Es el monto que obtuvo la empresa en el mes de referencia, por todas aquellas actividades de producción de bienes y servicios.';
COMMENT ON COLUMN vw_enec_jalisco.ingresos_contratista IS
    'Ingresos por la ejecución de obras como contratista principal (Miles de pesos corrientes). Es el importe de los ingresos obtenidos por la ejecución de obras de construcción, de edificación, ingeniería civil o trabajos especiales (obra nueva, ampliación, remodelación o reparación) que realiza la empresa como contratista principal, que hayan sido concluidas o están en el proceso.';
COMMENT ON COLUMN vw_enec_jalisco.ingresos_subcontratista IS
    'Ingresos por la ejecución de obras como subcontratista (Miles de pesos corrientes). Son las percepciones recibidas por la ejecución de obras de construcción, de edificación, ingeniería civil o trabajos especiales (obra nueva, ampliación, remodelación o reparación) que realizó la empresa para otros contratistas, que hayan sido concluidas o estén en proceso.';
COMMENT ON COLUMN vw_enec_jalisco.ingresos_administracion IS
    'Ingresos por administración y supervisión de obras (Miles de pesos corrientes). Son los ingresos que recibe la empresa por los servicios a terceros, respecto de la supervisión o administración de obras, del manejo de los recursos materiales en la obra, el cumplimiento de los costos y las especificaciones técnicas establecidos durante la planeación para la construcción o entrega de obras, con la finalidad de que se respeten los tiempos programados, así como la calidad conforme a lo estipulado y la reglamentación vigente.';
COMMENT ON COLUMN vw_enec_jalisco.ingresos_otros IS
    'Otros ingresos por suministro de obras y servicios (Miles de pesos corrientes). Son los ingresos que obtiene la empresa que no fueron considerados de manera específica en los conceptos anteriores, pero estuvieron relacionados con la actividad.';
COMMENT ON COLUMN vw_enec_jalisco.valor_produccion IS
    'Valor de la producción generado en la entidad (Miles de pesos corrientes). Se refiere al monto o valor monetario que significa la realización de una obra o parte de esta. Independientemente de haber recibido o no el pago del (de la) dueño (a) o contratista de la obra.';
COMMENT ON COLUMN vw_enec_jalisco.valor_produccion_edificacion IS
    'Valor de la producción de obras de Edificación (Miles de pesos corrientes). Comprende: Vivienda, edificios industriales, comerciales y de servicios, escuelas, hospitales y clínicas además de obras y trabajos auxiliares para la edificación.';
COMMENT ON COLUMN vw_enec_jalisco.valor_produccion_agua_riego IS
    'Valor de la producción de obras de Agua, riego y saneamiento (Miles de pesos corrientes). Comprende: Construcción de sistema de agua potable, perforación de pozos de agua, obras de riego y trabajos auxiliares para el agua, riego y saneamiento.';
COMMENT ON COLUMN vw_enec_jalisco.valor_produccion_electricidad IS
    'Valor de la producción de obras de Electricidad y telecomunicaciones (Miles de pesos corrientes). Comprende: Infraestructura para la generación y distribución de electricidad, infraestructura para telecomunicaciones, obras y trabajos auxiliares para electricidad y telecomunicaciones.';
COMMENT ON COLUMN vw_enec_jalisco.valor_produccion_transporte IS
    'Valor de la producción de obras de Transporte y urbanización (Miles de pesos corrientes). Comprende: Obras de transporte en ciudades y urbanización, carreteras, caminos y puentes, obras ferroviarias, Infraestructura marítimo y fluvial, Obras y trabajos auxiliares para transporte.';
COMMENT ON COLUMN vw_enec_jalisco.valor_produccion_petroleo IS
    'Valor de la producción de obras de Petróleo y petroquímica (Miles de pesos corrientes). Comprende: Refinerías y plantas petroleras, oleoductos y gaseoductos, obras y trabajos auxiliares para petróleo y petroquímica.';
COMMENT ON COLUMN vw_enec_jalisco.valor_produccion_otras IS
    'Valor de la producción de obras de Otras construcciones (Miles de pesos corrientes). Comprende: Instalaciones en edificaciones, montaje de estructuras, trabajos de albañilería y acabados, obras y trabajos auxiliares para otras construcciones.';
COMMENT ON COLUMN vw_enec_jalisco.valor_produccion_publico IS
    'Valor de la producción de obras del sector público (Miles de pesos corrientes). Son todas las obras que realiza una empresa constructora por encargo de una dependencia gubernamental en cualquiera de sus tres niveles: Federal, Estatal y Municipal.';
COMMENT ON COLUMN vw_enec_jalisco.valor_produccion_privado IS
    'Valor de la producción de obras del sector privado (Miles de pesos corrientes). Son todas las obras que realiza una empresa constructora para cualquier particular o entidad privada, incluyendo las obras realizadas por las empresas y organismos de los diversos sectores económicos del país.';
COMMENT ON COLUMN vw_enec_jalisco.estatus IS
    'Estatus de los datos: Cifras definitivas, Cifras revisadas o Cifras preliminares.';
COMMENT ON COLUMN vw_enec_jalisco.fecha_actualizacion IS
    'Fecha en que el pipeline cargó o actualizó el registro en esta base.';
