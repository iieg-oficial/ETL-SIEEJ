CREATE TABLE IF NOT EXISTS stg_economico_nacional_2019 (
    id                                        SERIAL PRIMARY KEY,
    censo_id                              INTEGER NOT NULL REFERENCES cat_censos(id),
    actividad_economica_id          INTEGER REFERENCES cat_actividades_economicas(id),
    estrato_id                      INTEGER REFERENCES cat_estratos(id),
    prod_bruta_tot_mdp                                      FLOAT,
    part_bienes_elab_gen_ext_pbt                            FLOAT,
    part_imatmpp                                            FLOAT,
    part_act_fijos_producidos_uso_propio_pb                 FLOAT,
    part_var_exist_prod_proceso_pbt                         FLOAT,
    part_mar_rev_merc_pbt                                   FLOAT,
    part_serv_prof_cient_tec_pbt                            FLOAT,
    part_ingr_abmi_produccion                               FLOAT,
    part_otros_comp_pbt                                     FLOAT,
    consu_intermedio_mdp                                    FLOAT,
    valor_agregado_censal_bruto_mdp                         FLOAT,
    part_ssen_tr                                            FLOAT,
    part_salarios_ppvs_tr                                   FLOAT,
    part_sueldos_pers_acd_tr                                FLOAT,
    pers_dependiente_pers_ocup_tot_porcentaje               FLOAT,
    pnr_perasonal_ocupado_tot                               FLOAT,
    pnr_po_dependiente                                      FLOAT,
    prest_soc_util_rep_tot_rem                              FLOAT,
    part_urt_tr                                             FLOAT,
    part_mt_pers_remu                                       FLOAT,
    part_mt_po_produccion_ventas_servicios                  FLOAT,
    part_mt_po_acd                                          FLOAT,
    prest_soc_tot_rem                                       FLOAT,
    part_prestaciones_sociales_utilidades_sueldos_salarios  FLOAT,
    part_mt_pfotn                                           FLOAT,
    tot_prestaciones_ss                                     FLOAT,
    part_mt_pcpor                                           FLOAT,
    part_mt_phcs                                            FLOAT,
    remuneracion_media_per_ocupada_remu                     FLOAT,
    salario_pers_operativo_anual                            FLOAT,
    sueldo_pers_administrativo_anual                        FLOAT,
    pagos_promedio_per_suministrada                         FLOAT,
    pagos_promedio_pers_comisiones_u_honorarios             FLOAT,
    part_remuneraciones_gcbs                                FLOAT,
    per_no_dep_pers_ocup_tot                                FLOAT,
    indem_liqui_remu_tot                                    FLOAT,
    remuneracion_media_per_remu                             FLOAT,
    horas_dia_trab_prom_pers_remu                           FLOAT,
    horas_dia_trab_prom_pers_no_remu                        FLOAT,
    horas_dia_trab_prom_ppvs                                FLOAT,
    horas_dia_trab_prom_empleados_administrativos_control   FLOAT,
    horas_dia_trab_prom_pers_comisiones_honorarios          FLOAT,
    valor_agregado_censal_bruto_pbt                         FLOAT,
    part_consu_intermedio_pbt                               FLOAT,
    va_promedio_per_ocupada                                 FLOAT,
    pbt_pers_ocupado_tot                                    FLOAT,
    part_mpms_gastos_consu_bienes                           FLOAT,
    part_mcs_gcbs                                           FLOAT,
    inversion_tot_mdp                                       FLOAT,
    part_cae_gcbs                                           FLOAT,
    inversion_ti_tot                                        FLOAT,
    part_gastos_consu_otros_bienes_servicios_gastos_consu   FLOAT,
    inversion_tot_act_fijos                                 FLOAT,
    part_ivm_ti_suministro_bienes                           FLOAT,
    inversion_tot_valor_agregado_censal_bruto               FLOAT,
    part_servi_prof_cient                                   FLOAT,
    part_otros_isbs_ti                                      FLOAT,
    form_brut_cap_mdp                                       FLOAT,
    inversion_tot_pbt                                       FLOAT,
    part_venta_productos_elaborados_generados_o_extraidos_tot FLOAT,
    part_ingr_abmi_tot                                      FLOAT,
    part_imatmpp_2                                          FLOAT,
    part_mep_tot_act_fijos                                  FLOAT,
    part_cif_tot_act_fijos                                  FLOAT,
    part_et_tot_act_fijos                                   FLOAT,
    part_ecp_tot_act_fijos                                  FLOAT,
    margen_bruto_operacion                                  FLOAT,
    ing_princ_por_sum_bienes                                FLOAT,
    gp_gcbs                                                 FLOAT,
    gp_ip                                                   FLOAT,
    part_meo_otros_act_fijos_tot                            FLOAT,
    valor_act_fijos_per_ocupada                             FLOAT,
    maqui_equip_prod_a_prod_tot                             FLOAT,
    acti_fijo_brut_tot                                      FLOAT,
    forma_brut_cap_fijo_acervo_tot                          FLOAT,
    produccion_act_fijos_uso_propio_compras_act_fijos       FLOAT,
    otros_isbs_ti_suministro                                FLOAT,
    gastos_no_derivados_actividad_gcbs                      FLOAT,
    ingr_no_derivados_actividad_isbs                        FLOAT,
    valor_promedio_maquinaria_equipo_per_ocupada_anuales    FLOAT,
    ip_respecto_gp                                          FLOAT,
    porcentaje_ip_ti_actividad_financieros                  FLOAT,
    isbs_per_ocupada                                        FLOAT,
    mar_por_rev_mdp                                         FLOAT,
    part_depreciacion_valor_act_fijos                       FLOAT,
    tasa_rentabilidad_promedio                              FLOAT,
    gastos_tot_mdp                                          FLOAT,
    salario_promedio_diarios_per_operativa                  FLOAT,
    sueldo_promedio_diario_per_administrativa               FLOAT,
    va_tot_act_fijos                                        FLOAT,
    part_muje_pers_ocupado_tot                              FLOAT,
    ingr_tot_general_mdp                                    FLOAT,
    pers_dep_razon_social                                   FLOAT,
    pers_dep_razon_social_h                                 FLOAT,
    pers_dep_razon_social_m                                 FLOAT,
    horas_pers_dep_razon_social_mh                          FLOAT,
    pers_ocupado_tot                                        FLOAT,
    pers_ocupado_tot_h                                      FLOAT,
    pers_ocupado_tot_m                                      FLOAT,
    horas_pers_ocupado_tot_mh                               FLOAT,
    pers_remu                                               FLOAT,
    pers_remu_h                                             FLOAT,
    pers_remu_m                                             FLOAT,
    horas_pers_remu_mh                                      FLOAT,
    pers_no_remu                                            FLOAT,
    pers_no_remu_h                                          FLOAT,
    pers_no_remu_m                                          FLOAT,
    horas_pers_no_remu_mh                                   FLOAT,
    pers_prod_ventas_servicios                              FLOAT,
    pers_prod_ventas_servicios_h                            FLOAT,
    pers_prod_ventas_servicios_m                            FLOAT,
    horas_pers_prod_ventas_servicios_mh                     FLOAT,
    pers_admin_contable_direccion                           FLOAT,
    pers_admin_contable_direccion_h                         FLOAT,
    pers_admin_contable_direccion_m                         FLOAT,
    horas_pers_admin_contable_direccion_mh                  FLOAT,
    pers_no_dep_razon_social                                FLOAT,
    pers_no_dep_razon_social_h                              FLOAT,
    pers_no_dep_razon_social_m                              FLOAT,
    horas_pers_no_dep_razon_social_mh                       FLOAT,
    pers_contratado_otra_razon_social                       FLOAT,
    pers_contratado_otra_razon_social_h                     FLOAT,
    pers_contratado_otra_razon_social_m                     FLOAT,
    horas_pers_contratado_otra_razon_social_mh              FLOAT,
    pers_honorarios                                         FLOAT,
    pers_honorarios_h                                       FLOAT,
    pers_honorarios_m                                       FLOAT,
    horas_pers_honorarios_mh                                FLOAT,
    remuneraciones_tot_mdp                                  FLOAT,
    salarios_pers_prod_ventas_servicios_mdp                 FLOAT,
    sueldos_pers_admin_contable_direccion_mdp               FLOAT,
    contribuciones_seguridad_social_mdp                     FLOAT,
    otras_prestaciones_sociales_mdp                         FLOAT,
    utilidades_repartidas_mdp                               FLOAT,
    indemnizacion_liquidacion_mdp                           FLOAT,
    gastos_consu_tot_mdp                                    FLOAT,
    mercancias_compradas_reventa_mdp                        FLOAT,
    materiales_servicios_mdp                                FLOAT,
    materias_primas_mdp                                     FLOAT,
    combustibles_lubricantes_energeticos_mdp                FLOAT,
    renta_alquiler_bienes_mdp                               FLOAT,
    servicios_profesionales_mdp                             FLOAT,
    maquila_servicios_produccion_mdp                        FLOAT,
    otros_bienes_servicios_mdp                              FLOAT,
    fletes_productos_vendidos_mdp                           FLOAT,
    papeleria_oficina_mdp                                   FLOAT,
    energia_electrica_mdp                                   FLOAT,
    pagos_pers_subcontratado_mdp                            FLOAT,
    honorarios_comisiones_mdp                               FLOAT,
    publicidad_mdp                                          FLOAT,
    servicios_comunicacion_mdp                              FLOAT,
    envases_empaques_mdp                                    FLOAT,
    reparaciones_refacciones_mdp                            FLOAT,
    consu_agua_mdp                                          FLOAT,
    ingr_tot_mdp                                            FLOAT,
    ingr_reventa_mercancias_mdp                             FLOAT,
    ingr_servicios_profesionales_mdp                        FLOAT,
    ingr_venta_productos_mdp                                FLOAT,
    ingr_alquiler_bienes_mdp                                FLOAT,
    otros_ingr_mdp                                          FLOAT,
    otros_componentes_prod_bruta_mdp                        FLOAT,
    ingr_maquila_terceros_mdp                               FLOAT,
    valor_productos_elaborados_mdp                          FLOAT,
    act_fijos_uso_propio_mdp                                FLOAT,
    invent_inic_mdp                                         FLOAT,
    invent_final_mdp                                        FLOAT,
    var_exis_mdp                                            FLOAT,
    invent_inic_proceso_mdp                                 FLOAT,
    invent_final_proceso_mdp                                FLOAT,
    var_invent_proceso_mdp                                  FLOAT,
    invent_inic_reventa_mdp                                 FLOAT,
    invent_final_reventa_mdp                                FLOAT,
    acervo_act_fijos_mdp                                    FLOAT,
    depreciacion_act_fijos_mdp                              FLOAT,
    compra_act_fijos_mdp                                    FLOAT,
    ventas_act_fijos_mdp                                    FLOAT,
    acervo_maquinaria_equipo_mdp                            FLOAT,
    acervo_bienes_inmuebles_mdp                             FLOAT,
    acervo_unidades_transporte_mdp                          FLOAT,
    acervo_equipo_computo_mdp                               FLOAT,
    acervo_mobiliario_oficina_mdp                           FLOAT,
    unidades_economicas                                     FLOAT
);
COMMENT ON COLUMN stg_economico_nacional_2019.censo_id IS 'Referencia al censo economico';
COMMENT ON COLUMN stg_economico_nacional_2019.actividad_economica_id IS 'Referencia a la actividad economica SCIAN';
COMMENT ON COLUMN stg_economico_nacional_2019.estrato_id IS 'Referencia al estrato de personal ocupado';
COMMENT ON COLUMN stg_economico_nacional_2019.prod_bruta_tot_mdp IS 'Produccion bruta total (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.part_bienes_elab_gen_ext_pbt IS 'Participacion del valor de bienes elaborados, generados o extraidos en la produccion bruta total';
COMMENT ON COLUMN stg_economico_nacional_2019.part_imatmpp IS 'Participacion de ingresos por maquilar o transformar materias primas propiedad de terceros';
COMMENT ON COLUMN stg_economico_nacional_2019.part_act_fijos_producidos_uso_propio_pb IS 'Participacion de activos fijos producidos para uso propio en la produccion bruta';
COMMENT ON COLUMN stg_economico_nacional_2019.part_var_exist_prod_proceso_pbt IS 'Participacion de la variacion de existencias de productos en proceso en la produccion bruta total';
COMMENT ON COLUMN stg_economico_nacional_2019.part_mar_rev_merc_pbt IS 'Participacion del margen por reventa de mercancias en la produccion bruta total';
COMMENT ON COLUMN stg_economico_nacional_2019.part_serv_prof_cient_tec_pbt IS 'Participacion de servicios profesionales, cientificos y tecnicos en la produccion bruta';
COMMENT ON COLUMN stg_economico_nacional_2019.part_ingr_abmi_produccion IS 'Participacion de ingresos por alquiler de bienes muebles e inmuebles en la produccion';
COMMENT ON COLUMN stg_economico_nacional_2019.part_otros_comp_pbt IS 'Participacion de otros componentes de la produccion bruta total';
COMMENT ON COLUMN stg_economico_nacional_2019.consu_intermedio_mdp IS 'Consumo intermedio (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.valor_agregado_censal_bruto_mdp IS 'Valor agregado censal bruto (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.part_ssen_tr IS 'Participacion de salarios y sueldos en el total de remuneraciones';
COMMENT ON COLUMN stg_economico_nacional_2019.part_salarios_ppvs_tr IS 'Participacion de salarios al personal de produccion, ventas y servicios en el total de remuneraciones';
COMMENT ON COLUMN stg_economico_nacional_2019.part_sueldos_pers_acd_tr IS 'Participacion de sueldos al personal administrativo, contable y de direccion en el total de remuneraciones';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_dependiente_pers_ocup_tot_porcentaje IS 'Personal dependiente sobre personal ocupado total (porcentaje)';
COMMENT ON COLUMN stg_economico_nacional_2019.pnr_perasonal_ocupado_tot IS 'Personal no remunerado sobre personal ocupado total';
COMMENT ON COLUMN stg_economico_nacional_2019.pnr_po_dependiente IS 'Personal no remunerado sobre personal ocupado dependiente';
COMMENT ON COLUMN stg_economico_nacional_2019.prest_soc_util_rep_tot_rem IS 'Prestaciones sociales y utilidades repartidas sobre el total de remuneraciones';
COMMENT ON COLUMN stg_economico_nacional_2019.part_urt_tr IS 'Participacion de utilidades repartidas a trabajadores en el total de remuneraciones';
COMMENT ON COLUMN stg_economico_nacional_2019.part_mt_pers_remu IS 'Participacion de mujeres en el total de personal remunerado';
COMMENT ON COLUMN stg_economico_nacional_2019.part_mt_po_produccion_ventas_servicios IS 'Participacion de mujeres en el total de personal de produccion, ventas y servicios';
COMMENT ON COLUMN stg_economico_nacional_2019.part_mt_po_acd IS 'Participacion de mujeres en el total de personal administrativo, contable y de direccion';
COMMENT ON COLUMN stg_economico_nacional_2019.prest_soc_tot_rem IS 'Prestaciones sociales sobre el total de remuneraciones';
COMMENT ON COLUMN stg_economico_nacional_2019.part_prestaciones_sociales_utilidades_sueldos_salarios IS 'Participacion de prestaciones sociales y utilidades sobre sueldos y salarios';
COMMENT ON COLUMN stg_economico_nacional_2019.part_mt_pfotn IS 'Participacion de mujeres en el total de propietarios, familiares y otros trabajadores no remunerados';
COMMENT ON COLUMN stg_economico_nacional_2019.tot_prestaciones_ss IS 'Total de prestaciones sobre salarios y sueldos';
COMMENT ON COLUMN stg_economico_nacional_2019.part_mt_pcpor IS 'Participacion de mujeres en el total de personal contratado y proporcionado por otra razon social';
COMMENT ON COLUMN stg_economico_nacional_2019.part_mt_phcs IS 'Participacion de mujeres en el total de personal por honorarios o comisiones sin sueldo fijo';
COMMENT ON COLUMN stg_economico_nacional_2019.remuneracion_media_per_ocupada_remu IS 'Remuneracion media por persona ocupada remunerada';
COMMENT ON COLUMN stg_economico_nacional_2019.salario_pers_operativo_anual IS 'Salario al personal operativo (anual)';
COMMENT ON COLUMN stg_economico_nacional_2019.sueldo_pers_administrativo_anual IS 'Sueldo al personal administrativo (anual)';
COMMENT ON COLUMN stg_economico_nacional_2019.pagos_promedio_per_suministrada IS 'Pagos promedio por persona suministrada';
COMMENT ON COLUMN stg_economico_nacional_2019.pagos_promedio_pers_comisiones_u_honorarios IS 'Pagos promedio al personal por comisiones u honorarios';
COMMENT ON COLUMN stg_economico_nacional_2019.part_remuneraciones_gcbs IS 'Participacion de remuneraciones en gastos por consumo de bienes y servicios';
COMMENT ON COLUMN stg_economico_nacional_2019.per_no_dep_pers_ocup_tot IS 'Personal no dependiente sobre personal ocupado total';
COMMENT ON COLUMN stg_economico_nacional_2019.indem_liqui_remu_tot IS 'Indemnizaciones y liquidaciones sobre remuneraciones totales';
COMMENT ON COLUMN stg_economico_nacional_2019.remuneracion_media_per_remu IS 'Remuneracion media por persona remunerada';
COMMENT ON COLUMN stg_economico_nacional_2019.horas_dia_trab_prom_pers_remu IS 'Horas diarias trabajadas promedio por personal remunerado';
COMMENT ON COLUMN stg_economico_nacional_2019.horas_dia_trab_prom_pers_no_remu IS 'Horas diarias trabajadas promedio por personal no remunerado';
COMMENT ON COLUMN stg_economico_nacional_2019.horas_dia_trab_prom_ppvs IS 'Horas diarias trabajadas promedio por personal de produccion, ventas y servicios';
COMMENT ON COLUMN stg_economico_nacional_2019.horas_dia_trab_prom_empleados_administrativos_control IS 'Horas diarias trabajadas promedio por empleados administrativos y de control';
COMMENT ON COLUMN stg_economico_nacional_2019.horas_dia_trab_prom_pers_comisiones_honorarios IS 'Horas diarias trabajadas promedio por personal por comisiones u honorarios';
COMMENT ON COLUMN stg_economico_nacional_2019.valor_agregado_censal_bruto_pbt IS 'Valor agregado censal bruto sobre la produccion bruta total';
COMMENT ON COLUMN stg_economico_nacional_2019.part_consu_intermedio_pbt IS 'Participacion del consumo intermedio en la produccion bruta total';
COMMENT ON COLUMN stg_economico_nacional_2019.va_promedio_per_ocupada IS 'Valor agregado promedio por persona ocupada';
COMMENT ON COLUMN stg_economico_nacional_2019.pbt_pers_ocupado_tot IS 'Produccion bruta total sobre personal ocupado total';
COMMENT ON COLUMN stg_economico_nacional_2019.part_mpms_gastos_consu_bienes IS 'Participacion de materias primas, materiales y suministros en gastos por consumo de bienes';
COMMENT ON COLUMN stg_economico_nacional_2019.part_mcs_gcbs IS 'Participacion de maquila y contratacion de servicios en gastos por consumo de bienes y servicios';
COMMENT ON COLUMN stg_economico_nacional_2019.inversion_tot_mdp IS 'Inversion total (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.part_cae_gcbs IS 'Participacion del consumo de agua y energeticos en gastos por consumo de bienes y servicios';
COMMENT ON COLUMN stg_economico_nacional_2019.inversion_ti_tot IS 'Inversion total sobre ingresos totales';
COMMENT ON COLUMN stg_economico_nacional_2019.part_gastos_consu_otros_bienes_servicios_gastos_consu IS 'Participacion de gastos por consumo de otros bienes y servicios en gastos por consumo';
COMMENT ON COLUMN stg_economico_nacional_2019.inversion_tot_act_fijos IS 'Inversion total sobre activos fijos';
COMMENT ON COLUMN stg_economico_nacional_2019.part_ivm_ti_suministro_bienes IS 'Participacion de ingresos por venta de mercancias en el total de ingresos por suministro de bienes';
COMMENT ON COLUMN stg_economico_nacional_2019.inversion_tot_valor_agregado_censal_bruto IS 'Inversion total sobre valor agregado censal bruto';
COMMENT ON COLUMN stg_economico_nacional_2019.part_servi_prof_cient IS 'Participacion de servicios profesionales, cientificos y tecnicos en el total de ingresos';
COMMENT ON COLUMN stg_economico_nacional_2019.part_otros_isbs_ti IS 'Participacion de otros ingresos por suministro de bienes y servicios en el total de ingresos';
COMMENT ON COLUMN stg_economico_nacional_2019.form_brut_cap_mdp IS 'Formacion bruta de capital fijo (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.inversion_tot_pbt IS 'Inversion total sobre la produccion bruta total';
COMMENT ON COLUMN stg_economico_nacional_2019.part_venta_productos_elaborados_generados_o_extraidos_tot IS 'Participacion de la venta de productos elaborados, generados o extraidos en el total';
COMMENT ON COLUMN stg_economico_nacional_2019.part_ingr_abmi_tot IS 'Participacion de ingresos por alquiler de bienes muebles e inmuebles en el total';
COMMENT ON COLUMN stg_economico_nacional_2019.part_imatmpp_2 IS 'Participacion de ingresos por maquilar o transformar materias primas propiedad de terceros (2)';
COMMENT ON COLUMN stg_economico_nacional_2019.part_mep_tot_act_fijos IS 'Participacion de maquinaria y equipo de produccion en el total de activos fijos';
COMMENT ON COLUMN stg_economico_nacional_2019.part_cif_tot_act_fijos IS 'Participacion de construcciones e instalaciones fijas en el total de activos fijos';
COMMENT ON COLUMN stg_economico_nacional_2019.part_et_tot_act_fijos IS 'Participacion del equipo de transporte en el total de activos fijos';
COMMENT ON COLUMN stg_economico_nacional_2019.part_ecp_tot_act_fijos IS 'Participacion del equipo de computo y perifericos en el total de activos fijos';
COMMENT ON COLUMN stg_economico_nacional_2019.margen_bruto_operacion IS 'Margen bruto de operacion';
COMMENT ON COLUMN stg_economico_nacional_2019.ing_princ_por_sum_bienes IS 'Ingreso principal sobre ingresos por suministro de bienes y servicios';
COMMENT ON COLUMN stg_economico_nacional_2019.gp_gcbs IS 'Gasto principal sobre gastos por consumo de bienes y servicios';
COMMENT ON COLUMN stg_economico_nacional_2019.gp_ip IS 'Gasto principal sobre ingreso principal';
COMMENT ON COLUMN stg_economico_nacional_2019.part_meo_otros_act_fijos_tot IS 'Participacion de mobiliario y equipo de oficina y otros activos fijos en el total';
COMMENT ON COLUMN stg_economico_nacional_2019.valor_act_fijos_per_ocupada IS 'Valor de activos fijos por persona ocupada';
COMMENT ON COLUMN stg_economico_nacional_2019.maqui_equip_prod_a_prod_tot IS 'Maquinaria y equipo de produccion sobre la produccion bruta total';
COMMENT ON COLUMN stg_economico_nacional_2019.acti_fijo_brut_tot IS 'Activos fijos sobre la produccion bruta total';
COMMENT ON COLUMN stg_economico_nacional_2019.forma_brut_cap_fijo_acervo_tot IS 'Formacion bruta de capital fijo sobre acervo de capital';
COMMENT ON COLUMN stg_economico_nacional_2019.produccion_act_fijos_uso_propio_compras_act_fijos IS 'Produccion de activos fijos para uso propio sobre compras de activos fijos';
COMMENT ON COLUMN stg_economico_nacional_2019.otros_isbs_ti_suministro IS 'Otros ingresos por suministro de bienes y servicios sobre el total de ingresos por suministro';
COMMENT ON COLUMN stg_economico_nacional_2019.gastos_no_derivados_actividad_gcbs IS 'Gastos no derivados de la actividad sobre gastos por consumo de bienes y servicios';
COMMENT ON COLUMN stg_economico_nacional_2019.ingr_no_derivados_actividad_isbs IS 'Ingresos no derivados de la actividad sobre ingresos por suministro de bienes y servicios';
COMMENT ON COLUMN stg_economico_nacional_2019.valor_promedio_maquinaria_equipo_per_ocupada_anuales IS 'Valor promedio de maquinaria y equipo por persona ocupada (anuales)';
COMMENT ON COLUMN stg_economico_nacional_2019.ip_respecto_gp IS 'Ingreso principal respecto al gasto principal';
COMMENT ON COLUMN stg_economico_nacional_2019.porcentaje_ip_ti_actividad_financieros IS 'Porcentaje del ingreso principal en el total de ingresos por actividades financieras';
COMMENT ON COLUMN stg_economico_nacional_2019.isbs_per_ocupada IS 'Ingresos por suministro de bienes y servicios por persona ocupada';
COMMENT ON COLUMN stg_economico_nacional_2019.mar_por_rev_mdp IS 'Margen por reventa de mercancias (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.part_depreciacion_valor_act_fijos IS 'Participacion de la depreciacion en el valor de activos fijos';
COMMENT ON COLUMN stg_economico_nacional_2019.tasa_rentabilidad_promedio IS 'Tasa de rentabilidad promedio';
COMMENT ON COLUMN stg_economico_nacional_2019.gastos_tot_mdp IS 'Total de gastos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.salario_promedio_diarios_per_operativa IS 'Salario promedio diario por persona operativa';
COMMENT ON COLUMN stg_economico_nacional_2019.sueldo_promedio_diario_per_administrativa IS 'Sueldo promedio diario por persona administrativa';
COMMENT ON COLUMN stg_economico_nacional_2019.va_tot_act_fijos IS 'Valor agregado total sobre activos fijos';
COMMENT ON COLUMN stg_economico_nacional_2019.part_muje_pers_ocupado_tot IS 'Participacion de mujeres en el personal ocupado total';
COMMENT ON COLUMN stg_economico_nacional_2019.ingr_tot_general_mdp IS 'Total de ingresos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_dep_razon_social IS 'Personal dependiente de la razon social total';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_dep_razon_social_h IS 'Personal dependiente de la razon social, hombres';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_dep_razon_social_m IS 'Personal dependiente de la razon social, mujeres';
COMMENT ON COLUMN stg_economico_nacional_2019.horas_pers_dep_razon_social_mh IS 'Horas trabajadas por personal dependiente de la razon social (miles de horas)';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_ocupado_tot IS 'Personal ocupado total';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_ocupado_tot_h IS 'Personal ocupado total, hombres';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_ocupado_tot_m IS 'Personal ocupado total, mujeres';
COMMENT ON COLUMN stg_economico_nacional_2019.horas_pers_ocupado_tot_mh IS 'Horas trabajadas por personal ocupado total (miles de horas)';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_remu IS 'Personal remunerado total';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_remu_h IS 'Personal remunerado, hombres';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_remu_m IS 'Personal remunerado, mujeres';
COMMENT ON COLUMN stg_economico_nacional_2019.horas_pers_remu_mh IS 'Horas trabajadas por personal remunerado (miles de horas)';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_no_remu IS 'Personas propietarias, familiares y otro personal no remunerado total';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_no_remu_h IS 'Personas propietarias, familiares y otro personal no remunerado, hombres';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_no_remu_m IS 'Personas propietarias, familiares y otro personal no remunerado, mujeres';
COMMENT ON COLUMN stg_economico_nacional_2019.horas_pers_no_remu_mh IS 'Horas trabajadas por personal no remunerado (miles de horas)';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_prod_ventas_servicios IS 'Personal de produccion, ventas y servicios total';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_prod_ventas_servicios_h IS 'Personal de produccion, ventas y servicios, hombres';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_prod_ventas_servicios_m IS 'Personal de produccion, ventas y servicios, mujeres';
COMMENT ON COLUMN stg_economico_nacional_2019.horas_pers_prod_ventas_servicios_mh IS 'Horas trabajadas por personal de produccion, ventas y servicios (miles de horas)';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_admin_contable_direccion IS 'Personal administrativo, contable y de direccion total';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_admin_contable_direccion_h IS 'Personal administrativo, contable y de direccion, hombres';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_admin_contable_direccion_m IS 'Personal administrativo, contable y de direccion, mujeres';
COMMENT ON COLUMN stg_economico_nacional_2019.horas_pers_admin_contable_direccion_mh IS 'Horas trabajadas por personal administrativo, contable y de direccion (miles de horas)';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_no_dep_razon_social IS 'Personal no dependiente de la razon social total';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_no_dep_razon_social_h IS 'Personal no dependiente de la razon social, hombres';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_no_dep_razon_social_m IS 'Personal no dependiente de la razon social, mujeres';
COMMENT ON COLUMN stg_economico_nacional_2019.horas_pers_no_dep_razon_social_mh IS 'Horas trabajadas por personal no dependiente de la razon social (miles de horas)';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_contratado_otra_razon_social IS 'Personal contratado y proporcionado por otra razon social total';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_contratado_otra_razon_social_h IS 'Personal contratado y proporcionado por otra razon social, hombres';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_contratado_otra_razon_social_m IS 'Personal contratado y proporcionado por otra razon social, mujeres';
COMMENT ON COLUMN stg_economico_nacional_2019.horas_pers_contratado_otra_razon_social_mh IS 'Horas trabajadas por personal contratado por otra razon social (miles de horas)';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_honorarios IS 'Personal por honorarios o comisiones sin sueldo o salario fijo total';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_honorarios_h IS 'Personal por honorarios o comisiones sin sueldo o salario fijo, hombres';
COMMENT ON COLUMN stg_economico_nacional_2019.pers_honorarios_m IS 'Personal por honorarios o comisiones sin sueldo o salario fijo, mujeres';
COMMENT ON COLUMN stg_economico_nacional_2019.horas_pers_honorarios_mh IS 'Horas trabajadas por personal por honorarios (miles de horas)';
COMMENT ON COLUMN stg_economico_nacional_2019.remuneraciones_tot_mdp IS 'Total de remuneraciones (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.salarios_pers_prod_ventas_servicios_mdp IS 'Total de salarios al personal de produccion, ventas y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.sueldos_pers_admin_contable_direccion_mdp IS 'Total de sueldos al personal administrativo, contable y de direccion (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.contribuciones_seguridad_social_mdp IS 'Contribuciones patronales a regimenes de seguridad social (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.otras_prestaciones_sociales_mdp IS 'Otras prestaciones sociales (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.utilidades_repartidas_mdp IS 'Utilidades repartidas al personal (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.indemnizacion_liquidacion_mdp IS 'Gastos por indemnizacion o liquidacion del personal (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.gastos_consu_tot_mdp IS 'Total de gastos por consumo de bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.mercancias_compradas_reventa_mdp IS 'Mercancias y bienes comprados para la reventa (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.materiales_servicios_mdp IS 'Materiales e insumos consumidos para la prestacion de servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.materias_primas_mdp IS 'Materias primas y materiales que se integran a la produccion (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.combustibles_lubricantes_energeticos_mdp IS 'Consumo de combustibles, lubricantes y energeticos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.renta_alquiler_bienes_mdp IS 'Renta y alquiler de bienes muebles e inmuebles (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.servicios_profesionales_mdp IS 'Contratacion de servicios profesionales, cientificos y tecnicos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.maquila_servicios_produccion_mdp IS 'Maquila y servicios de produccion de bienes por contrato (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.otros_bienes_servicios_mdp IS 'Consumo de otros bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.fletes_productos_vendidos_mdp IS 'Fletes de productos vendidos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.papeleria_oficina_mdp IS 'Gastos por consumo de papeleria y articulos de oficina (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.energia_electrica_mdp IS 'Gasto por consumo de energia electrica (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.pagos_pers_subcontratado_mdp IS 'Pagos a otra razon social que contrato y proporciono personal (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.honorarios_comisiones_mdp IS 'Gastos por honorarios o comisiones sin sueldo o salario fijo (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.publicidad_mdp IS 'Gastos por publicidad (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.servicios_comunicacion_mdp IS 'Gastos por servicios de comunicacion (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.envases_empaques_mdp IS 'Gastos por consumo de envases y empaques (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.reparaciones_refacciones_mdp IS 'Reparaciones y refacciones para mantenimiento corriente (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.consu_agua_mdp IS 'Consumo de agua (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.ingr_tot_mdp IS 'Total de ingresos por suministro de bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.ingr_reventa_mercancias_mdp IS 'Ingresos por la reventa de mercancias y bienes (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.ingr_servicios_profesionales_mdp IS 'Ingresos por prestacion de servicios profesionales, cientificos y tecnicos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.ingr_venta_productos_mdp IS 'Venta de productos elaborados, generados o extraidos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.ingr_alquiler_bienes_mdp IS 'Ingresos por alquiler de bienes muebles e inmuebles (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.otros_ingr_mdp IS 'Otros ingresos por suministro de bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.otros_componentes_prod_bruta_mdp IS 'Otros componentes de la produccion bruta total (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.ingr_maquila_terceros_mdp IS 'Ingresos por maquilar o transformar materias primas propiedad de terceros (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.valor_productos_elaborados_mdp IS 'Valor de productos elaborados, bienes generados y extraidos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.act_fijos_uso_propio_mdp IS 'Activos fijos producidos para uso propio (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.invent_inic_mdp IS 'Total de inventario inicial (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.invent_final_mdp IS 'Total de inventario final (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.var_exis_mdp IS 'Variacion total de existencias (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.invent_inic_proceso_mdp IS 'Total de inventario inicial de productos en proceso (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.invent_final_proceso_mdp IS 'Total de inventario final de productos en proceso (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.var_invent_proceso_mdp IS 'Variacion de inventarios de productos en proceso (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.invent_inic_reventa_mdp IS 'Total de inventario inicial de mercancias compradas para reventa (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.invent_final_reventa_mdp IS 'Total de inventario final de mercancias compradas para reventa (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.acervo_act_fijos_mdp IS 'Acervo total de activos fijos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.depreciacion_act_fijos_mdp IS 'Depreciacion total de activos fijos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.compra_act_fijos_mdp IS 'Compra y adquisicion total de activos fijos y reformas mayores (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.ventas_act_fijos_mdp IS 'Ventas totales de activos fijos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.acervo_maquinaria_equipo_mdp IS 'Acervo total de maquinaria y equipo de produccion (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.acervo_bienes_inmuebles_mdp IS 'Acervo total de bienes inmuebles (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.acervo_unidades_transporte_mdp IS 'Acervo total de unidades y equipo de transporte (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.acervo_equipo_computo_mdp IS 'Acervo total de equipo de computo y perifericos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.acervo_mobiliario_oficina_mdp IS 'Acervo total de mobiliario, equipo de oficina y otros activos fijos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2019.unidades_economicas IS 'Unidades economicas';

CREATE TABLE IF NOT EXISTS stg_economico_estatal_2019 (
    id                                        SERIAL PRIMARY KEY,
    censo_id                              INTEGER NOT NULL REFERENCES cat_censos(id),
    actividad_economica_id          INTEGER REFERENCES cat_actividades_economicas(id),
    estrato_id                      INTEGER REFERENCES cat_estratos(id),
    cve_ent                                   INTEGER NOT NULL,
    prod_bruta_tot_mdp                                      FLOAT,
    part_bienes_elab_gen_ext_pbt                            FLOAT,
    part_imatmpp                                            FLOAT,
    part_act_fijos_producidos_uso_propio_pb                 FLOAT,
    part_var_exist_prod_proceso_pbt                         FLOAT,
    part_mar_rev_merc_pbt                                   FLOAT,
    part_serv_prof_cient_tec_pbt                            FLOAT,
    part_ingr_abmi_produccion                               FLOAT,
    part_otros_comp_pbt                                     FLOAT,
    consu_intermedio_mdp                                    FLOAT,
    valor_agregado_censal_bruto_mdp                         FLOAT,
    part_ssen_tr                                            FLOAT,
    part_salarios_ppvs_tr                                   FLOAT,
    part_sueldos_pers_acd_tr                                FLOAT,
    pers_dependiente_pers_ocup_tot_porcentaje               FLOAT,
    pnr_perasonal_ocupado_tot                               FLOAT,
    pnr_po_dependiente                                      FLOAT,
    prest_soc_util_rep_tot_rem                              FLOAT,
    part_urt_tr                                             FLOAT,
    part_mt_pers_remu                                       FLOAT,
    part_mt_po_produccion_ventas_servicios                  FLOAT,
    part_mt_po_acd                                          FLOAT,
    prest_soc_tot_rem                                       FLOAT,
    part_prestaciones_sociales_utilidades_sueldos_salarios  FLOAT,
    part_mt_pfotn                                           FLOAT,
    tot_prestaciones_ss                                     FLOAT,
    part_mt_pcpor                                           FLOAT,
    part_mt_phcs                                            FLOAT,
    remuneracion_media_per_ocupada_remu                     FLOAT,
    salario_pers_operativo_anual                            FLOAT,
    sueldo_pers_administrativo_anual                        FLOAT,
    pagos_promedio_per_suministrada                         FLOAT,
    pagos_promedio_pers_comisiones_u_honorarios             FLOAT,
    part_remuneraciones_gcbs                                FLOAT,
    per_no_dep_pers_ocup_tot                                FLOAT,
    indem_liqui_remu_tot                                    FLOAT,
    remuneracion_media_per_remu                             FLOAT,
    horas_dia_trab_prom_pers_remu                           FLOAT,
    horas_dia_trab_prom_pers_no_remu                        FLOAT,
    horas_dia_trab_prom_ppvs                                FLOAT,
    horas_dia_trab_prom_empleados_administrativos_control   FLOAT,
    horas_dia_trab_prom_pers_comisiones_honorarios          FLOAT,
    valor_agregado_censal_bruto_pbt                         FLOAT,
    part_consu_intermedio_pbt                               FLOAT,
    va_promedio_per_ocupada                                 FLOAT,
    pbt_pers_ocupado_tot                                    FLOAT,
    part_mpms_gastos_consu_bienes                           FLOAT,
    part_mcs_gcbs                                           FLOAT,
    inversion_tot_mdp                                       FLOAT,
    part_cae_gcbs                                           FLOAT,
    inversion_ti_tot                                        FLOAT,
    part_gastos_consu_otros_bienes_servicios_gastos_consu   FLOAT,
    inversion_tot_act_fijos                                 FLOAT,
    part_ivm_ti_suministro_bienes                           FLOAT,
    inversion_tot_valor_agregado_censal_bruto               FLOAT,
    part_servi_prof_cient                                   FLOAT,
    part_otros_isbs_ti                                      FLOAT,
    form_brut_cap_mdp                                       FLOAT,
    inversion_tot_pbt                                       FLOAT,
    part_venta_productos_elaborados_generados_o_extraidos_tot FLOAT,
    part_ingr_abmi_tot                                      FLOAT,
    part_imatmpp_2                                          FLOAT,
    part_mep_tot_act_fijos                                  FLOAT,
    part_cif_tot_act_fijos                                  FLOAT,
    part_et_tot_act_fijos                                   FLOAT,
    part_ecp_tot_act_fijos                                  FLOAT,
    margen_bruto_operacion                                  FLOAT,
    ing_princ_por_sum_bienes                                FLOAT,
    gp_gcbs                                                 FLOAT,
    gp_ip                                                   FLOAT,
    part_meo_otros_act_fijos_tot                            FLOAT,
    valor_act_fijos_per_ocupada                             FLOAT,
    maqui_equip_prod_a_prod_tot                             FLOAT,
    acti_fijo_brut_tot                                      FLOAT,
    forma_brut_cap_fijo_acervo_tot                          FLOAT,
    produccion_act_fijos_uso_propio_compras_act_fijos       FLOAT,
    otros_isbs_ti_suministro                                FLOAT,
    gastos_no_derivados_actividad_gcbs                      FLOAT,
    ingr_no_derivados_actividad_isbs                        FLOAT,
    valor_promedio_maquinaria_equipo_per_ocupada_anuales    FLOAT,
    ip_respecto_gp                                          FLOAT,
    porcentaje_ip_ti_actividad_financieros                  FLOAT,
    isbs_per_ocupada                                        FLOAT,
    mar_por_rev_mdp                                         FLOAT,
    part_depreciacion_valor_act_fijos                       FLOAT,
    tasa_rentabilidad_promedio                              FLOAT,
    gastos_tot_mdp                                          FLOAT,
    salario_promedio_diarios_per_operativa                  FLOAT,
    sueldo_promedio_diario_per_administrativa               FLOAT,
    va_tot_act_fijos                                        FLOAT,
    part_muje_pers_ocupado_tot                              FLOAT,
    ingr_tot_general_mdp                                    FLOAT,
    pers_dep_razon_social                                   FLOAT,
    pers_dep_razon_social_h                                 FLOAT,
    pers_dep_razon_social_m                                 FLOAT,
    horas_pers_dep_razon_social_mh                          FLOAT,
    pers_ocupado_tot                                        FLOAT,
    pers_ocupado_tot_h                                      FLOAT,
    pers_ocupado_tot_m                                      FLOAT,
    horas_pers_ocupado_tot_mh                               FLOAT,
    pers_remu                                               FLOAT,
    pers_remu_h                                             FLOAT,
    pers_remu_m                                             FLOAT,
    horas_pers_remu_mh                                      FLOAT,
    pers_no_remu                                            FLOAT,
    pers_no_remu_h                                          FLOAT,
    pers_no_remu_m                                          FLOAT,
    horas_pers_no_remu_mh                                   FLOAT,
    pers_prod_ventas_servicios                              FLOAT,
    pers_prod_ventas_servicios_h                            FLOAT,
    pers_prod_ventas_servicios_m                            FLOAT,
    horas_pers_prod_ventas_servicios_mh                     FLOAT,
    pers_admin_contable_direccion                           FLOAT,
    pers_admin_contable_direccion_h                         FLOAT,
    pers_admin_contable_direccion_m                         FLOAT,
    horas_pers_admin_contable_direccion_mh                  FLOAT,
    pers_no_dep_razon_social                                FLOAT,
    pers_no_dep_razon_social_h                              FLOAT,
    pers_no_dep_razon_social_m                              FLOAT,
    horas_pers_no_dep_razon_social_mh                       FLOAT,
    pers_contratado_otra_razon_social                       FLOAT,
    pers_contratado_otra_razon_social_h                     FLOAT,
    pers_contratado_otra_razon_social_m                     FLOAT,
    horas_pers_contratado_otra_razon_social_mh              FLOAT,
    pers_honorarios                                         FLOAT,
    pers_honorarios_h                                       FLOAT,
    pers_honorarios_m                                       FLOAT,
    horas_pers_honorarios_mh                                FLOAT,
    remuneraciones_tot_mdp                                  FLOAT,
    salarios_pers_prod_ventas_servicios_mdp                 FLOAT,
    sueldos_pers_admin_contable_direccion_mdp               FLOAT,
    contribuciones_seguridad_social_mdp                     FLOAT,
    otras_prestaciones_sociales_mdp                         FLOAT,
    utilidades_repartidas_mdp                               FLOAT,
    indemnizacion_liquidacion_mdp                           FLOAT,
    gastos_consu_tot_mdp                                    FLOAT,
    mercancias_compradas_reventa_mdp                        FLOAT,
    materiales_servicios_mdp                                FLOAT,
    materias_primas_mdp                                     FLOAT,
    combustibles_lubricantes_energeticos_mdp                FLOAT,
    renta_alquiler_bienes_mdp                               FLOAT,
    servicios_profesionales_mdp                             FLOAT,
    maquila_servicios_produccion_mdp                        FLOAT,
    otros_bienes_servicios_mdp                              FLOAT,
    fletes_productos_vendidos_mdp                           FLOAT,
    papeleria_oficina_mdp                                   FLOAT,
    energia_electrica_mdp                                   FLOAT,
    pagos_pers_subcontratado_mdp                            FLOAT,
    honorarios_comisiones_mdp                               FLOAT,
    publicidad_mdp                                          FLOAT,
    servicios_comunicacion_mdp                              FLOAT,
    envases_empaques_mdp                                    FLOAT,
    reparaciones_refacciones_mdp                            FLOAT,
    consu_agua_mdp                                          FLOAT,
    ingr_tot_mdp                                            FLOAT,
    ingr_reventa_mercancias_mdp                             FLOAT,
    ingr_servicios_profesionales_mdp                        FLOAT,
    ingr_venta_productos_mdp                                FLOAT,
    ingr_alquiler_bienes_mdp                                FLOAT,
    otros_ingr_mdp                                          FLOAT,
    otros_componentes_prod_bruta_mdp                        FLOAT,
    ingr_maquila_terceros_mdp                               FLOAT,
    valor_productos_elaborados_mdp                          FLOAT,
    act_fijos_uso_propio_mdp                                FLOAT,
    invent_inic_mdp                                         FLOAT,
    invent_final_mdp                                        FLOAT,
    var_exis_mdp                                            FLOAT,
    invent_inic_proceso_mdp                                 FLOAT,
    invent_final_proceso_mdp                                FLOAT,
    var_invent_proceso_mdp                                  FLOAT,
    invent_inic_reventa_mdp                                 FLOAT,
    invent_final_reventa_mdp                                FLOAT,
    acervo_act_fijos_mdp                                    FLOAT,
    depreciacion_act_fijos_mdp                              FLOAT,
    compra_act_fijos_mdp                                    FLOAT,
    ventas_act_fijos_mdp                                    FLOAT,
    acervo_maquinaria_equipo_mdp                            FLOAT,
    acervo_bienes_inmuebles_mdp                             FLOAT,
    acervo_unidades_transporte_mdp                          FLOAT,
    acervo_equipo_computo_mdp                               FLOAT,
    acervo_mobiliario_oficina_mdp                           FLOAT,
    unidades_economicas                                     FLOAT
);
COMMENT ON COLUMN stg_economico_estatal_2019.censo_id IS 'Referencia al censo economico';
COMMENT ON COLUMN stg_economico_estatal_2019.actividad_economica_id IS 'Referencia a la actividad economica SCIAN';
COMMENT ON COLUMN stg_economico_estatal_2019.estrato_id IS 'Referencia al estrato de personal ocupado';
COMMENT ON COLUMN stg_economico_estatal_2019.cve_ent IS 'Clave de entidad federativa';
COMMENT ON COLUMN stg_economico_estatal_2019.prod_bruta_tot_mdp IS 'Produccion bruta total (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.part_bienes_elab_gen_ext_pbt IS 'Participacion del valor de bienes elaborados, generados o extraidos en la produccion bruta total';
COMMENT ON COLUMN stg_economico_estatal_2019.part_imatmpp IS 'Participacion de ingresos por maquilar o transformar materias primas propiedad de terceros';
COMMENT ON COLUMN stg_economico_estatal_2019.part_act_fijos_producidos_uso_propio_pb IS 'Participacion de activos fijos producidos para uso propio en la produccion bruta';
COMMENT ON COLUMN stg_economico_estatal_2019.part_var_exist_prod_proceso_pbt IS 'Participacion de la variacion de existencias de productos en proceso en la produccion bruta total';
COMMENT ON COLUMN stg_economico_estatal_2019.part_mar_rev_merc_pbt IS 'Participacion del margen por reventa de mercancias en la produccion bruta total';
COMMENT ON COLUMN stg_economico_estatal_2019.part_serv_prof_cient_tec_pbt IS 'Participacion de servicios profesionales, cientificos y tecnicos en la produccion bruta';
COMMENT ON COLUMN stg_economico_estatal_2019.part_ingr_abmi_produccion IS 'Participacion de ingresos por alquiler de bienes muebles e inmuebles en la produccion';
COMMENT ON COLUMN stg_economico_estatal_2019.part_otros_comp_pbt IS 'Participacion de otros componentes de la produccion bruta total';
COMMENT ON COLUMN stg_economico_estatal_2019.consu_intermedio_mdp IS 'Consumo intermedio (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.valor_agregado_censal_bruto_mdp IS 'Valor agregado censal bruto (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.part_ssen_tr IS 'Participacion de salarios y sueldos en el total de remuneraciones';
COMMENT ON COLUMN stg_economico_estatal_2019.part_salarios_ppvs_tr IS 'Participacion de salarios al personal de produccion, ventas y servicios en el total de remuneraciones';
COMMENT ON COLUMN stg_economico_estatal_2019.part_sueldos_pers_acd_tr IS 'Participacion de sueldos al personal administrativo, contable y de direccion en el total de remuneraciones';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_dependiente_pers_ocup_tot_porcentaje IS 'Personal dependiente sobre personal ocupado total (porcentaje)';
COMMENT ON COLUMN stg_economico_estatal_2019.pnr_perasonal_ocupado_tot IS 'Personal no remunerado sobre personal ocupado total';
COMMENT ON COLUMN stg_economico_estatal_2019.pnr_po_dependiente IS 'Personal no remunerado sobre personal ocupado dependiente';
COMMENT ON COLUMN stg_economico_estatal_2019.prest_soc_util_rep_tot_rem IS 'Prestaciones sociales y utilidades repartidas sobre el total de remuneraciones';
COMMENT ON COLUMN stg_economico_estatal_2019.part_urt_tr IS 'Participacion de utilidades repartidas a trabajadores en el total de remuneraciones';
COMMENT ON COLUMN stg_economico_estatal_2019.part_mt_pers_remu IS 'Participacion de mujeres en el total de personal remunerado';
COMMENT ON COLUMN stg_economico_estatal_2019.part_mt_po_produccion_ventas_servicios IS 'Participacion de mujeres en el total de personal de produccion, ventas y servicios';
COMMENT ON COLUMN stg_economico_estatal_2019.part_mt_po_acd IS 'Participacion de mujeres en el total de personal administrativo, contable y de direccion';
COMMENT ON COLUMN stg_economico_estatal_2019.prest_soc_tot_rem IS 'Prestaciones sociales sobre el total de remuneraciones';
COMMENT ON COLUMN stg_economico_estatal_2019.part_prestaciones_sociales_utilidades_sueldos_salarios IS 'Participacion de prestaciones sociales y utilidades sobre sueldos y salarios';
COMMENT ON COLUMN stg_economico_estatal_2019.part_mt_pfotn IS 'Participacion de mujeres en el total de propietarios, familiares y otros trabajadores no remunerados';
COMMENT ON COLUMN stg_economico_estatal_2019.tot_prestaciones_ss IS 'Total de prestaciones sobre salarios y sueldos';
COMMENT ON COLUMN stg_economico_estatal_2019.part_mt_pcpor IS 'Participacion de mujeres en el total de personal contratado y proporcionado por otra razon social';
COMMENT ON COLUMN stg_economico_estatal_2019.part_mt_phcs IS 'Participacion de mujeres en el total de personal por honorarios o comisiones sin sueldo fijo';
COMMENT ON COLUMN stg_economico_estatal_2019.remuneracion_media_per_ocupada_remu IS 'Remuneracion media por persona ocupada remunerada';
COMMENT ON COLUMN stg_economico_estatal_2019.salario_pers_operativo_anual IS 'Salario al personal operativo (anual)';
COMMENT ON COLUMN stg_economico_estatal_2019.sueldo_pers_administrativo_anual IS 'Sueldo al personal administrativo (anual)';
COMMENT ON COLUMN stg_economico_estatal_2019.pagos_promedio_per_suministrada IS 'Pagos promedio por persona suministrada';
COMMENT ON COLUMN stg_economico_estatal_2019.pagos_promedio_pers_comisiones_u_honorarios IS 'Pagos promedio al personal por comisiones u honorarios';
COMMENT ON COLUMN stg_economico_estatal_2019.part_remuneraciones_gcbs IS 'Participacion de remuneraciones en gastos por consumo de bienes y servicios';
COMMENT ON COLUMN stg_economico_estatal_2019.per_no_dep_pers_ocup_tot IS 'Personal no dependiente sobre personal ocupado total';
COMMENT ON COLUMN stg_economico_estatal_2019.indem_liqui_remu_tot IS 'Indemnizaciones y liquidaciones sobre remuneraciones totales';
COMMENT ON COLUMN stg_economico_estatal_2019.remuneracion_media_per_remu IS 'Remuneracion media por persona remunerada';
COMMENT ON COLUMN stg_economico_estatal_2019.horas_dia_trab_prom_pers_remu IS 'Horas diarias trabajadas promedio por personal remunerado';
COMMENT ON COLUMN stg_economico_estatal_2019.horas_dia_trab_prom_pers_no_remu IS 'Horas diarias trabajadas promedio por personal no remunerado';
COMMENT ON COLUMN stg_economico_estatal_2019.horas_dia_trab_prom_ppvs IS 'Horas diarias trabajadas promedio por personal de produccion, ventas y servicios';
COMMENT ON COLUMN stg_economico_estatal_2019.horas_dia_trab_prom_empleados_administrativos_control IS 'Horas diarias trabajadas promedio por empleados administrativos y de control';
COMMENT ON COLUMN stg_economico_estatal_2019.horas_dia_trab_prom_pers_comisiones_honorarios IS 'Horas diarias trabajadas promedio por personal por comisiones u honorarios';
COMMENT ON COLUMN stg_economico_estatal_2019.valor_agregado_censal_bruto_pbt IS 'Valor agregado censal bruto sobre la produccion bruta total';
COMMENT ON COLUMN stg_economico_estatal_2019.part_consu_intermedio_pbt IS 'Participacion del consumo intermedio en la produccion bruta total';
COMMENT ON COLUMN stg_economico_estatal_2019.va_promedio_per_ocupada IS 'Valor agregado promedio por persona ocupada';
COMMENT ON COLUMN stg_economico_estatal_2019.pbt_pers_ocupado_tot IS 'Produccion bruta total sobre personal ocupado total';
COMMENT ON COLUMN stg_economico_estatal_2019.part_mpms_gastos_consu_bienes IS 'Participacion de materias primas, materiales y suministros en gastos por consumo de bienes';
COMMENT ON COLUMN stg_economico_estatal_2019.part_mcs_gcbs IS 'Participacion de maquila y contratacion de servicios en gastos por consumo de bienes y servicios';
COMMENT ON COLUMN stg_economico_estatal_2019.inversion_tot_mdp IS 'Inversion total (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.part_cae_gcbs IS 'Participacion del consumo de agua y energeticos en gastos por consumo de bienes y servicios';
COMMENT ON COLUMN stg_economico_estatal_2019.inversion_ti_tot IS 'Inversion total sobre ingresos totales';
COMMENT ON COLUMN stg_economico_estatal_2019.part_gastos_consu_otros_bienes_servicios_gastos_consu IS 'Participacion de gastos por consumo de otros bienes y servicios en gastos por consumo';
COMMENT ON COLUMN stg_economico_estatal_2019.inversion_tot_act_fijos IS 'Inversion total sobre activos fijos';
COMMENT ON COLUMN stg_economico_estatal_2019.part_ivm_ti_suministro_bienes IS 'Participacion de ingresos por venta de mercancias en el total de ingresos por suministro de bienes';
COMMENT ON COLUMN stg_economico_estatal_2019.inversion_tot_valor_agregado_censal_bruto IS 'Inversion total sobre valor agregado censal bruto';
COMMENT ON COLUMN stg_economico_estatal_2019.part_servi_prof_cient IS 'Participacion de servicios profesionales, cientificos y tecnicos en el total de ingresos';
COMMENT ON COLUMN stg_economico_estatal_2019.part_otros_isbs_ti IS 'Participacion de otros ingresos por suministro de bienes y servicios en el total de ingresos';
COMMENT ON COLUMN stg_economico_estatal_2019.form_brut_cap_mdp IS 'Formacion bruta de capital fijo (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.inversion_tot_pbt IS 'Inversion total sobre la produccion bruta total';
COMMENT ON COLUMN stg_economico_estatal_2019.part_venta_productos_elaborados_generados_o_extraidos_tot IS 'Participacion de la venta de productos elaborados, generados o extraidos en el total';
COMMENT ON COLUMN stg_economico_estatal_2019.part_ingr_abmi_tot IS 'Participacion de ingresos por alquiler de bienes muebles e inmuebles en el total';
COMMENT ON COLUMN stg_economico_estatal_2019.part_imatmpp_2 IS 'Participacion de ingresos por maquilar o transformar materias primas propiedad de terceros (2)';
COMMENT ON COLUMN stg_economico_estatal_2019.part_mep_tot_act_fijos IS 'Participacion de maquinaria y equipo de produccion en el total de activos fijos';
COMMENT ON COLUMN stg_economico_estatal_2019.part_cif_tot_act_fijos IS 'Participacion de construcciones e instalaciones fijas en el total de activos fijos';
COMMENT ON COLUMN stg_economico_estatal_2019.part_et_tot_act_fijos IS 'Participacion del equipo de transporte en el total de activos fijos';
COMMENT ON COLUMN stg_economico_estatal_2019.part_ecp_tot_act_fijos IS 'Participacion del equipo de computo y perifericos en el total de activos fijos';
COMMENT ON COLUMN stg_economico_estatal_2019.margen_bruto_operacion IS 'Margen bruto de operacion';
COMMENT ON COLUMN stg_economico_estatal_2019.ing_princ_por_sum_bienes IS 'Ingreso principal sobre ingresos por suministro de bienes y servicios';
COMMENT ON COLUMN stg_economico_estatal_2019.gp_gcbs IS 'Gasto principal sobre gastos por consumo de bienes y servicios';
COMMENT ON COLUMN stg_economico_estatal_2019.gp_ip IS 'Gasto principal sobre ingreso principal';
COMMENT ON COLUMN stg_economico_estatal_2019.part_meo_otros_act_fijos_tot IS 'Participacion de mobiliario y equipo de oficina y otros activos fijos en el total';
COMMENT ON COLUMN stg_economico_estatal_2019.valor_act_fijos_per_ocupada IS 'Valor de activos fijos por persona ocupada';
COMMENT ON COLUMN stg_economico_estatal_2019.maqui_equip_prod_a_prod_tot IS 'Maquinaria y equipo de produccion sobre la produccion bruta total';
COMMENT ON COLUMN stg_economico_estatal_2019.acti_fijo_brut_tot IS 'Activos fijos sobre la produccion bruta total';
COMMENT ON COLUMN stg_economico_estatal_2019.forma_brut_cap_fijo_acervo_tot IS 'Formacion bruta de capital fijo sobre acervo de capital';
COMMENT ON COLUMN stg_economico_estatal_2019.produccion_act_fijos_uso_propio_compras_act_fijos IS 'Produccion de activos fijos para uso propio sobre compras de activos fijos';
COMMENT ON COLUMN stg_economico_estatal_2019.otros_isbs_ti_suministro IS 'Otros ingresos por suministro de bienes y servicios sobre el total de ingresos por suministro';
COMMENT ON COLUMN stg_economico_estatal_2019.gastos_no_derivados_actividad_gcbs IS 'Gastos no derivados de la actividad sobre gastos por consumo de bienes y servicios';
COMMENT ON COLUMN stg_economico_estatal_2019.ingr_no_derivados_actividad_isbs IS 'Ingresos no derivados de la actividad sobre ingresos por suministro de bienes y servicios';
COMMENT ON COLUMN stg_economico_estatal_2019.valor_promedio_maquinaria_equipo_per_ocupada_anuales IS 'Valor promedio de maquinaria y equipo por persona ocupada (anuales)';
COMMENT ON COLUMN stg_economico_estatal_2019.ip_respecto_gp IS 'Ingreso principal respecto al gasto principal';
COMMENT ON COLUMN stg_economico_estatal_2019.porcentaje_ip_ti_actividad_financieros IS 'Porcentaje del ingreso principal en el total de ingresos por actividades financieras';
COMMENT ON COLUMN stg_economico_estatal_2019.isbs_per_ocupada IS 'Ingresos por suministro de bienes y servicios por persona ocupada';
COMMENT ON COLUMN stg_economico_estatal_2019.mar_por_rev_mdp IS 'Margen por reventa de mercancias (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.part_depreciacion_valor_act_fijos IS 'Participacion de la depreciacion en el valor de activos fijos';
COMMENT ON COLUMN stg_economico_estatal_2019.tasa_rentabilidad_promedio IS 'Tasa de rentabilidad promedio';
COMMENT ON COLUMN stg_economico_estatal_2019.gastos_tot_mdp IS 'Total de gastos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.salario_promedio_diarios_per_operativa IS 'Salario promedio diario por persona operativa';
COMMENT ON COLUMN stg_economico_estatal_2019.sueldo_promedio_diario_per_administrativa IS 'Sueldo promedio diario por persona administrativa';
COMMENT ON COLUMN stg_economico_estatal_2019.va_tot_act_fijos IS 'Valor agregado total sobre activos fijos';
COMMENT ON COLUMN stg_economico_estatal_2019.part_muje_pers_ocupado_tot IS 'Participacion de mujeres en el personal ocupado total';
COMMENT ON COLUMN stg_economico_estatal_2019.ingr_tot_general_mdp IS 'Total de ingresos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_dep_razon_social IS 'Personal dependiente de la razon social total';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_dep_razon_social_h IS 'Personal dependiente de la razon social, hombres';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_dep_razon_social_m IS 'Personal dependiente de la razon social, mujeres';
COMMENT ON COLUMN stg_economico_estatal_2019.horas_pers_dep_razon_social_mh IS 'Horas trabajadas por personal dependiente de la razon social (miles de horas)';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_ocupado_tot IS 'Personal ocupado total';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_ocupado_tot_h IS 'Personal ocupado total, hombres';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_ocupado_tot_m IS 'Personal ocupado total, mujeres';
COMMENT ON COLUMN stg_economico_estatal_2019.horas_pers_ocupado_tot_mh IS 'Horas trabajadas por personal ocupado total (miles de horas)';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_remu IS 'Personal remunerado total';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_remu_h IS 'Personal remunerado, hombres';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_remu_m IS 'Personal remunerado, mujeres';
COMMENT ON COLUMN stg_economico_estatal_2019.horas_pers_remu_mh IS 'Horas trabajadas por personal remunerado (miles de horas)';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_no_remu IS 'Personas propietarias, familiares y otro personal no remunerado total';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_no_remu_h IS 'Personas propietarias, familiares y otro personal no remunerado, hombres';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_no_remu_m IS 'Personas propietarias, familiares y otro personal no remunerado, mujeres';
COMMENT ON COLUMN stg_economico_estatal_2019.horas_pers_no_remu_mh IS 'Horas trabajadas por personal no remunerado (miles de horas)';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_prod_ventas_servicios IS 'Personal de produccion, ventas y servicios total';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_prod_ventas_servicios_h IS 'Personal de produccion, ventas y servicios, hombres';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_prod_ventas_servicios_m IS 'Personal de produccion, ventas y servicios, mujeres';
COMMENT ON COLUMN stg_economico_estatal_2019.horas_pers_prod_ventas_servicios_mh IS 'Horas trabajadas por personal de produccion, ventas y servicios (miles de horas)';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_admin_contable_direccion IS 'Personal administrativo, contable y de direccion total';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_admin_contable_direccion_h IS 'Personal administrativo, contable y de direccion, hombres';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_admin_contable_direccion_m IS 'Personal administrativo, contable y de direccion, mujeres';
COMMENT ON COLUMN stg_economico_estatal_2019.horas_pers_admin_contable_direccion_mh IS 'Horas trabajadas por personal administrativo, contable y de direccion (miles de horas)';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_no_dep_razon_social IS 'Personal no dependiente de la razon social total';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_no_dep_razon_social_h IS 'Personal no dependiente de la razon social, hombres';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_no_dep_razon_social_m IS 'Personal no dependiente de la razon social, mujeres';
COMMENT ON COLUMN stg_economico_estatal_2019.horas_pers_no_dep_razon_social_mh IS 'Horas trabajadas por personal no dependiente de la razon social (miles de horas)';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_contratado_otra_razon_social IS 'Personal contratado y proporcionado por otra razon social total';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_contratado_otra_razon_social_h IS 'Personal contratado y proporcionado por otra razon social, hombres';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_contratado_otra_razon_social_m IS 'Personal contratado y proporcionado por otra razon social, mujeres';
COMMENT ON COLUMN stg_economico_estatal_2019.horas_pers_contratado_otra_razon_social_mh IS 'Horas trabajadas por personal contratado por otra razon social (miles de horas)';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_honorarios IS 'Personal por honorarios o comisiones sin sueldo o salario fijo total';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_honorarios_h IS 'Personal por honorarios o comisiones sin sueldo o salario fijo, hombres';
COMMENT ON COLUMN stg_economico_estatal_2019.pers_honorarios_m IS 'Personal por honorarios o comisiones sin sueldo o salario fijo, mujeres';
COMMENT ON COLUMN stg_economico_estatal_2019.horas_pers_honorarios_mh IS 'Horas trabajadas por personal por honorarios (miles de horas)';
COMMENT ON COLUMN stg_economico_estatal_2019.remuneraciones_tot_mdp IS 'Total de remuneraciones (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.salarios_pers_prod_ventas_servicios_mdp IS 'Total de salarios al personal de produccion, ventas y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.sueldos_pers_admin_contable_direccion_mdp IS 'Total de sueldos al personal administrativo, contable y de direccion (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.contribuciones_seguridad_social_mdp IS 'Contribuciones patronales a regimenes de seguridad social (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.otras_prestaciones_sociales_mdp IS 'Otras prestaciones sociales (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.utilidades_repartidas_mdp IS 'Utilidades repartidas al personal (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.indemnizacion_liquidacion_mdp IS 'Gastos por indemnizacion o liquidacion del personal (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.gastos_consu_tot_mdp IS 'Total de gastos por consumo de bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.mercancias_compradas_reventa_mdp IS 'Mercancias y bienes comprados para la reventa (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.materiales_servicios_mdp IS 'Materiales e insumos consumidos para la prestacion de servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.materias_primas_mdp IS 'Materias primas y materiales que se integran a la produccion (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.combustibles_lubricantes_energeticos_mdp IS 'Consumo de combustibles, lubricantes y energeticos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.renta_alquiler_bienes_mdp IS 'Renta y alquiler de bienes muebles e inmuebles (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.servicios_profesionales_mdp IS 'Contratacion de servicios profesionales, cientificos y tecnicos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.maquila_servicios_produccion_mdp IS 'Maquila y servicios de produccion de bienes por contrato (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.otros_bienes_servicios_mdp IS 'Consumo de otros bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.fletes_productos_vendidos_mdp IS 'Fletes de productos vendidos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.papeleria_oficina_mdp IS 'Gastos por consumo de papeleria y articulos de oficina (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.energia_electrica_mdp IS 'Gasto por consumo de energia electrica (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.pagos_pers_subcontratado_mdp IS 'Pagos a otra razon social que contrato y proporciono personal (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.honorarios_comisiones_mdp IS 'Gastos por honorarios o comisiones sin sueldo o salario fijo (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.publicidad_mdp IS 'Gastos por publicidad (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.servicios_comunicacion_mdp IS 'Gastos por servicios de comunicacion (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.envases_empaques_mdp IS 'Gastos por consumo de envases y empaques (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.reparaciones_refacciones_mdp IS 'Reparaciones y refacciones para mantenimiento corriente (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.consu_agua_mdp IS 'Consumo de agua (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.ingr_tot_mdp IS 'Total de ingresos por suministro de bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.ingr_reventa_mercancias_mdp IS 'Ingresos por la reventa de mercancias y bienes (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.ingr_servicios_profesionales_mdp IS 'Ingresos por prestacion de servicios profesionales, cientificos y tecnicos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.ingr_venta_productos_mdp IS 'Venta de productos elaborados, generados o extraidos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.ingr_alquiler_bienes_mdp IS 'Ingresos por alquiler de bienes muebles e inmuebles (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.otros_ingr_mdp IS 'Otros ingresos por suministro de bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.otros_componentes_prod_bruta_mdp IS 'Otros componentes de la produccion bruta total (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.ingr_maquila_terceros_mdp IS 'Ingresos por maquilar o transformar materias primas propiedad de terceros (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.valor_productos_elaborados_mdp IS 'Valor de productos elaborados, bienes generados y extraidos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.act_fijos_uso_propio_mdp IS 'Activos fijos producidos para uso propio (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.invent_inic_mdp IS 'Total de inventario inicial (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.invent_final_mdp IS 'Total de inventario final (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.var_exis_mdp IS 'Variacion total de existencias (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.invent_inic_proceso_mdp IS 'Total de inventario inicial de productos en proceso (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.invent_final_proceso_mdp IS 'Total de inventario final de productos en proceso (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.var_invent_proceso_mdp IS 'Variacion de inventarios de productos en proceso (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.invent_inic_reventa_mdp IS 'Total de inventario inicial de mercancias compradas para reventa (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.invent_final_reventa_mdp IS 'Total de inventario final de mercancias compradas para reventa (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.acervo_act_fijos_mdp IS 'Acervo total de activos fijos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.depreciacion_act_fijos_mdp IS 'Depreciacion total de activos fijos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.compra_act_fijos_mdp IS 'Compra y adquisicion total de activos fijos y reformas mayores (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.ventas_act_fijos_mdp IS 'Ventas totales de activos fijos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.acervo_maquinaria_equipo_mdp IS 'Acervo total de maquinaria y equipo de produccion (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.acervo_bienes_inmuebles_mdp IS 'Acervo total de bienes inmuebles (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.acervo_unidades_transporte_mdp IS 'Acervo total de unidades y equipo de transporte (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.acervo_equipo_computo_mdp IS 'Acervo total de equipo de computo y perifericos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.acervo_mobiliario_oficina_mdp IS 'Acervo total de mobiliario, equipo de oficina y otros activos fijos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2019.unidades_economicas IS 'Unidades economicas';

CREATE TABLE IF NOT EXISTS stg_economico_municipal_2019 (
    id                                        SERIAL PRIMARY KEY,
    censo_id                              INTEGER NOT NULL REFERENCES cat_censos(id),
    actividad_economica_id          INTEGER REFERENCES cat_actividades_economicas(id),
    estrato_id                      INTEGER REFERENCES cat_estratos(id),
    cve_ent                                   INTEGER NOT NULL,
    cve_mun                                   INTEGER NOT NULL,
    prod_bruta_tot_mdp                                      FLOAT,
    part_bienes_elab_gen_ext_pbt                            FLOAT,
    part_imatmpp                                            FLOAT,
    part_act_fijos_producidos_uso_propio_pb                 FLOAT,
    part_var_exist_prod_proceso_pbt                         FLOAT,
    part_mar_rev_merc_pbt                                   FLOAT,
    part_serv_prof_cient_tec_pbt                            FLOAT,
    part_ingr_abmi_produccion                               FLOAT,
    part_otros_comp_pbt                                     FLOAT,
    consu_intermedio_mdp                                    FLOAT,
    valor_agregado_censal_bruto_mdp                         FLOAT,
    part_ssen_tr                                            FLOAT,
    part_salarios_ppvs_tr                                   FLOAT,
    part_sueldos_pers_acd_tr                                FLOAT,
    pers_dependiente_pers_ocup_tot_porcentaje               FLOAT,
    pnr_perasonal_ocupado_tot                               FLOAT,
    pnr_po_dependiente                                      FLOAT,
    prest_soc_util_rep_tot_rem                              FLOAT,
    part_urt_tr                                             FLOAT,
    part_mt_pers_remu                                       FLOAT,
    part_mt_po_produccion_ventas_servicios                  FLOAT,
    part_mt_po_acd                                          FLOAT,
    prest_soc_tot_rem                                       FLOAT,
    part_prestaciones_sociales_utilidades_sueldos_salarios  FLOAT,
    part_mt_pfotn                                           FLOAT,
    tot_prestaciones_ss                                     FLOAT,
    part_mt_pcpor                                           FLOAT,
    part_mt_phcs                                            FLOAT,
    remuneracion_media_per_ocupada_remu                     FLOAT,
    salario_pers_operativo_anual                            FLOAT,
    sueldo_pers_administrativo_anual                        FLOAT,
    pagos_promedio_per_suministrada                         FLOAT,
    pagos_promedio_pers_comisiones_u_honorarios             FLOAT,
    part_remuneraciones_gcbs                                FLOAT,
    per_no_dep_pers_ocup_tot                                FLOAT,
    indem_liqui_remu_tot                                    FLOAT,
    remuneracion_media_per_remu                             FLOAT,
    horas_dia_trab_prom_pers_remu                           FLOAT,
    horas_dia_trab_prom_pers_no_remu                        FLOAT,
    horas_dia_trab_prom_ppvs                                FLOAT,
    horas_dia_trab_prom_empleados_administrativos_control   FLOAT,
    horas_dia_trab_prom_pers_comisiones_honorarios          FLOAT,
    valor_agregado_censal_bruto_pbt                         FLOAT,
    part_consu_intermedio_pbt                               FLOAT,
    va_promedio_per_ocupada                                 FLOAT,
    pbt_pers_ocupado_tot                                    FLOAT,
    part_mpms_gastos_consu_bienes                           FLOAT,
    part_mcs_gcbs                                           FLOAT,
    inversion_tot_mdp                                       FLOAT,
    part_cae_gcbs                                           FLOAT,
    inversion_ti_tot                                        FLOAT,
    part_gastos_consu_otros_bienes_servicios_gastos_consu   FLOAT,
    inversion_tot_act_fijos                                 FLOAT,
    part_ivm_ti_suministro_bienes                           FLOAT,
    inversion_tot_valor_agregado_censal_bruto               FLOAT,
    part_servi_prof_cient                                   FLOAT,
    part_otros_isbs_ti                                      FLOAT,
    form_brut_cap_mdp                                       FLOAT,
    inversion_tot_pbt                                       FLOAT,
    part_venta_productos_elaborados_generados_o_extraidos_tot FLOAT,
    part_ingr_abmi_tot                                      FLOAT,
    part_imatmpp_2                                          FLOAT,
    part_mep_tot_act_fijos                                  FLOAT,
    part_cif_tot_act_fijos                                  FLOAT,
    part_et_tot_act_fijos                                   FLOAT,
    part_ecp_tot_act_fijos                                  FLOAT,
    margen_bruto_operacion                                  FLOAT,
    ing_princ_por_sum_bienes                                FLOAT,
    gp_gcbs                                                 FLOAT,
    gp_ip                                                   FLOAT,
    part_meo_otros_act_fijos_tot                            FLOAT,
    valor_act_fijos_per_ocupada                             FLOAT,
    maqui_equip_prod_a_prod_tot                             FLOAT,
    acti_fijo_brut_tot                                      FLOAT,
    forma_brut_cap_fijo_acervo_tot                          FLOAT,
    produccion_act_fijos_uso_propio_compras_act_fijos       FLOAT,
    otros_isbs_ti_suministro                                FLOAT,
    gastos_no_derivados_actividad_gcbs                      FLOAT,
    ingr_no_derivados_actividad_isbs                        FLOAT,
    valor_promedio_maquinaria_equipo_per_ocupada_anuales    FLOAT,
    ip_respecto_gp                                          FLOAT,
    porcentaje_ip_ti_actividad_financieros                  FLOAT,
    isbs_per_ocupada                                        FLOAT,
    mar_por_rev_mdp                                         FLOAT,
    part_depreciacion_valor_act_fijos                       FLOAT,
    tasa_rentabilidad_promedio                              FLOAT,
    gastos_tot_mdp                                          FLOAT,
    salario_promedio_diarios_per_operativa                  FLOAT,
    sueldo_promedio_diario_per_administrativa               FLOAT,
    va_tot_act_fijos                                        FLOAT,
    part_muje_pers_ocupado_tot                              FLOAT,
    ingr_tot_general_mdp                                    FLOAT,
    pers_dep_razon_social                                   FLOAT,
    pers_dep_razon_social_h                                 FLOAT,
    pers_dep_razon_social_m                                 FLOAT,
    horas_pers_dep_razon_social_mh                          FLOAT,
    pers_ocupado_tot                                        FLOAT,
    pers_ocupado_tot_h                                      FLOAT,
    pers_ocupado_tot_m                                      FLOAT,
    horas_pers_ocupado_tot_mh                               FLOAT,
    pers_remu                                               FLOAT,
    pers_remu_h                                             FLOAT,
    pers_remu_m                                             FLOAT,
    horas_pers_remu_mh                                      FLOAT,
    pers_no_remu                                            FLOAT,
    pers_no_remu_h                                          FLOAT,
    pers_no_remu_m                                          FLOAT,
    horas_pers_no_remu_mh                                   FLOAT,
    pers_prod_ventas_servicios                              FLOAT,
    pers_prod_ventas_servicios_h                            FLOAT,
    pers_prod_ventas_servicios_m                            FLOAT,
    horas_pers_prod_ventas_servicios_mh                     FLOAT,
    pers_admin_contable_direccion                           FLOAT,
    pers_admin_contable_direccion_h                         FLOAT,
    pers_admin_contable_direccion_m                         FLOAT,
    horas_pers_admin_contable_direccion_mh                  FLOAT,
    pers_no_dep_razon_social                                FLOAT,
    pers_no_dep_razon_social_h                              FLOAT,
    pers_no_dep_razon_social_m                              FLOAT,
    horas_pers_no_dep_razon_social_mh                       FLOAT,
    pers_contratado_otra_razon_social                       FLOAT,
    pers_contratado_otra_razon_social_h                     FLOAT,
    pers_contratado_otra_razon_social_m                     FLOAT,
    horas_pers_contratado_otra_razon_social_mh              FLOAT,
    pers_honorarios                                         FLOAT,
    pers_honorarios_h                                       FLOAT,
    pers_honorarios_m                                       FLOAT,
    horas_pers_honorarios_mh                                FLOAT,
    remuneraciones_tot_mdp                                  FLOAT,
    salarios_pers_prod_ventas_servicios_mdp                 FLOAT,
    sueldos_pers_admin_contable_direccion_mdp               FLOAT,
    contribuciones_seguridad_social_mdp                     FLOAT,
    otras_prestaciones_sociales_mdp                         FLOAT,
    utilidades_repartidas_mdp                               FLOAT,
    indemnizacion_liquidacion_mdp                           FLOAT,
    gastos_consu_tot_mdp                                    FLOAT,
    mercancias_compradas_reventa_mdp                        FLOAT,
    materiales_servicios_mdp                                FLOAT,
    materias_primas_mdp                                     FLOAT,
    combustibles_lubricantes_energeticos_mdp                FLOAT,
    renta_alquiler_bienes_mdp                               FLOAT,
    servicios_profesionales_mdp                             FLOAT,
    maquila_servicios_produccion_mdp                        FLOAT,
    otros_bienes_servicios_mdp                              FLOAT,
    fletes_productos_vendidos_mdp                           FLOAT,
    papeleria_oficina_mdp                                   FLOAT,
    energia_electrica_mdp                                   FLOAT,
    pagos_pers_subcontratado_mdp                            FLOAT,
    honorarios_comisiones_mdp                               FLOAT,
    publicidad_mdp                                          FLOAT,
    servicios_comunicacion_mdp                              FLOAT,
    envases_empaques_mdp                                    FLOAT,
    reparaciones_refacciones_mdp                            FLOAT,
    consu_agua_mdp                                          FLOAT,
    ingr_tot_mdp                                            FLOAT,
    ingr_reventa_mercancias_mdp                             FLOAT,
    ingr_servicios_profesionales_mdp                        FLOAT,
    ingr_venta_productos_mdp                                FLOAT,
    ingr_alquiler_bienes_mdp                                FLOAT,
    otros_ingr_mdp                                          FLOAT,
    otros_componentes_prod_bruta_mdp                        FLOAT,
    ingr_maquila_terceros_mdp                               FLOAT,
    valor_productos_elaborados_mdp                          FLOAT,
    act_fijos_uso_propio_mdp                                FLOAT,
    invent_inic_mdp                                         FLOAT,
    invent_final_mdp                                        FLOAT,
    var_exis_mdp                                            FLOAT,
    invent_inic_proceso_mdp                                 FLOAT,
    invent_final_proceso_mdp                                FLOAT,
    var_invent_proceso_mdp                                  FLOAT,
    invent_inic_reventa_mdp                                 FLOAT,
    invent_final_reventa_mdp                                FLOAT,
    acervo_act_fijos_mdp                                    FLOAT,
    depreciacion_act_fijos_mdp                              FLOAT,
    compra_act_fijos_mdp                                    FLOAT,
    ventas_act_fijos_mdp                                    FLOAT,
    acervo_maquinaria_equipo_mdp                            FLOAT,
    acervo_bienes_inmuebles_mdp                             FLOAT,
    acervo_unidades_transporte_mdp                          FLOAT,
    acervo_equipo_computo_mdp                               FLOAT,
    acervo_mobiliario_oficina_mdp                           FLOAT,
    unidades_economicas                                     FLOAT
);
COMMENT ON COLUMN stg_economico_municipal_2019.censo_id IS 'Referencia al censo economico';
COMMENT ON COLUMN stg_economico_municipal_2019.actividad_economica_id IS 'Referencia a la actividad economica SCIAN';
COMMENT ON COLUMN stg_economico_municipal_2019.estrato_id IS 'Referencia al estrato de personal ocupado';
COMMENT ON COLUMN stg_economico_municipal_2019.cve_ent IS 'Clave de entidad federativa';
COMMENT ON COLUMN stg_economico_municipal_2019.cve_mun IS 'Clave de municipio';
COMMENT ON COLUMN stg_economico_municipal_2019.prod_bruta_tot_mdp IS 'Produccion bruta total (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.part_bienes_elab_gen_ext_pbt IS 'Participacion del valor de bienes elaborados, generados o extraidos en la produccion bruta total';
COMMENT ON COLUMN stg_economico_municipal_2019.part_imatmpp IS 'Participacion de ingresos por maquilar o transformar materias primas propiedad de terceros';
COMMENT ON COLUMN stg_economico_municipal_2019.part_act_fijos_producidos_uso_propio_pb IS 'Participacion de activos fijos producidos para uso propio en la produccion bruta';
COMMENT ON COLUMN stg_economico_municipal_2019.part_var_exist_prod_proceso_pbt IS 'Participacion de la variacion de existencias de productos en proceso en la produccion bruta total';
COMMENT ON COLUMN stg_economico_municipal_2019.part_mar_rev_merc_pbt IS 'Participacion del margen por reventa de mercancias en la produccion bruta total';
COMMENT ON COLUMN stg_economico_municipal_2019.part_serv_prof_cient_tec_pbt IS 'Participacion de servicios profesionales, cientificos y tecnicos en la produccion bruta';
COMMENT ON COLUMN stg_economico_municipal_2019.part_ingr_abmi_produccion IS 'Participacion de ingresos por alquiler de bienes muebles e inmuebles en la produccion';
COMMENT ON COLUMN stg_economico_municipal_2019.part_otros_comp_pbt IS 'Participacion de otros componentes de la produccion bruta total';
COMMENT ON COLUMN stg_economico_municipal_2019.consu_intermedio_mdp IS 'Consumo intermedio (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.valor_agregado_censal_bruto_mdp IS 'Valor agregado censal bruto (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.part_ssen_tr IS 'Participacion de salarios y sueldos en el total de remuneraciones';
COMMENT ON COLUMN stg_economico_municipal_2019.part_salarios_ppvs_tr IS 'Participacion de salarios al personal de produccion, ventas y servicios en el total de remuneraciones';
COMMENT ON COLUMN stg_economico_municipal_2019.part_sueldos_pers_acd_tr IS 'Participacion de sueldos al personal administrativo, contable y de direccion en el total de remuneraciones';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_dependiente_pers_ocup_tot_porcentaje IS 'Personal dependiente sobre personal ocupado total (porcentaje)';
COMMENT ON COLUMN stg_economico_municipal_2019.pnr_perasonal_ocupado_tot IS 'Personal no remunerado sobre personal ocupado total';
COMMENT ON COLUMN stg_economico_municipal_2019.pnr_po_dependiente IS 'Personal no remunerado sobre personal ocupado dependiente';
COMMENT ON COLUMN stg_economico_municipal_2019.prest_soc_util_rep_tot_rem IS 'Prestaciones sociales y utilidades repartidas sobre el total de remuneraciones';
COMMENT ON COLUMN stg_economico_municipal_2019.part_urt_tr IS 'Participacion de utilidades repartidas a trabajadores en el total de remuneraciones';
COMMENT ON COLUMN stg_economico_municipal_2019.part_mt_pers_remu IS 'Participacion de mujeres en el total de personal remunerado';
COMMENT ON COLUMN stg_economico_municipal_2019.part_mt_po_produccion_ventas_servicios IS 'Participacion de mujeres en el total de personal de produccion, ventas y servicios';
COMMENT ON COLUMN stg_economico_municipal_2019.part_mt_po_acd IS 'Participacion de mujeres en el total de personal administrativo, contable y de direccion';
COMMENT ON COLUMN stg_economico_municipal_2019.prest_soc_tot_rem IS 'Prestaciones sociales sobre el total de remuneraciones';
COMMENT ON COLUMN stg_economico_municipal_2019.part_prestaciones_sociales_utilidades_sueldos_salarios IS 'Participacion de prestaciones sociales y utilidades sobre sueldos y salarios';
COMMENT ON COLUMN stg_economico_municipal_2019.part_mt_pfotn IS 'Participacion de mujeres en el total de propietarios, familiares y otros trabajadores no remunerados';
COMMENT ON COLUMN stg_economico_municipal_2019.tot_prestaciones_ss IS 'Total de prestaciones sobre salarios y sueldos';
COMMENT ON COLUMN stg_economico_municipal_2019.part_mt_pcpor IS 'Participacion de mujeres en el total de personal contratado y proporcionado por otra razon social';
COMMENT ON COLUMN stg_economico_municipal_2019.part_mt_phcs IS 'Participacion de mujeres en el total de personal por honorarios o comisiones sin sueldo fijo';
COMMENT ON COLUMN stg_economico_municipal_2019.remuneracion_media_per_ocupada_remu IS 'Remuneracion media por persona ocupada remunerada';
COMMENT ON COLUMN stg_economico_municipal_2019.salario_pers_operativo_anual IS 'Salario al personal operativo (anual)';
COMMENT ON COLUMN stg_economico_municipal_2019.sueldo_pers_administrativo_anual IS 'Sueldo al personal administrativo (anual)';
COMMENT ON COLUMN stg_economico_municipal_2019.pagos_promedio_per_suministrada IS 'Pagos promedio por persona suministrada';
COMMENT ON COLUMN stg_economico_municipal_2019.pagos_promedio_pers_comisiones_u_honorarios IS 'Pagos promedio al personal por comisiones u honorarios';
COMMENT ON COLUMN stg_economico_municipal_2019.part_remuneraciones_gcbs IS 'Participacion de remuneraciones en gastos por consumo de bienes y servicios';
COMMENT ON COLUMN stg_economico_municipal_2019.per_no_dep_pers_ocup_tot IS 'Personal no dependiente sobre personal ocupado total';
COMMENT ON COLUMN stg_economico_municipal_2019.indem_liqui_remu_tot IS 'Indemnizaciones y liquidaciones sobre remuneraciones totales';
COMMENT ON COLUMN stg_economico_municipal_2019.remuneracion_media_per_remu IS 'Remuneracion media por persona remunerada';
COMMENT ON COLUMN stg_economico_municipal_2019.horas_dia_trab_prom_pers_remu IS 'Horas diarias trabajadas promedio por personal remunerado';
COMMENT ON COLUMN stg_economico_municipal_2019.horas_dia_trab_prom_pers_no_remu IS 'Horas diarias trabajadas promedio por personal no remunerado';
COMMENT ON COLUMN stg_economico_municipal_2019.horas_dia_trab_prom_ppvs IS 'Horas diarias trabajadas promedio por personal de produccion, ventas y servicios';
COMMENT ON COLUMN stg_economico_municipal_2019.horas_dia_trab_prom_empleados_administrativos_control IS 'Horas diarias trabajadas promedio por empleados administrativos y de control';
COMMENT ON COLUMN stg_economico_municipal_2019.horas_dia_trab_prom_pers_comisiones_honorarios IS 'Horas diarias trabajadas promedio por personal por comisiones u honorarios';
COMMENT ON COLUMN stg_economico_municipal_2019.valor_agregado_censal_bruto_pbt IS 'Valor agregado censal bruto sobre la produccion bruta total';
COMMENT ON COLUMN stg_economico_municipal_2019.part_consu_intermedio_pbt IS 'Participacion del consumo intermedio en la produccion bruta total';
COMMENT ON COLUMN stg_economico_municipal_2019.va_promedio_per_ocupada IS 'Valor agregado promedio por persona ocupada';
COMMENT ON COLUMN stg_economico_municipal_2019.pbt_pers_ocupado_tot IS 'Produccion bruta total sobre personal ocupado total';
COMMENT ON COLUMN stg_economico_municipal_2019.part_mpms_gastos_consu_bienes IS 'Participacion de materias primas, materiales y suministros en gastos por consumo de bienes';
COMMENT ON COLUMN stg_economico_municipal_2019.part_mcs_gcbs IS 'Participacion de maquila y contratacion de servicios en gastos por consumo de bienes y servicios';
COMMENT ON COLUMN stg_economico_municipal_2019.inversion_tot_mdp IS 'Inversion total (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.part_cae_gcbs IS 'Participacion del consumo de agua y energeticos en gastos por consumo de bienes y servicios';
COMMENT ON COLUMN stg_economico_municipal_2019.inversion_ti_tot IS 'Inversion total sobre ingresos totales';
COMMENT ON COLUMN stg_economico_municipal_2019.part_gastos_consu_otros_bienes_servicios_gastos_consu IS 'Participacion de gastos por consumo de otros bienes y servicios en gastos por consumo';
COMMENT ON COLUMN stg_economico_municipal_2019.inversion_tot_act_fijos IS 'Inversion total sobre activos fijos';
COMMENT ON COLUMN stg_economico_municipal_2019.part_ivm_ti_suministro_bienes IS 'Participacion de ingresos por venta de mercancias en el total de ingresos por suministro de bienes';
COMMENT ON COLUMN stg_economico_municipal_2019.inversion_tot_valor_agregado_censal_bruto IS 'Inversion total sobre valor agregado censal bruto';
COMMENT ON COLUMN stg_economico_municipal_2019.part_servi_prof_cient IS 'Participacion de servicios profesionales, cientificos y tecnicos en el total de ingresos';
COMMENT ON COLUMN stg_economico_municipal_2019.part_otros_isbs_ti IS 'Participacion de otros ingresos por suministro de bienes y servicios en el total de ingresos';
COMMENT ON COLUMN stg_economico_municipal_2019.form_brut_cap_mdp IS 'Formacion bruta de capital fijo (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.inversion_tot_pbt IS 'Inversion total sobre la produccion bruta total';
COMMENT ON COLUMN stg_economico_municipal_2019.part_venta_productos_elaborados_generados_o_extraidos_tot IS 'Participacion de la venta de productos elaborados, generados o extraidos en el total';
COMMENT ON COLUMN stg_economico_municipal_2019.part_ingr_abmi_tot IS 'Participacion de ingresos por alquiler de bienes muebles e inmuebles en el total';
COMMENT ON COLUMN stg_economico_municipal_2019.part_imatmpp_2 IS 'Participacion de ingresos por maquilar o transformar materias primas propiedad de terceros (2)';
COMMENT ON COLUMN stg_economico_municipal_2019.part_mep_tot_act_fijos IS 'Participacion de maquinaria y equipo de produccion en el total de activos fijos';
COMMENT ON COLUMN stg_economico_municipal_2019.part_cif_tot_act_fijos IS 'Participacion de construcciones e instalaciones fijas en el total de activos fijos';
COMMENT ON COLUMN stg_economico_municipal_2019.part_et_tot_act_fijos IS 'Participacion del equipo de transporte en el total de activos fijos';
COMMENT ON COLUMN stg_economico_municipal_2019.part_ecp_tot_act_fijos IS 'Participacion del equipo de computo y perifericos en el total de activos fijos';
COMMENT ON COLUMN stg_economico_municipal_2019.margen_bruto_operacion IS 'Margen bruto de operacion';
COMMENT ON COLUMN stg_economico_municipal_2019.ing_princ_por_sum_bienes IS 'Ingreso principal sobre ingresos por suministro de bienes y servicios';
COMMENT ON COLUMN stg_economico_municipal_2019.gp_gcbs IS 'Gasto principal sobre gastos por consumo de bienes y servicios';
COMMENT ON COLUMN stg_economico_municipal_2019.gp_ip IS 'Gasto principal sobre ingreso principal';
COMMENT ON COLUMN stg_economico_municipal_2019.part_meo_otros_act_fijos_tot IS 'Participacion de mobiliario y equipo de oficina y otros activos fijos en el total';
COMMENT ON COLUMN stg_economico_municipal_2019.valor_act_fijos_per_ocupada IS 'Valor de activos fijos por persona ocupada';
COMMENT ON COLUMN stg_economico_municipal_2019.maqui_equip_prod_a_prod_tot IS 'Maquinaria y equipo de produccion sobre la produccion bruta total';
COMMENT ON COLUMN stg_economico_municipal_2019.acti_fijo_brut_tot IS 'Activos fijos sobre la produccion bruta total';
COMMENT ON COLUMN stg_economico_municipal_2019.forma_brut_cap_fijo_acervo_tot IS 'Formacion bruta de capital fijo sobre acervo de capital';
COMMENT ON COLUMN stg_economico_municipal_2019.produccion_act_fijos_uso_propio_compras_act_fijos IS 'Produccion de activos fijos para uso propio sobre compras de activos fijos';
COMMENT ON COLUMN stg_economico_municipal_2019.otros_isbs_ti_suministro IS 'Otros ingresos por suministro de bienes y servicios sobre el total de ingresos por suministro';
COMMENT ON COLUMN stg_economico_municipal_2019.gastos_no_derivados_actividad_gcbs IS 'Gastos no derivados de la actividad sobre gastos por consumo de bienes y servicios';
COMMENT ON COLUMN stg_economico_municipal_2019.ingr_no_derivados_actividad_isbs IS 'Ingresos no derivados de la actividad sobre ingresos por suministro de bienes y servicios';
COMMENT ON COLUMN stg_economico_municipal_2019.valor_promedio_maquinaria_equipo_per_ocupada_anuales IS 'Valor promedio de maquinaria y equipo por persona ocupada (anuales)';
COMMENT ON COLUMN stg_economico_municipal_2019.ip_respecto_gp IS 'Ingreso principal respecto al gasto principal';
COMMENT ON COLUMN stg_economico_municipal_2019.porcentaje_ip_ti_actividad_financieros IS 'Porcentaje del ingreso principal en el total de ingresos por actividades financieras';
COMMENT ON COLUMN stg_economico_municipal_2019.isbs_per_ocupada IS 'Ingresos por suministro de bienes y servicios por persona ocupada';
COMMENT ON COLUMN stg_economico_municipal_2019.mar_por_rev_mdp IS 'Margen por reventa de mercancias (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.part_depreciacion_valor_act_fijos IS 'Participacion de la depreciacion en el valor de activos fijos';
COMMENT ON COLUMN stg_economico_municipal_2019.tasa_rentabilidad_promedio IS 'Tasa de rentabilidad promedio';
COMMENT ON COLUMN stg_economico_municipal_2019.gastos_tot_mdp IS 'Total de gastos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.salario_promedio_diarios_per_operativa IS 'Salario promedio diario por persona operativa';
COMMENT ON COLUMN stg_economico_municipal_2019.sueldo_promedio_diario_per_administrativa IS 'Sueldo promedio diario por persona administrativa';
COMMENT ON COLUMN stg_economico_municipal_2019.va_tot_act_fijos IS 'Valor agregado total sobre activos fijos';
COMMENT ON COLUMN stg_economico_municipal_2019.part_muje_pers_ocupado_tot IS 'Participacion de mujeres en el personal ocupado total';
COMMENT ON COLUMN stg_economico_municipal_2019.ingr_tot_general_mdp IS 'Total de ingresos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_dep_razon_social IS 'Personal dependiente de la razon social total';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_dep_razon_social_h IS 'Personal dependiente de la razon social, hombres';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_dep_razon_social_m IS 'Personal dependiente de la razon social, mujeres';
COMMENT ON COLUMN stg_economico_municipal_2019.horas_pers_dep_razon_social_mh IS 'Horas trabajadas por personal dependiente de la razon social (miles de horas)';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_ocupado_tot IS 'Personal ocupado total';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_ocupado_tot_h IS 'Personal ocupado total, hombres';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_ocupado_tot_m IS 'Personal ocupado total, mujeres';
COMMENT ON COLUMN stg_economico_municipal_2019.horas_pers_ocupado_tot_mh IS 'Horas trabajadas por personal ocupado total (miles de horas)';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_remu IS 'Personal remunerado total';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_remu_h IS 'Personal remunerado, hombres';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_remu_m IS 'Personal remunerado, mujeres';
COMMENT ON COLUMN stg_economico_municipal_2019.horas_pers_remu_mh IS 'Horas trabajadas por personal remunerado (miles de horas)';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_no_remu IS 'Personas propietarias, familiares y otro personal no remunerado total';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_no_remu_h IS 'Personas propietarias, familiares y otro personal no remunerado, hombres';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_no_remu_m IS 'Personas propietarias, familiares y otro personal no remunerado, mujeres';
COMMENT ON COLUMN stg_economico_municipal_2019.horas_pers_no_remu_mh IS 'Horas trabajadas por personal no remunerado (miles de horas)';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_prod_ventas_servicios IS 'Personal de produccion, ventas y servicios total';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_prod_ventas_servicios_h IS 'Personal de produccion, ventas y servicios, hombres';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_prod_ventas_servicios_m IS 'Personal de produccion, ventas y servicios, mujeres';
COMMENT ON COLUMN stg_economico_municipal_2019.horas_pers_prod_ventas_servicios_mh IS 'Horas trabajadas por personal de produccion, ventas y servicios (miles de horas)';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_admin_contable_direccion IS 'Personal administrativo, contable y de direccion total';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_admin_contable_direccion_h IS 'Personal administrativo, contable y de direccion, hombres';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_admin_contable_direccion_m IS 'Personal administrativo, contable y de direccion, mujeres';
COMMENT ON COLUMN stg_economico_municipal_2019.horas_pers_admin_contable_direccion_mh IS 'Horas trabajadas por personal administrativo, contable y de direccion (miles de horas)';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_no_dep_razon_social IS 'Personal no dependiente de la razon social total';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_no_dep_razon_social_h IS 'Personal no dependiente de la razon social, hombres';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_no_dep_razon_social_m IS 'Personal no dependiente de la razon social, mujeres';
COMMENT ON COLUMN stg_economico_municipal_2019.horas_pers_no_dep_razon_social_mh IS 'Horas trabajadas por personal no dependiente de la razon social (miles de horas)';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_contratado_otra_razon_social IS 'Personal contratado y proporcionado por otra razon social total';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_contratado_otra_razon_social_h IS 'Personal contratado y proporcionado por otra razon social, hombres';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_contratado_otra_razon_social_m IS 'Personal contratado y proporcionado por otra razon social, mujeres';
COMMENT ON COLUMN stg_economico_municipal_2019.horas_pers_contratado_otra_razon_social_mh IS 'Horas trabajadas por personal contratado por otra razon social (miles de horas)';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_honorarios IS 'Personal por honorarios o comisiones sin sueldo o salario fijo total';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_honorarios_h IS 'Personal por honorarios o comisiones sin sueldo o salario fijo, hombres';
COMMENT ON COLUMN stg_economico_municipal_2019.pers_honorarios_m IS 'Personal por honorarios o comisiones sin sueldo o salario fijo, mujeres';
COMMENT ON COLUMN stg_economico_municipal_2019.horas_pers_honorarios_mh IS 'Horas trabajadas por personal por honorarios (miles de horas)';
COMMENT ON COLUMN stg_economico_municipal_2019.remuneraciones_tot_mdp IS 'Total de remuneraciones (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.salarios_pers_prod_ventas_servicios_mdp IS 'Total de salarios al personal de produccion, ventas y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.sueldos_pers_admin_contable_direccion_mdp IS 'Total de sueldos al personal administrativo, contable y de direccion (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.contribuciones_seguridad_social_mdp IS 'Contribuciones patronales a regimenes de seguridad social (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.otras_prestaciones_sociales_mdp IS 'Otras prestaciones sociales (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.utilidades_repartidas_mdp IS 'Utilidades repartidas al personal (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.indemnizacion_liquidacion_mdp IS 'Gastos por indemnizacion o liquidacion del personal (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.gastos_consu_tot_mdp IS 'Total de gastos por consumo de bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.mercancias_compradas_reventa_mdp IS 'Mercancias y bienes comprados para la reventa (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.materiales_servicios_mdp IS 'Materiales e insumos consumidos para la prestacion de servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.materias_primas_mdp IS 'Materias primas y materiales que se integran a la produccion (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.combustibles_lubricantes_energeticos_mdp IS 'Consumo de combustibles, lubricantes y energeticos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.renta_alquiler_bienes_mdp IS 'Renta y alquiler de bienes muebles e inmuebles (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.servicios_profesionales_mdp IS 'Contratacion de servicios profesionales, cientificos y tecnicos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.maquila_servicios_produccion_mdp IS 'Maquila y servicios de produccion de bienes por contrato (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.otros_bienes_servicios_mdp IS 'Consumo de otros bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.fletes_productos_vendidos_mdp IS 'Fletes de productos vendidos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.papeleria_oficina_mdp IS 'Gastos por consumo de papeleria y articulos de oficina (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.energia_electrica_mdp IS 'Gasto por consumo de energia electrica (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.pagos_pers_subcontratado_mdp IS 'Pagos a otra razon social que contrato y proporciono personal (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.honorarios_comisiones_mdp IS 'Gastos por honorarios o comisiones sin sueldo o salario fijo (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.publicidad_mdp IS 'Gastos por publicidad (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.servicios_comunicacion_mdp IS 'Gastos por servicios de comunicacion (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.envases_empaques_mdp IS 'Gastos por consumo de envases y empaques (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.reparaciones_refacciones_mdp IS 'Reparaciones y refacciones para mantenimiento corriente (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.consu_agua_mdp IS 'Consumo de agua (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.ingr_tot_mdp IS 'Total de ingresos por suministro de bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.ingr_reventa_mercancias_mdp IS 'Ingresos por la reventa de mercancias y bienes (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.ingr_servicios_profesionales_mdp IS 'Ingresos por prestacion de servicios profesionales, cientificos y tecnicos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.ingr_venta_productos_mdp IS 'Venta de productos elaborados, generados o extraidos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.ingr_alquiler_bienes_mdp IS 'Ingresos por alquiler de bienes muebles e inmuebles (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.otros_ingr_mdp IS 'Otros ingresos por suministro de bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.otros_componentes_prod_bruta_mdp IS 'Otros componentes de la produccion bruta total (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.ingr_maquila_terceros_mdp IS 'Ingresos por maquilar o transformar materias primas propiedad de terceros (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.valor_productos_elaborados_mdp IS 'Valor de productos elaborados, bienes generados y extraidos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.act_fijos_uso_propio_mdp IS 'Activos fijos producidos para uso propio (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.invent_inic_mdp IS 'Total de inventario inicial (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.invent_final_mdp IS 'Total de inventario final (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.var_exis_mdp IS 'Variacion total de existencias (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.invent_inic_proceso_mdp IS 'Total de inventario inicial de productos en proceso (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.invent_final_proceso_mdp IS 'Total de inventario final de productos en proceso (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.var_invent_proceso_mdp IS 'Variacion de inventarios de productos en proceso (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.invent_inic_reventa_mdp IS 'Total de inventario inicial de mercancias compradas para reventa (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.invent_final_reventa_mdp IS 'Total de inventario final de mercancias compradas para reventa (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.acervo_act_fijos_mdp IS 'Acervo total de activos fijos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.depreciacion_act_fijos_mdp IS 'Depreciacion total de activos fijos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.compra_act_fijos_mdp IS 'Compra y adquisicion total de activos fijos y reformas mayores (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.ventas_act_fijos_mdp IS 'Ventas totales de activos fijos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.acervo_maquinaria_equipo_mdp IS 'Acervo total de maquinaria y equipo de produccion (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.acervo_bienes_inmuebles_mdp IS 'Acervo total de bienes inmuebles (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.acervo_unidades_transporte_mdp IS 'Acervo total de unidades y equipo de transporte (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.acervo_equipo_computo_mdp IS 'Acervo total de equipo de computo y perifericos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.acervo_mobiliario_oficina_mdp IS 'Acervo total de mobiliario, equipo de oficina y otros activos fijos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2019.unidades_economicas IS 'Unidades economicas';

CREATE TABLE IF NOT EXISTS stg_economico_nacional_2024 (
    id                                        SERIAL PRIMARY KEY,
    censo_id                              INTEGER NOT NULL REFERENCES cat_censos(id),
    actividad_economica_id          INTEGER REFERENCES cat_actividades_economicas(id),
    estrato_id                      INTEGER REFERENCES cat_estratos(id),
    sector                                                  TEXT,
    subsector                                               TEXT,
    rama                                                    TEXT,
    subrama                                                 TEXT,
    clase                                                   TEXT,
    unidades_economicas                                     FLOAT,
    pers_ocupado_tot                                        FLOAT,
    pers_ocupado_tot_h                                      FLOAT,
    pers_ocupado_tot_m                                      FLOAT,
    horas_pers_ocupado_tot_mh                               FLOAT,
    pers_dep_razon_social                                   FLOAT,
    pers_dep_razon_social_h                                 FLOAT,
    pers_dep_razon_social_m                                 FLOAT,
    horas_pers_dep_razon_social_mh                          FLOAT,
    pers_remu                                               FLOAT,
    pers_remu_h                                             FLOAT,
    pers_remu_m                                             FLOAT,
    horas_pers_remu_mh                                      FLOAT,
    pers_no_remu                                            FLOAT,
    pers_no_remu_h                                          FLOAT,
    pers_no_remu_m                                          FLOAT,
    horas_pers_no_remu_mh                                   FLOAT,
    pers_prod_ventas_servicios                              FLOAT,
    pers_prod_ventas_servicios_h                            FLOAT,
    pers_prod_ventas_servicios_m                            FLOAT,
    horas_pers_prod_ventas_servicios_mh                     FLOAT,
    pers_admin_contable_direccion                           FLOAT,
    pers_admin_contable_direccion_h                         FLOAT,
    pers_admin_contable_direccion_m                         FLOAT,
    horas_pers_admin_contable_direccion_mh                  FLOAT,
    pers_no_dep_razon_social                                FLOAT,
    pers_no_dep_razon_social_h                              FLOAT,
    pers_no_dep_razon_social_m                              FLOAT,
    horas_pers_no_dep_razon_social_mh                       FLOAT,
    pers_contratado_otra_razon_social                       FLOAT,
    pers_contratado_otra_razon_social_h                     FLOAT,
    pers_contratado_otra_razon_social_m                     FLOAT,
    horas_pers_contratado_otra_razon_social_mh              FLOAT,
    pers_honorarios                                         FLOAT,
    pers_honorarios_h                                       FLOAT,
    pers_honorarios_m                                       FLOAT,
    horas_pers_honorarios_mh                                FLOAT,
    remuneraciones_tot_mdp                                  FLOAT,
    salarios_pers_prod_ventas_servicios_mdp                 FLOAT,
    sueldos_pers_admin_contable_direccion_mdp               FLOAT,
    contribuciones_seguridad_social_mdp                     FLOAT,
    otras_prestaciones_sociales_mdp                         FLOAT,
    utilidades_repartidas_mdp                               FLOAT,
    indemnizacion_liquidacion_mdp                           FLOAT,
    gastos_consu_tot_mdp                                    FLOAT,
    mercancias_compradas_reventa_mdp                        FLOAT,
    materiales_servicios_mdp                                FLOAT,
    materias_primas_mdp                                     FLOAT,
    combustibles_lubricantes_energeticos_mdp                FLOAT,
    renta_alquiler_bienes_mdp                               FLOAT,
    servicios_profesionales_mdp                             FLOAT,
    maquila_servicios_produccion_mdp                        FLOAT,
    otros_bienes_servicios_mdp                              FLOAT,
    fletes_productos_vendidos_mdp                           FLOAT,
    papeleria_oficina_mdp                                   FLOAT,
    energia_electrica_mdp                                   FLOAT,
    pagos_pers_subcontratado_mdp                            FLOAT,
    honorarios_comisiones_mdp                               FLOAT,
    publicidad_mdp                                          FLOAT,
    servicios_comunicacion_mdp                              FLOAT,
    envases_empaques_mdp                                    FLOAT,
    reparaciones_refacciones_mdp                            FLOAT,
    consu_agua_mdp                                          FLOAT,
    ingr_tot_mdp                                            FLOAT,
    ingr_reventa_mercancias_mdp                             FLOAT,
    ingr_servicios_profesionales_mdp                        FLOAT,
    ingr_venta_productos_mdp                                FLOAT,
    ingr_alquiler_bienes_mdp                                FLOAT,
    otros_ingr_mdp                                          FLOAT,
    otros_componentes_prod_bruta_mdp                        FLOAT,
    ingr_maquila_terceros_mdp                               FLOAT,
    prod_bruta_tot_mdp                                      FLOAT,
    consu_intermedio_mdp                                    FLOAT,
    valor_agregado_censal_bruto_mdp                         FLOAT,
    inversion_tot_mdp                                       FLOAT,
    form_brut_cap_mdp                                       FLOAT,
    mar_por_rev_mdp                                         FLOAT,
    gastos_tot_mdp                                          FLOAT,
    ingr_tot_general_mdp                                    FLOAT,
    valor_productos_elaborados_mdp                          FLOAT,
    act_fijos_uso_propio_mdp                                FLOAT,
    invent_inic_mdp                                         FLOAT,
    invent_final_mdp                                        FLOAT,
    var_exis_mdp                                            FLOAT,
    invent_inic_proceso_mdp                                 FLOAT,
    invent_final_proceso_mdp                                FLOAT,
    var_invent_proceso_mdp                                  FLOAT,
    invent_inic_reventa_mdp                                 FLOAT,
    invent_final_reventa_mdp                                FLOAT,
    acervo_act_fijos_mdp                                    FLOAT,
    depreciacion_act_fijos_mdp                              FLOAT,
    compra_act_fijos_mdp                                    FLOAT,
    ventas_act_fijos_mdp                                    FLOAT,
    acervo_maquinaria_equipo_mdp                            FLOAT,
    acervo_bienes_inmuebles_mdp                             FLOAT,
    acervo_unidades_transporte_mdp                          FLOAT,
    acervo_equipo_computo_mdp                               FLOAT,
    acervo_mobiliario_oficina_mdp                           FLOAT
);
COMMENT ON COLUMN stg_economico_nacional_2024.censo_id IS 'Referencia al censo economico';
COMMENT ON COLUMN stg_economico_nacional_2024.actividad_economica_id IS 'Referencia a la actividad economica SCIAN';
COMMENT ON COLUMN stg_economico_nacional_2024.estrato_id IS 'Referencia al estrato de personal ocupado';
COMMENT ON COLUMN stg_economico_nacional_2024.sector IS 'Sector de actividad economica SCIAN (solo 2024)';
COMMENT ON COLUMN stg_economico_nacional_2024.subsector IS 'Subsector de actividad economica SCIAN (solo 2024)';
COMMENT ON COLUMN stg_economico_nacional_2024.rama IS 'Rama de actividad economica SCIAN (solo 2024)';
COMMENT ON COLUMN stg_economico_nacional_2024.subrama IS 'Subrama de actividad economica SCIAN (solo 2024)';
COMMENT ON COLUMN stg_economico_nacional_2024.clase IS 'Clase de actividad economica SCIAN (solo 2024)';
COMMENT ON COLUMN stg_economico_nacional_2024.unidades_economicas IS 'Unidades economicas';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_ocupado_tot IS 'Personal ocupado total';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_ocupado_tot_h IS 'Personal ocupado total, hombres';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_ocupado_tot_m IS 'Personal ocupado total, mujeres';
COMMENT ON COLUMN stg_economico_nacional_2024.horas_pers_ocupado_tot_mh IS 'Horas trabajadas por personal ocupado total (miles de horas)';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_dep_razon_social IS 'Personal dependiente de la razon social total';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_dep_razon_social_h IS 'Personal dependiente de la razon social, hombres';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_dep_razon_social_m IS 'Personal dependiente de la razon social, mujeres';
COMMENT ON COLUMN stg_economico_nacional_2024.horas_pers_dep_razon_social_mh IS 'Horas trabajadas por personal dependiente de la razon social (miles de horas)';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_remu IS 'Personal remunerado total';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_remu_h IS 'Personal remunerado, hombres';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_remu_m IS 'Personal remunerado, mujeres';
COMMENT ON COLUMN stg_economico_nacional_2024.horas_pers_remu_mh IS 'Horas trabajadas por personal remunerado (miles de horas)';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_no_remu IS 'Personas propietarias, familiares y otro personal no remunerado total';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_no_remu_h IS 'Personas propietarias, familiares y otro personal no remunerado, hombres';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_no_remu_m IS 'Personas propietarias, familiares y otro personal no remunerado, mujeres';
COMMENT ON COLUMN stg_economico_nacional_2024.horas_pers_no_remu_mh IS 'Horas trabajadas por personal no remunerado (miles de horas)';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_prod_ventas_servicios IS 'Personal de produccion, ventas y servicios total';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_prod_ventas_servicios_h IS 'Personal de produccion, ventas y servicios, hombres';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_prod_ventas_servicios_m IS 'Personal de produccion, ventas y servicios, mujeres';
COMMENT ON COLUMN stg_economico_nacional_2024.horas_pers_prod_ventas_servicios_mh IS 'Horas trabajadas por personal de produccion, ventas y servicios (miles de horas)';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_admin_contable_direccion IS 'Personal administrativo, contable y de direccion total';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_admin_contable_direccion_h IS 'Personal administrativo, contable y de direccion, hombres';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_admin_contable_direccion_m IS 'Personal administrativo, contable y de direccion, mujeres';
COMMENT ON COLUMN stg_economico_nacional_2024.horas_pers_admin_contable_direccion_mh IS 'Horas trabajadas por personal administrativo, contable y de direccion (miles de horas)';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_no_dep_razon_social IS 'Personal no dependiente de la razon social total';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_no_dep_razon_social_h IS 'Personal no dependiente de la razon social, hombres';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_no_dep_razon_social_m IS 'Personal no dependiente de la razon social, mujeres';
COMMENT ON COLUMN stg_economico_nacional_2024.horas_pers_no_dep_razon_social_mh IS 'Horas trabajadas por personal no dependiente de la razon social (miles de horas)';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_contratado_otra_razon_social IS 'Personal contratado y proporcionado por otra razon social total';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_contratado_otra_razon_social_h IS 'Personal contratado y proporcionado por otra razon social, hombres';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_contratado_otra_razon_social_m IS 'Personal contratado y proporcionado por otra razon social, mujeres';
COMMENT ON COLUMN stg_economico_nacional_2024.horas_pers_contratado_otra_razon_social_mh IS 'Horas trabajadas por personal contratado por otra razon social (miles de horas)';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_honorarios IS 'Personal por honorarios o comisiones sin sueldo o salario fijo total';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_honorarios_h IS 'Personal por honorarios o comisiones sin sueldo o salario fijo, hombres';
COMMENT ON COLUMN stg_economico_nacional_2024.pers_honorarios_m IS 'Personal por honorarios o comisiones sin sueldo o salario fijo, mujeres';
COMMENT ON COLUMN stg_economico_nacional_2024.horas_pers_honorarios_mh IS 'Horas trabajadas por personal por honorarios (miles de horas)';
COMMENT ON COLUMN stg_economico_nacional_2024.remuneraciones_tot_mdp IS 'Total de remuneraciones (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.salarios_pers_prod_ventas_servicios_mdp IS 'Total de salarios al personal de produccion, ventas y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.sueldos_pers_admin_contable_direccion_mdp IS 'Total de sueldos al personal administrativo, contable y de direccion (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.contribuciones_seguridad_social_mdp IS 'Contribuciones patronales a regimenes de seguridad social (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.otras_prestaciones_sociales_mdp IS 'Otras prestaciones sociales (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.utilidades_repartidas_mdp IS 'Utilidades repartidas al personal (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.indemnizacion_liquidacion_mdp IS 'Gastos por indemnizacion o liquidacion del personal (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.gastos_consu_tot_mdp IS 'Total de gastos por consumo de bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.mercancias_compradas_reventa_mdp IS 'Mercancias y bienes comprados para la reventa (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.materiales_servicios_mdp IS 'Materiales e insumos consumidos para la prestacion de servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.materias_primas_mdp IS 'Materias primas y materiales que se integran a la produccion (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.combustibles_lubricantes_energeticos_mdp IS 'Consumo de combustibles, lubricantes y energeticos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.renta_alquiler_bienes_mdp IS 'Renta y alquiler de bienes muebles e inmuebles (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.servicios_profesionales_mdp IS 'Contratacion de servicios profesionales, cientificos y tecnicos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.maquila_servicios_produccion_mdp IS 'Maquila y servicios de produccion de bienes por contrato (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.otros_bienes_servicios_mdp IS 'Consumo de otros bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.fletes_productos_vendidos_mdp IS 'Fletes de productos vendidos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.papeleria_oficina_mdp IS 'Gastos por consumo de papeleria y articulos de oficina (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.energia_electrica_mdp IS 'Gasto por consumo de energia electrica (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.pagos_pers_subcontratado_mdp IS 'Pagos a otra razon social que contrato y proporciono personal (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.honorarios_comisiones_mdp IS 'Gastos por honorarios o comisiones sin sueldo o salario fijo (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.publicidad_mdp IS 'Gastos por publicidad (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.servicios_comunicacion_mdp IS 'Gastos por servicios de comunicacion (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.envases_empaques_mdp IS 'Gastos por consumo de envases y empaques (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.reparaciones_refacciones_mdp IS 'Reparaciones y refacciones para mantenimiento corriente (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.consu_agua_mdp IS 'Consumo de agua (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.ingr_tot_mdp IS 'Total de ingresos por suministro de bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.ingr_reventa_mercancias_mdp IS 'Ingresos por la reventa de mercancias y bienes (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.ingr_servicios_profesionales_mdp IS 'Ingresos por prestacion de servicios profesionales, cientificos y tecnicos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.ingr_venta_productos_mdp IS 'Venta de productos elaborados, generados o extraidos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.ingr_alquiler_bienes_mdp IS 'Ingresos por alquiler de bienes muebles e inmuebles (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.otros_ingr_mdp IS 'Otros ingresos por suministro de bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.otros_componentes_prod_bruta_mdp IS 'Otros componentes de la produccion bruta total (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.ingr_maquila_terceros_mdp IS 'Ingresos por maquilar o transformar materias primas propiedad de terceros (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.prod_bruta_tot_mdp IS 'Produccion bruta total (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.consu_intermedio_mdp IS 'Consumo intermedio (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.valor_agregado_censal_bruto_mdp IS 'Valor agregado censal bruto (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.inversion_tot_mdp IS 'Inversion total (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.form_brut_cap_mdp IS 'Formacion bruta de capital fijo (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.mar_por_rev_mdp IS 'Margen por reventa de mercancias (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.gastos_tot_mdp IS 'Total de gastos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.ingr_tot_general_mdp IS 'Total de ingresos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.valor_productos_elaborados_mdp IS 'Valor de productos elaborados, bienes generados y extraidos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.act_fijos_uso_propio_mdp IS 'Activos fijos producidos para uso propio (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.invent_inic_mdp IS 'Total de inventario inicial (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.invent_final_mdp IS 'Total de inventario final (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.var_exis_mdp IS 'Variacion total de existencias (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.invent_inic_proceso_mdp IS 'Total de inventario inicial de productos en proceso (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.invent_final_proceso_mdp IS 'Total de inventario final de productos en proceso (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.var_invent_proceso_mdp IS 'Variacion de inventarios de productos en proceso (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.invent_inic_reventa_mdp IS 'Total de inventario inicial de mercancias compradas para reventa (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.invent_final_reventa_mdp IS 'Total de inventario final de mercancias compradas para reventa (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.acervo_act_fijos_mdp IS 'Acervo total de activos fijos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.depreciacion_act_fijos_mdp IS 'Depreciacion total de activos fijos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.compra_act_fijos_mdp IS 'Compra y adquisicion total de activos fijos y reformas mayores (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.ventas_act_fijos_mdp IS 'Ventas totales de activos fijos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.acervo_maquinaria_equipo_mdp IS 'Acervo total de maquinaria y equipo de produccion (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.acervo_bienes_inmuebles_mdp IS 'Acervo total de bienes inmuebles (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.acervo_unidades_transporte_mdp IS 'Acervo total de unidades y equipo de transporte (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.acervo_equipo_computo_mdp IS 'Acervo total de equipo de computo y perifericos (millones de pesos)';
COMMENT ON COLUMN stg_economico_nacional_2024.acervo_mobiliario_oficina_mdp IS 'Acervo total de mobiliario, equipo de oficina y otros activos fijos (millones de pesos)';

CREATE TABLE IF NOT EXISTS stg_economico_estatal_2024 (
    id                                        SERIAL PRIMARY KEY,
    censo_id                              INTEGER NOT NULL REFERENCES cat_censos(id),
    actividad_economica_id          INTEGER REFERENCES cat_actividades_economicas(id),
    estrato_id                      INTEGER REFERENCES cat_estratos(id),
    cve_ent                                   INTEGER NOT NULL,
    sector                                                  TEXT,
    subsector                                               TEXT,
    rama                                                    TEXT,
    subrama                                                 TEXT,
    clase                                                   TEXT,
    unidades_economicas                                     FLOAT,
    pers_ocupado_tot                                        FLOAT,
    pers_ocupado_tot_h                                      FLOAT,
    pers_ocupado_tot_m                                      FLOAT,
    horas_pers_ocupado_tot_mh                               FLOAT,
    pers_dep_razon_social                                   FLOAT,
    pers_dep_razon_social_h                                 FLOAT,
    pers_dep_razon_social_m                                 FLOAT,
    horas_pers_dep_razon_social_mh                          FLOAT,
    pers_remu                                               FLOAT,
    pers_remu_h                                             FLOAT,
    pers_remu_m                                             FLOAT,
    horas_pers_remu_mh                                      FLOAT,
    pers_no_remu                                            FLOAT,
    pers_no_remu_h                                          FLOAT,
    pers_no_remu_m                                          FLOAT,
    horas_pers_no_remu_mh                                   FLOAT,
    pers_prod_ventas_servicios                              FLOAT,
    pers_prod_ventas_servicios_h                            FLOAT,
    pers_prod_ventas_servicios_m                            FLOAT,
    horas_pers_prod_ventas_servicios_mh                     FLOAT,
    pers_admin_contable_direccion                           FLOAT,
    pers_admin_contable_direccion_h                         FLOAT,
    pers_admin_contable_direccion_m                         FLOAT,
    horas_pers_admin_contable_direccion_mh                  FLOAT,
    pers_no_dep_razon_social                                FLOAT,
    pers_no_dep_razon_social_h                              FLOAT,
    pers_no_dep_razon_social_m                              FLOAT,
    horas_pers_no_dep_razon_social_mh                       FLOAT,
    pers_contratado_otra_razon_social                       FLOAT,
    pers_contratado_otra_razon_social_h                     FLOAT,
    pers_contratado_otra_razon_social_m                     FLOAT,
    horas_pers_contratado_otra_razon_social_mh              FLOAT,
    pers_honorarios                                         FLOAT,
    pers_honorarios_h                                       FLOAT,
    pers_honorarios_m                                       FLOAT,
    horas_pers_honorarios_mh                                FLOAT,
    remuneraciones_tot_mdp                                  FLOAT,
    salarios_pers_prod_ventas_servicios_mdp                 FLOAT,
    sueldos_pers_admin_contable_direccion_mdp               FLOAT,
    contribuciones_seguridad_social_mdp                     FLOAT,
    otras_prestaciones_sociales_mdp                         FLOAT,
    utilidades_repartidas_mdp                               FLOAT,
    indemnizacion_liquidacion_mdp                           FLOAT,
    gastos_consu_tot_mdp                                    FLOAT,
    mercancias_compradas_reventa_mdp                        FLOAT,
    materiales_servicios_mdp                                FLOAT,
    materias_primas_mdp                                     FLOAT,
    combustibles_lubricantes_energeticos_mdp                FLOAT,
    renta_alquiler_bienes_mdp                               FLOAT,
    servicios_profesionales_mdp                             FLOAT,
    maquila_servicios_produccion_mdp                        FLOAT,
    otros_bienes_servicios_mdp                              FLOAT,
    fletes_productos_vendidos_mdp                           FLOAT,
    papeleria_oficina_mdp                                   FLOAT,
    energia_electrica_mdp                                   FLOAT,
    pagos_pers_subcontratado_mdp                            FLOAT,
    honorarios_comisiones_mdp                               FLOAT,
    publicidad_mdp                                          FLOAT,
    servicios_comunicacion_mdp                              FLOAT,
    envases_empaques_mdp                                    FLOAT,
    reparaciones_refacciones_mdp                            FLOAT,
    consu_agua_mdp                                          FLOAT,
    ingr_tot_mdp                                            FLOAT,
    ingr_reventa_mercancias_mdp                             FLOAT,
    ingr_servicios_profesionales_mdp                        FLOAT,
    ingr_venta_productos_mdp                                FLOAT,
    ingr_alquiler_bienes_mdp                                FLOAT,
    otros_ingr_mdp                                          FLOAT,
    otros_componentes_prod_bruta_mdp                        FLOAT,
    ingr_maquila_terceros_mdp                               FLOAT,
    prod_bruta_tot_mdp                                      FLOAT,
    consu_intermedio_mdp                                    FLOAT,
    valor_agregado_censal_bruto_mdp                         FLOAT,
    inversion_tot_mdp                                       FLOAT,
    form_brut_cap_mdp                                       FLOAT,
    mar_por_rev_mdp                                         FLOAT,
    gastos_tot_mdp                                          FLOAT,
    ingr_tot_general_mdp                                    FLOAT,
    valor_productos_elaborados_mdp                          FLOAT,
    act_fijos_uso_propio_mdp                                FLOAT,
    invent_inic_mdp                                         FLOAT,
    invent_final_mdp                                        FLOAT,
    var_exis_mdp                                            FLOAT,
    invent_inic_proceso_mdp                                 FLOAT,
    invent_final_proceso_mdp                                FLOAT,
    var_invent_proceso_mdp                                  FLOAT,
    invent_inic_reventa_mdp                                 FLOAT,
    invent_final_reventa_mdp                                FLOAT,
    acervo_act_fijos_mdp                                    FLOAT,
    depreciacion_act_fijos_mdp                              FLOAT,
    compra_act_fijos_mdp                                    FLOAT,
    ventas_act_fijos_mdp                                    FLOAT,
    acervo_maquinaria_equipo_mdp                            FLOAT,
    acervo_bienes_inmuebles_mdp                             FLOAT,
    acervo_unidades_transporte_mdp                          FLOAT,
    acervo_equipo_computo_mdp                               FLOAT,
    acervo_mobiliario_oficina_mdp                           FLOAT
);
COMMENT ON COLUMN stg_economico_estatal_2024.censo_id IS 'Referencia al censo economico';
COMMENT ON COLUMN stg_economico_estatal_2024.actividad_economica_id IS 'Referencia a la actividad economica SCIAN';
COMMENT ON COLUMN stg_economico_estatal_2024.estrato_id IS 'Referencia al estrato de personal ocupado';
COMMENT ON COLUMN stg_economico_estatal_2024.cve_ent IS 'Clave de entidad federativa';
COMMENT ON COLUMN stg_economico_estatal_2024.sector IS 'Sector de actividad economica SCIAN (solo 2024)';
COMMENT ON COLUMN stg_economico_estatal_2024.subsector IS 'Subsector de actividad economica SCIAN (solo 2024)';
COMMENT ON COLUMN stg_economico_estatal_2024.rama IS 'Rama de actividad economica SCIAN (solo 2024)';
COMMENT ON COLUMN stg_economico_estatal_2024.subrama IS 'Subrama de actividad economica SCIAN (solo 2024)';
COMMENT ON COLUMN stg_economico_estatal_2024.clase IS 'Clase de actividad economica SCIAN (solo 2024)';
COMMENT ON COLUMN stg_economico_estatal_2024.unidades_economicas IS 'Unidades economicas';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_ocupado_tot IS 'Personal ocupado total';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_ocupado_tot_h IS 'Personal ocupado total, hombres';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_ocupado_tot_m IS 'Personal ocupado total, mujeres';
COMMENT ON COLUMN stg_economico_estatal_2024.horas_pers_ocupado_tot_mh IS 'Horas trabajadas por personal ocupado total (miles de horas)';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_dep_razon_social IS 'Personal dependiente de la razon social total';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_dep_razon_social_h IS 'Personal dependiente de la razon social, hombres';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_dep_razon_social_m IS 'Personal dependiente de la razon social, mujeres';
COMMENT ON COLUMN stg_economico_estatal_2024.horas_pers_dep_razon_social_mh IS 'Horas trabajadas por personal dependiente de la razon social (miles de horas)';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_remu IS 'Personal remunerado total';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_remu_h IS 'Personal remunerado, hombres';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_remu_m IS 'Personal remunerado, mujeres';
COMMENT ON COLUMN stg_economico_estatal_2024.horas_pers_remu_mh IS 'Horas trabajadas por personal remunerado (miles de horas)';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_no_remu IS 'Personas propietarias, familiares y otro personal no remunerado total';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_no_remu_h IS 'Personas propietarias, familiares y otro personal no remunerado, hombres';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_no_remu_m IS 'Personas propietarias, familiares y otro personal no remunerado, mujeres';
COMMENT ON COLUMN stg_economico_estatal_2024.horas_pers_no_remu_mh IS 'Horas trabajadas por personal no remunerado (miles de horas)';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_prod_ventas_servicios IS 'Personal de produccion, ventas y servicios total';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_prod_ventas_servicios_h IS 'Personal de produccion, ventas y servicios, hombres';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_prod_ventas_servicios_m IS 'Personal de produccion, ventas y servicios, mujeres';
COMMENT ON COLUMN stg_economico_estatal_2024.horas_pers_prod_ventas_servicios_mh IS 'Horas trabajadas por personal de produccion, ventas y servicios (miles de horas)';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_admin_contable_direccion IS 'Personal administrativo, contable y de direccion total';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_admin_contable_direccion_h IS 'Personal administrativo, contable y de direccion, hombres';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_admin_contable_direccion_m IS 'Personal administrativo, contable y de direccion, mujeres';
COMMENT ON COLUMN stg_economico_estatal_2024.horas_pers_admin_contable_direccion_mh IS 'Horas trabajadas por personal administrativo, contable y de direccion (miles de horas)';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_no_dep_razon_social IS 'Personal no dependiente de la razon social total';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_no_dep_razon_social_h IS 'Personal no dependiente de la razon social, hombres';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_no_dep_razon_social_m IS 'Personal no dependiente de la razon social, mujeres';
COMMENT ON COLUMN stg_economico_estatal_2024.horas_pers_no_dep_razon_social_mh IS 'Horas trabajadas por personal no dependiente de la razon social (miles de horas)';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_contratado_otra_razon_social IS 'Personal contratado y proporcionado por otra razon social total';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_contratado_otra_razon_social_h IS 'Personal contratado y proporcionado por otra razon social, hombres';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_contratado_otra_razon_social_m IS 'Personal contratado y proporcionado por otra razon social, mujeres';
COMMENT ON COLUMN stg_economico_estatal_2024.horas_pers_contratado_otra_razon_social_mh IS 'Horas trabajadas por personal contratado por otra razon social (miles de horas)';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_honorarios IS 'Personal por honorarios o comisiones sin sueldo o salario fijo total';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_honorarios_h IS 'Personal por honorarios o comisiones sin sueldo o salario fijo, hombres';
COMMENT ON COLUMN stg_economico_estatal_2024.pers_honorarios_m IS 'Personal por honorarios o comisiones sin sueldo o salario fijo, mujeres';
COMMENT ON COLUMN stg_economico_estatal_2024.horas_pers_honorarios_mh IS 'Horas trabajadas por personal por honorarios (miles de horas)';
COMMENT ON COLUMN stg_economico_estatal_2024.remuneraciones_tot_mdp IS 'Total de remuneraciones (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.salarios_pers_prod_ventas_servicios_mdp IS 'Total de salarios al personal de produccion, ventas y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.sueldos_pers_admin_contable_direccion_mdp IS 'Total de sueldos al personal administrativo, contable y de direccion (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.contribuciones_seguridad_social_mdp IS 'Contribuciones patronales a regimenes de seguridad social (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.otras_prestaciones_sociales_mdp IS 'Otras prestaciones sociales (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.utilidades_repartidas_mdp IS 'Utilidades repartidas al personal (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.indemnizacion_liquidacion_mdp IS 'Gastos por indemnizacion o liquidacion del personal (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.gastos_consu_tot_mdp IS 'Total de gastos por consumo de bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.mercancias_compradas_reventa_mdp IS 'Mercancias y bienes comprados para la reventa (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.materiales_servicios_mdp IS 'Materiales e insumos consumidos para la prestacion de servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.materias_primas_mdp IS 'Materias primas y materiales que se integran a la produccion (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.combustibles_lubricantes_energeticos_mdp IS 'Consumo de combustibles, lubricantes y energeticos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.renta_alquiler_bienes_mdp IS 'Renta y alquiler de bienes muebles e inmuebles (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.servicios_profesionales_mdp IS 'Contratacion de servicios profesionales, cientificos y tecnicos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.maquila_servicios_produccion_mdp IS 'Maquila y servicios de produccion de bienes por contrato (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.otros_bienes_servicios_mdp IS 'Consumo de otros bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.fletes_productos_vendidos_mdp IS 'Fletes de productos vendidos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.papeleria_oficina_mdp IS 'Gastos por consumo de papeleria y articulos de oficina (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.energia_electrica_mdp IS 'Gasto por consumo de energia electrica (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.pagos_pers_subcontratado_mdp IS 'Pagos a otra razon social que contrato y proporciono personal (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.honorarios_comisiones_mdp IS 'Gastos por honorarios o comisiones sin sueldo o salario fijo (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.publicidad_mdp IS 'Gastos por publicidad (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.servicios_comunicacion_mdp IS 'Gastos por servicios de comunicacion (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.envases_empaques_mdp IS 'Gastos por consumo de envases y empaques (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.reparaciones_refacciones_mdp IS 'Reparaciones y refacciones para mantenimiento corriente (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.consu_agua_mdp IS 'Consumo de agua (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.ingr_tot_mdp IS 'Total de ingresos por suministro de bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.ingr_reventa_mercancias_mdp IS 'Ingresos por la reventa de mercancias y bienes (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.ingr_servicios_profesionales_mdp IS 'Ingresos por prestacion de servicios profesionales, cientificos y tecnicos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.ingr_venta_productos_mdp IS 'Venta de productos elaborados, generados o extraidos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.ingr_alquiler_bienes_mdp IS 'Ingresos por alquiler de bienes muebles e inmuebles (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.otros_ingr_mdp IS 'Otros ingresos por suministro de bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.otros_componentes_prod_bruta_mdp IS 'Otros componentes de la produccion bruta total (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.ingr_maquila_terceros_mdp IS 'Ingresos por maquilar o transformar materias primas propiedad de terceros (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.prod_bruta_tot_mdp IS 'Produccion bruta total (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.consu_intermedio_mdp IS 'Consumo intermedio (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.valor_agregado_censal_bruto_mdp IS 'Valor agregado censal bruto (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.inversion_tot_mdp IS 'Inversion total (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.form_brut_cap_mdp IS 'Formacion bruta de capital fijo (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.mar_por_rev_mdp IS 'Margen por reventa de mercancias (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.gastos_tot_mdp IS 'Total de gastos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.ingr_tot_general_mdp IS 'Total de ingresos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.valor_productos_elaborados_mdp IS 'Valor de productos elaborados, bienes generados y extraidos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.act_fijos_uso_propio_mdp IS 'Activos fijos producidos para uso propio (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.invent_inic_mdp IS 'Total de inventario inicial (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.invent_final_mdp IS 'Total de inventario final (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.var_exis_mdp IS 'Variacion total de existencias (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.invent_inic_proceso_mdp IS 'Total de inventario inicial de productos en proceso (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.invent_final_proceso_mdp IS 'Total de inventario final de productos en proceso (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.var_invent_proceso_mdp IS 'Variacion de inventarios de productos en proceso (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.invent_inic_reventa_mdp IS 'Total de inventario inicial de mercancias compradas para reventa (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.invent_final_reventa_mdp IS 'Total de inventario final de mercancias compradas para reventa (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.acervo_act_fijos_mdp IS 'Acervo total de activos fijos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.depreciacion_act_fijos_mdp IS 'Depreciacion total de activos fijos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.compra_act_fijos_mdp IS 'Compra y adquisicion total de activos fijos y reformas mayores (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.ventas_act_fijos_mdp IS 'Ventas totales de activos fijos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.acervo_maquinaria_equipo_mdp IS 'Acervo total de maquinaria y equipo de produccion (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.acervo_bienes_inmuebles_mdp IS 'Acervo total de bienes inmuebles (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.acervo_unidades_transporte_mdp IS 'Acervo total de unidades y equipo de transporte (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.acervo_equipo_computo_mdp IS 'Acervo total de equipo de computo y perifericos (millones de pesos)';
COMMENT ON COLUMN stg_economico_estatal_2024.acervo_mobiliario_oficina_mdp IS 'Acervo total de mobiliario, equipo de oficina y otros activos fijos (millones de pesos)';

CREATE TABLE IF NOT EXISTS stg_economico_municipal_2024 (
    id                                        SERIAL PRIMARY KEY,
    censo_id                              INTEGER NOT NULL REFERENCES cat_censos(id),
    actividad_economica_id          INTEGER REFERENCES cat_actividades_economicas(id),
    estrato_id                      INTEGER REFERENCES cat_estratos(id),
    cve_ent                                   INTEGER NOT NULL,
    cve_mun                                   INTEGER NOT NULL,
    sector                                                  TEXT,
    subsector                                               TEXT,
    rama                                                    TEXT,
    subrama                                                 TEXT,
    clase                                                   TEXT,
    unidades_economicas                                     FLOAT,
    pers_ocupado_tot                                        FLOAT,
    pers_ocupado_tot_h                                      FLOAT,
    pers_ocupado_tot_m                                      FLOAT,
    horas_pers_ocupado_tot_mh                               FLOAT,
    pers_dep_razon_social                                   FLOAT,
    pers_dep_razon_social_h                                 FLOAT,
    pers_dep_razon_social_m                                 FLOAT,
    horas_pers_dep_razon_social_mh                          FLOAT,
    pers_remu                                               FLOAT,
    pers_remu_h                                             FLOAT,
    pers_remu_m                                             FLOAT,
    horas_pers_remu_mh                                      FLOAT,
    pers_no_remu                                            FLOAT,
    pers_no_remu_h                                          FLOAT,
    pers_no_remu_m                                          FLOAT,
    horas_pers_no_remu_mh                                   FLOAT,
    pers_prod_ventas_servicios                              FLOAT,
    pers_prod_ventas_servicios_h                            FLOAT,
    pers_prod_ventas_servicios_m                            FLOAT,
    horas_pers_prod_ventas_servicios_mh                     FLOAT,
    pers_admin_contable_direccion                           FLOAT,
    pers_admin_contable_direccion_h                         FLOAT,
    pers_admin_contable_direccion_m                         FLOAT,
    horas_pers_admin_contable_direccion_mh                  FLOAT,
    pers_no_dep_razon_social                                FLOAT,
    pers_no_dep_razon_social_h                              FLOAT,
    pers_no_dep_razon_social_m                              FLOAT,
    horas_pers_no_dep_razon_social_mh                       FLOAT,
    pers_contratado_otra_razon_social                       FLOAT,
    pers_contratado_otra_razon_social_h                     FLOAT,
    pers_contratado_otra_razon_social_m                     FLOAT,
    horas_pers_contratado_otra_razon_social_mh              FLOAT,
    pers_honorarios                                         FLOAT,
    pers_honorarios_h                                       FLOAT,
    pers_honorarios_m                                       FLOAT,
    horas_pers_honorarios_mh                                FLOAT,
    remuneraciones_tot_mdp                                  FLOAT,
    salarios_pers_prod_ventas_servicios_mdp                 FLOAT,
    sueldos_pers_admin_contable_direccion_mdp               FLOAT,
    contribuciones_seguridad_social_mdp                     FLOAT,
    otras_prestaciones_sociales_mdp                         FLOAT,
    utilidades_repartidas_mdp                               FLOAT,
    indemnizacion_liquidacion_mdp                           FLOAT,
    gastos_consu_tot_mdp                                    FLOAT,
    mercancias_compradas_reventa_mdp                        FLOAT,
    materiales_servicios_mdp                                FLOAT,
    materias_primas_mdp                                     FLOAT,
    combustibles_lubricantes_energeticos_mdp                FLOAT,
    renta_alquiler_bienes_mdp                               FLOAT,
    servicios_profesionales_mdp                             FLOAT,
    maquila_servicios_produccion_mdp                        FLOAT,
    otros_bienes_servicios_mdp                              FLOAT,
    fletes_productos_vendidos_mdp                           FLOAT,
    papeleria_oficina_mdp                                   FLOAT,
    energia_electrica_mdp                                   FLOAT,
    pagos_pers_subcontratado_mdp                            FLOAT,
    honorarios_comisiones_mdp                               FLOAT,
    publicidad_mdp                                          FLOAT,
    servicios_comunicacion_mdp                              FLOAT,
    envases_empaques_mdp                                    FLOAT,
    reparaciones_refacciones_mdp                            FLOAT,
    consu_agua_mdp                                          FLOAT,
    ingr_tot_mdp                                            FLOAT,
    ingr_reventa_mercancias_mdp                             FLOAT,
    ingr_servicios_profesionales_mdp                        FLOAT,
    ingr_venta_productos_mdp                                FLOAT,
    ingr_alquiler_bienes_mdp                                FLOAT,
    otros_ingr_mdp                                          FLOAT,
    otros_componentes_prod_bruta_mdp                        FLOAT,
    ingr_maquila_terceros_mdp                               FLOAT,
    prod_bruta_tot_mdp                                      FLOAT,
    consu_intermedio_mdp                                    FLOAT,
    valor_agregado_censal_bruto_mdp                         FLOAT,
    inversion_tot_mdp                                       FLOAT,
    form_brut_cap_mdp                                       FLOAT,
    mar_por_rev_mdp                                         FLOAT,
    gastos_tot_mdp                                          FLOAT,
    ingr_tot_general_mdp                                    FLOAT,
    valor_productos_elaborados_mdp                          FLOAT,
    act_fijos_uso_propio_mdp                                FLOAT,
    invent_inic_mdp                                         FLOAT,
    invent_final_mdp                                        FLOAT,
    var_exis_mdp                                            FLOAT,
    invent_inic_proceso_mdp                                 FLOAT,
    invent_final_proceso_mdp                                FLOAT,
    var_invent_proceso_mdp                                  FLOAT,
    invent_inic_reventa_mdp                                 FLOAT,
    invent_final_reventa_mdp                                FLOAT,
    acervo_act_fijos_mdp                                    FLOAT,
    depreciacion_act_fijos_mdp                              FLOAT,
    compra_act_fijos_mdp                                    FLOAT,
    ventas_act_fijos_mdp                                    FLOAT,
    acervo_maquinaria_equipo_mdp                            FLOAT,
    acervo_bienes_inmuebles_mdp                             FLOAT,
    acervo_unidades_transporte_mdp                          FLOAT,
    acervo_equipo_computo_mdp                               FLOAT,
    acervo_mobiliario_oficina_mdp                           FLOAT
);
COMMENT ON COLUMN stg_economico_municipal_2024.censo_id IS 'Referencia al censo economico';
COMMENT ON COLUMN stg_economico_municipal_2024.actividad_economica_id IS 'Referencia a la actividad economica SCIAN';
COMMENT ON COLUMN stg_economico_municipal_2024.estrato_id IS 'Referencia al estrato de personal ocupado';
COMMENT ON COLUMN stg_economico_municipal_2024.cve_ent IS 'Clave de entidad federativa';
COMMENT ON COLUMN stg_economico_municipal_2024.cve_mun IS 'Clave de municipio';
COMMENT ON COLUMN stg_economico_municipal_2024.sector IS 'Sector de actividad economica SCIAN (solo 2024)';
COMMENT ON COLUMN stg_economico_municipal_2024.subsector IS 'Subsector de actividad economica SCIAN (solo 2024)';
COMMENT ON COLUMN stg_economico_municipal_2024.rama IS 'Rama de actividad economica SCIAN (solo 2024)';
COMMENT ON COLUMN stg_economico_municipal_2024.subrama IS 'Subrama de actividad economica SCIAN (solo 2024)';
COMMENT ON COLUMN stg_economico_municipal_2024.clase IS 'Clase de actividad economica SCIAN (solo 2024)';
COMMENT ON COLUMN stg_economico_municipal_2024.unidades_economicas IS 'Unidades economicas';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_ocupado_tot IS 'Personal ocupado total';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_ocupado_tot_h IS 'Personal ocupado total, hombres';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_ocupado_tot_m IS 'Personal ocupado total, mujeres';
COMMENT ON COLUMN stg_economico_municipal_2024.horas_pers_ocupado_tot_mh IS 'Horas trabajadas por personal ocupado total (miles de horas)';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_dep_razon_social IS 'Personal dependiente de la razon social total';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_dep_razon_social_h IS 'Personal dependiente de la razon social, hombres';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_dep_razon_social_m IS 'Personal dependiente de la razon social, mujeres';
COMMENT ON COLUMN stg_economico_municipal_2024.horas_pers_dep_razon_social_mh IS 'Horas trabajadas por personal dependiente de la razon social (miles de horas)';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_remu IS 'Personal remunerado total';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_remu_h IS 'Personal remunerado, hombres';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_remu_m IS 'Personal remunerado, mujeres';
COMMENT ON COLUMN stg_economico_municipal_2024.horas_pers_remu_mh IS 'Horas trabajadas por personal remunerado (miles de horas)';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_no_remu IS 'Personas propietarias, familiares y otro personal no remunerado total';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_no_remu_h IS 'Personas propietarias, familiares y otro personal no remunerado, hombres';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_no_remu_m IS 'Personas propietarias, familiares y otro personal no remunerado, mujeres';
COMMENT ON COLUMN stg_economico_municipal_2024.horas_pers_no_remu_mh IS 'Horas trabajadas por personal no remunerado (miles de horas)';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_prod_ventas_servicios IS 'Personal de produccion, ventas y servicios total';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_prod_ventas_servicios_h IS 'Personal de produccion, ventas y servicios, hombres';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_prod_ventas_servicios_m IS 'Personal de produccion, ventas y servicios, mujeres';
COMMENT ON COLUMN stg_economico_municipal_2024.horas_pers_prod_ventas_servicios_mh IS 'Horas trabajadas por personal de produccion, ventas y servicios (miles de horas)';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_admin_contable_direccion IS 'Personal administrativo, contable y de direccion total';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_admin_contable_direccion_h IS 'Personal administrativo, contable y de direccion, hombres';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_admin_contable_direccion_m IS 'Personal administrativo, contable y de direccion, mujeres';
COMMENT ON COLUMN stg_economico_municipal_2024.horas_pers_admin_contable_direccion_mh IS 'Horas trabajadas por personal administrativo, contable y de direccion (miles de horas)';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_no_dep_razon_social IS 'Personal no dependiente de la razon social total';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_no_dep_razon_social_h IS 'Personal no dependiente de la razon social, hombres';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_no_dep_razon_social_m IS 'Personal no dependiente de la razon social, mujeres';
COMMENT ON COLUMN stg_economico_municipal_2024.horas_pers_no_dep_razon_social_mh IS 'Horas trabajadas por personal no dependiente de la razon social (miles de horas)';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_contratado_otra_razon_social IS 'Personal contratado y proporcionado por otra razon social total';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_contratado_otra_razon_social_h IS 'Personal contratado y proporcionado por otra razon social, hombres';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_contratado_otra_razon_social_m IS 'Personal contratado y proporcionado por otra razon social, mujeres';
COMMENT ON COLUMN stg_economico_municipal_2024.horas_pers_contratado_otra_razon_social_mh IS 'Horas trabajadas por personal contratado por otra razon social (miles de horas)';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_honorarios IS 'Personal por honorarios o comisiones sin sueldo o salario fijo total';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_honorarios_h IS 'Personal por honorarios o comisiones sin sueldo o salario fijo, hombres';
COMMENT ON COLUMN stg_economico_municipal_2024.pers_honorarios_m IS 'Personal por honorarios o comisiones sin sueldo o salario fijo, mujeres';
COMMENT ON COLUMN stg_economico_municipal_2024.horas_pers_honorarios_mh IS 'Horas trabajadas por personal por honorarios (miles de horas)';
COMMENT ON COLUMN stg_economico_municipal_2024.remuneraciones_tot_mdp IS 'Total de remuneraciones (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.salarios_pers_prod_ventas_servicios_mdp IS 'Total de salarios al personal de produccion, ventas y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.sueldos_pers_admin_contable_direccion_mdp IS 'Total de sueldos al personal administrativo, contable y de direccion (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.contribuciones_seguridad_social_mdp IS 'Contribuciones patronales a regimenes de seguridad social (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.otras_prestaciones_sociales_mdp IS 'Otras prestaciones sociales (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.utilidades_repartidas_mdp IS 'Utilidades repartidas al personal (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.indemnizacion_liquidacion_mdp IS 'Gastos por indemnizacion o liquidacion del personal (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.gastos_consu_tot_mdp IS 'Total de gastos por consumo de bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.mercancias_compradas_reventa_mdp IS 'Mercancias y bienes comprados para la reventa (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.materiales_servicios_mdp IS 'Materiales e insumos consumidos para la prestacion de servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.materias_primas_mdp IS 'Materias primas y materiales que se integran a la produccion (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.combustibles_lubricantes_energeticos_mdp IS 'Consumo de combustibles, lubricantes y energeticos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.renta_alquiler_bienes_mdp IS 'Renta y alquiler de bienes muebles e inmuebles (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.servicios_profesionales_mdp IS 'Contratacion de servicios profesionales, cientificos y tecnicos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.maquila_servicios_produccion_mdp IS 'Maquila y servicios de produccion de bienes por contrato (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.otros_bienes_servicios_mdp IS 'Consumo de otros bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.fletes_productos_vendidos_mdp IS 'Fletes de productos vendidos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.papeleria_oficina_mdp IS 'Gastos por consumo de papeleria y articulos de oficina (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.energia_electrica_mdp IS 'Gasto por consumo de energia electrica (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.pagos_pers_subcontratado_mdp IS 'Pagos a otra razon social que contrato y proporciono personal (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.honorarios_comisiones_mdp IS 'Gastos por honorarios o comisiones sin sueldo o salario fijo (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.publicidad_mdp IS 'Gastos por publicidad (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.servicios_comunicacion_mdp IS 'Gastos por servicios de comunicacion (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.envases_empaques_mdp IS 'Gastos por consumo de envases y empaques (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.reparaciones_refacciones_mdp IS 'Reparaciones y refacciones para mantenimiento corriente (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.consu_agua_mdp IS 'Consumo de agua (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.ingr_tot_mdp IS 'Total de ingresos por suministro de bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.ingr_reventa_mercancias_mdp IS 'Ingresos por la reventa de mercancias y bienes (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.ingr_servicios_profesionales_mdp IS 'Ingresos por prestacion de servicios profesionales, cientificos y tecnicos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.ingr_venta_productos_mdp IS 'Venta de productos elaborados, generados o extraidos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.ingr_alquiler_bienes_mdp IS 'Ingresos por alquiler de bienes muebles e inmuebles (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.otros_ingr_mdp IS 'Otros ingresos por suministro de bienes y servicios (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.otros_componentes_prod_bruta_mdp IS 'Otros componentes de la produccion bruta total (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.ingr_maquila_terceros_mdp IS 'Ingresos por maquilar o transformar materias primas propiedad de terceros (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.prod_bruta_tot_mdp IS 'Produccion bruta total (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.consu_intermedio_mdp IS 'Consumo intermedio (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.valor_agregado_censal_bruto_mdp IS 'Valor agregado censal bruto (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.inversion_tot_mdp IS 'Inversion total (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.form_brut_cap_mdp IS 'Formacion bruta de capital fijo (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.mar_por_rev_mdp IS 'Margen por reventa de mercancias (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.gastos_tot_mdp IS 'Total de gastos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.ingr_tot_general_mdp IS 'Total de ingresos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.valor_productos_elaborados_mdp IS 'Valor de productos elaborados, bienes generados y extraidos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.act_fijos_uso_propio_mdp IS 'Activos fijos producidos para uso propio (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.invent_inic_mdp IS 'Total de inventario inicial (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.invent_final_mdp IS 'Total de inventario final (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.var_exis_mdp IS 'Variacion total de existencias (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.invent_inic_proceso_mdp IS 'Total de inventario inicial de productos en proceso (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.invent_final_proceso_mdp IS 'Total de inventario final de productos en proceso (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.var_invent_proceso_mdp IS 'Variacion de inventarios de productos en proceso (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.invent_inic_reventa_mdp IS 'Total de inventario inicial de mercancias compradas para reventa (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.invent_final_reventa_mdp IS 'Total de inventario final de mercancias compradas para reventa (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.acervo_act_fijos_mdp IS 'Acervo total de activos fijos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.depreciacion_act_fijos_mdp IS 'Depreciacion total de activos fijos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.compra_act_fijos_mdp IS 'Compra y adquisicion total de activos fijos y reformas mayores (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.ventas_act_fijos_mdp IS 'Ventas totales de activos fijos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.acervo_maquinaria_equipo_mdp IS 'Acervo total de maquinaria y equipo de produccion (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.acervo_bienes_inmuebles_mdp IS 'Acervo total de bienes inmuebles (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.acervo_unidades_transporte_mdp IS 'Acervo total de unidades y equipo de transporte (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.acervo_equipo_computo_mdp IS 'Acervo total de equipo de computo y perifericos (millones de pesos)';
COMMENT ON COLUMN stg_economico_municipal_2024.acervo_mobiliario_oficina_mdp IS 'Acervo total de mobiliario, equipo de oficina y otros activos fijos (millones de pesos)';
