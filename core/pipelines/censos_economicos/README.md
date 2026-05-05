# sieej

## Esquema

<img src="assets/er_censos_economicos.png" width="1500" height="10000">

## Diccionario de variables

### cat_censos

| Columna | Descripción |
|---------|-------------|
| anio | Año del censo económico |
| descripcion | Nombre del censo (ej. Censos Economicos 2019) |
| fecha_publicacion | Fecha de publicación del censo por INEGI |
| fuente | Organismo que publica los datos (INEGI) |

### cat_clasificadores_codigos

| Columna | Descripción |
|---------|-------------|
| id | Identificador único del clasificador de código |
| clasificador | Nivel de clasificación (Gran sector, Sector, Subsector, Rama, Subrama, Clase) |

### cat_actividades_economicas

| Columna | Descripción |
|---------|-------------|
| censo_id | Referencia al censo al que pertenece |
| codigo | Código de la actividad económica |
| descripcion | Nombre de la actividad económica |
| codigo_id | Referencia al nivel de clasificación |

### cat_estratos

| Columna | Descripción |
|---------|-------------|
| id | Identificador único del estrato |
| codigo | Código numérico del estrato (1=0-10, 2=11-50, 3=51-250, 4=251+, 99=Confidencialidad) |
| descripcion | Rango de empleados (ej. 0 a 10, 11 a 50) |

### stg_economico_nacional_2019 / stg_economico_estatal_2019 / stg_economico_municipal_2019

| Columna | Descripción |
|---------|-------------|
| censo_id | Referencia al censo económico 2019 |
| actividad_economica_id | Referencia a la actividad económica |
| estrato_id | Referencia al estrato de empleados |
| unidades_economicas | Cantidad de unidades económicas |
| pers_ocupado_tot | Personal ocupado total |
| pers_ocupado_tot_h | Personal ocupado total, hombres |
| pers_ocupado_tot_m | Personal ocupado total, mujeres |
| horas_pers_ocupado_tot_mh | Horas de personal ocupado total en miles de horas |
| pers_dep_razon_social | Personal dependiente de razón social |
| pers_dep_razon_social_h | Personal dependiente de razón social, hombres |
| pers_dep_razon_social_m | Personal dependiente de razón social, mujeres |
| horas_pers_dep_razon_social_mh | Horas de personal dependiente de razón social en miles de horas |
| pers_remu | Personal remunerado total |
| pers_remu_h | Personal remunerado, hombres |
| pers_remu_m | Personal remunerado, mujeres |
| horas_pers_remu_mh | Horas de personal remunerado en miles de horas |
| pers_no_remu | Personal no remunerado total |
| pers_no_remu_h | Personal no remunerado, hombres |
| pers_no_remu_m | Personal no remunerado, mujeres |
| horas_pers_no_remu_mh | Horas de personal no remunerado en miles de horas |
| pers_prod_ventas_servicios | Personal de producción, ventas y servicios |
| pers_prod_ventas_servicios_h | Personal de producción, ventas y servicios, hombres |
| pers_prod_ventas_servicios_m | Personal de producción, ventas y servicios, mujeres |
| horas_pers_prod_ventas_servicios_mh | Horas de personal de producción, ventas y servicios en miles de horas |
| pers_admin_contable_direccion | Personal administrativo, contable y de dirección |
| pers_admin_contable_direccion_h | Personal administrativo, contable y de dirección, hombres |
| pers_admin_contable_direccion_m | Personal administrativo, contable y de dirección, mujeres |
| horas_pers_admin_contable_direccion_mh | Horas de personal administrativo, contable y de dirección en miles de horas |
| pers_no_dep_razon_social | Personal no dependiente de razón social |
| pers_no_dep_razon_social_h | Personal no dependiente de razón social, hombres |
| pers_no_dep_razon_social_m | Personal no dependiente de razón social, mujeres |
| horas_pers_no_dep_razon_social_mh | Horas de personal no dependiente de razón social en miles de horas |
| pers_contratado_otra_razon_social | Personal contratado de otra razón social |
| pers_contratado_otra_razon_social_h | Personal contratado de otra razón social, hombres |
| pers_contratado_otra_razon_social_m | Personal contratado de otra razón social, mujeres |
| horas_pers_contratado_otra_razon_social_mh | Horas de personal contratado de otra razón social en miles de horas |
| pers_honorarios | Personal por honorarios |
| pers_honorarios_h | Personal por honorarios, hombres |
| pers_honorarios_m | Personal por honorarios, mujeres |
| horas_pers_honorarios_mh | Horas de personal por honorarios en miles de horas |
| remuneraciones_tot_mdp | Total de remuneraciones en millones de pesos |
| salarios_pers_prod_ventas_servicios_mdp | Salarios de personal de producción, ventas y servicios en millones de pesos |
| sueldos_pers_admin_contable_direccion_mdp | Sueldos de personal administrativo, contable y de dirección en millones de pesos |
| contribuciones_seguridad_social_mdp | Contribuciones a seguridad social en millones de pesos |
| otras_prestaciones_sociales_mdp | Otras prestaciones sociales en millones de pesos |
| utilidades_repartidas_mdp | Utilidades repartidas en millones de pesos |
| indemnizacion_liquidacion_mdp | Indemnización y liquidación en millones de pesos |
| gastos_consu_tot_mdp | Total de gastos de consumo en millones de pesos |
| mercancias_compradas_reventa_mdp | Mercancías compradas para reventa en millones de pesos |
| materiales_servicios_mdp | Materiales y servicios en millones de pesos |
| materias_primas_mdp | Materias primas en millones de pesos |
| combustibles_lubricantes_energeticos_mdp | Combustibles, lubricantes y energéticos en millones de pesos |
| renta_alquiler_bienes_mdp | Renta y alquiler de bienes en millones de pesos |
| servicios_profesionales_mdp | Servicios profesionales en millones de pesos |
| maquila_servicios_produccion_mdp | Maquila y servicios de producción en millones de pesos |
| otros_bienes_servicios_mdp | Otros bienes y servicios en millones de pesos |
| fletes_productos_vendidos_mdp | Fletes de productos vendidos en millones de pesos |
| papeleria_oficina_mdp | Papelería de oficina en millones de pesos |
| energia_electrica_mdp | Energía eléctrica en millones de pesos |
| pagos_pers_subcontratado_mdp | Pagos a personal subcontratado en millones de pesos |
| honorarios_comisiones_mdp | Honorarios y comisiones en millones de pesos |
| publicidad_mdp | Publicidad en millones de pesos |
| servicios_comunicacion_mdp | Servicios de comunicación en millones de pesos |
| envases_empaques_mdp | Envases y empaques en millones de pesos |
| reparaciones_refacciones_mdp | Reparaciones y refacciones en millones de pesos |
| consu_agua_mdp | Consumo de agua en millones de pesos |
| ingr_tot_mdp | Total de ingresos en millones de pesos |
| ingr_reventa_mercancias_mdp | Ingresos por reventa de mercancías en millones de pesos |
| ingr_servicios_profesionales_mdp | Ingresos por servicios profesionales en millones de pesos |
| ingr_venta_productos_mdp | Ingresos por venta de productos en millones de pesos |
| ingr_alquiler_bienes_mdp | Ingresos por alquiler de bienes en millones de pesos |
| otros_ingr_mdp | Otros ingresos en millones de pesos |
| otros_componentes_prod_bruta_mdp | Otros componentes de la producción bruta en millones de pesos |
| ingr_maquila_terceros_mdp | Ingresos por maquila de terceros en millones de pesos |
| prod_bruta_tot_mdp | Producción bruta total en millones de pesos |
| consu_intermedio_mdp | Consumo intermedio en millones de pesos |
| valor_agregado_censal_bruto_mdp | Valor agregado censal bruto en millones de pesos |
| inversion_tot_mdp | Inversión total en millones de pesos |
| form_brut_cap_mdp | Formación bruta de capital en millones de pesos |
| mar_por_rev_mdp | Margen por reventa en millones de pesos |
| gastos_tot_mdp | Total de gastos en millones de pesos |
| ingr_tot_general_mdp | Total de ingresos general en millones de pesos |
| valor_productos_elaborados_mdp | Valor de productos elaborados en millones de pesos |
| act_fijos_uso_propio_mdp | Activos fijos de uso propio en millones de pesos |
| invent_inic_mdp | Inventario inicial en millones de pesos |
| invent_final_mdp | Inventario final en millones de pesos |
| var_exis_mdp | Variación de existencias en millones de pesos |
| invent_inic_proceso_mdp | Inventario inicial en proceso en millones de pesos |
| invent_final_proceso_mdp | Inventario final en proceso en millones de pesos |
| var_invent_proceso_mdp | Variación de inventario en proceso en millones de pesos |
| invent_inic_reventa_mdp | Inventario inicial para reventa en millones de pesos |
| invent_final_reventa_mdp | Inventario final para reventa en millones de pesos |
| acervo_act_fijos_mdp | Acervo de activos fijos en millones de pesos |
| depreciacion_act_fijos_mdp | Depreciación de activos fijos en millones de pesos |
| compra_act_fijos_mdp | Compra de activos fijos en millones de pesos |
| ventas_act_fijos_mdp | Ventas de activos fijos en millones de pesos |
| acervo_maquinaria_equipo_mdp | Acervo de maquinaria y equipo en millones de pesos |
| acervo_bienes_inmuebles_mdp | Acervo de bienes inmuebles en millones de pesos |
| acervo_unidades_transporte_mdp | Acervo de unidades de transporte en millones de pesos |
| acervo_equipo_computo_mdp | Acervo de equipo de cómputo en millones de pesos |
| acervo_mobiliario_oficina_mdp | Acervo de mobiliario de oficina en millones de pesos |
| part_bienes_elab_gen_ext_pbt | Participación de bienes elaborados, generados o extraídos en producción bruta |
| part_imatmpp | Participación de impuestos, aranceles y materias primas para procesamiento |
| part_act_fijos_producidos_uso_propio_pb | Participación de activos fijos producidos para uso propio en producción bruta |
| part_var_exist_prod_proceso_pbt | Participación de variación de existencias en proceso en producción bruta |
| part_mar_rev_merc_pbt | Participación de margen de reventa de mercancías en producción bruta |
| part_serv_prof_cient_tec_pbt | Participación de servicios profesionales, científicos y técnicos en producción bruta |
| part_ingr_abmi_produccion | Participación de ingresos por actividades de alojamiento, bebidas y servicios de comida |
| part_otros_comp_pbt | Participación de otros componentes en producción bruta |
| part_ssen_tr | Participación de servicios y suministros en total de remuneraciones |
| part_salarios_ppvs_tr | Participación de salarios de personal de producción, ventas y servicios en total de remuneraciones |
| part_sueldos_pers_acd_tr | Participación de sueldos de personal administrativo, contable y de dirección en total de remuneraciones |
| pers_dependiente_pers_ocup_tot_porcentaje | Porcentaje de personal dependiente sobre personal ocupado total |
| pnr_perasonal_ocupado_tot | Participación no remunerada en personal ocupado total |
| pnr_po_dependiente | Participación no remunerada en personal dependiente |
| prest_soc_util_rep_tot_rem | Prestaciones sociales y utilidades repartidas en total de remuneraciones |
| part_urt_tr | Participación de utilidades repartidas en total de remuneraciones |
| part_mt_pers_remu | Participación de total de remuneraciones sobre personal remunerado |
| part_mt_po_produccion_ventas_servicios | Participación de total de remuneraciones en personal de producción, ventas y servicios |
| part_mt_po_acd | Participación de total de remuneraciones en personal administrativo, contable y de dirección |
| prest_soc_tot_rem | Prestaciones sociales en total de remuneraciones |
| part_prestaciones_sociales_utilidades_sueldos_salarios | Participación de prestaciones sociales y utilidades en sueldos y salarios |
| part_mt_pfotn | Participación de total de remuneraciones en prestaciones de fondos de no trabajadores |
| tot_prestaciones_ss | Total de prestaciones de seguridad social |
| part_mt_pcpor | Participación de total de remuneraciones en prestaciones contributivas o propias |
| part_mt_phcs | Participación de total de remuneraciones en prestaciones de salud |
| remuneracion_media_per_ocupada_remu | Remuneración media por personal ocupado remunerado |
| salario_pers_operativo_anual | Salario anual de personal operativo |
| sueldo_pers_administrativo_anual | Sueldo anual de personal administrativo |
| pagos_promedio_per_suministrada | Pagos promedio por personal suministrada |
| pagos_promedio_pers_comisiones_u_honorarios | Pagos promedio por personal con comisiones u honorarios |
| part_remuneraciones_gcbs | Participación de remuneraciones en gastos de consumo de bienes y servicios |
| per_no_dep_pers_ocup_tot | Porcentaje de personal no dependiente en personal ocupado total |
| indem_liqui_remu_tot | Indemnización y liquidación en remuneraciones totales |
| remuneracion_media_per_remu | Remuneración media por personal remunerado |
| horas_dia_trab_prom_pers_remu | Horas promedio de trabajo diario, personal remunerado |
| horas_dia_trab_prom_pers_no_remu | Horas promedio de trabajo diario, personal no remunerado |
| horas_dia_trab_prom_ppvs | Horas promedio de trabajo diario, personal de producción, ventas y servicios |
| horas_dia_trab_prom_empleados_administrativos_control | Horas promedio de trabajo diario, personal administrativo, contable y de dirección |
| horas_dia_trab_prom_pers_comisiones_honorarios | Horas promedio de trabajo diario, personal con comisiones u honorarios |
| valor_agregado_censal_bruto_pbt | Valor agregado censal bruto como porcentaje de producción bruta |
| part_consu_intermedio_pbt | Participación de consumo intermedio en producción bruta |
| va_promedio_per_ocupada | Valor agregado promedio por personal ocupada |
| pbt_pers_ocupado_tot | Producción bruta total por personal ocupado |
| part_mpms_gastos_consu_bienes | Participación de materiales, papelería y materias primas en gastos de consumo de bienes |
| part_mcs_gcbs | Participación de mercancías compradas y servicios en gastos de consumo de bienes y servicios |
| part_cae_gcbs | Participación de combustibles, agua y energía en gastos de consumo de bienes y servicios |
| inversion_ti_tot | Inversión en tecnología de información total |
| part_gastos_consu_otros_bienes_servicios_gastos_consu | Participación de otros bienes y servicios en gastos de consumo |
| inversion_tot_act_fijos | Inversión total en activos fijos |
| part_ivm_ti_suministro_bienes | Participación de inversión en máquinas, vehículos y maquila en inversión total |
| inversion_tot_valor_agregado_censal_bruto | Inversión total en valor agregado censal bruto |
| part_servi_prof_cient | Participación de servicios profesionales, científicos y técnicos |
| part_otros_isbs_ti | Participación de otros inmuebles, servicios, bienes y suministros en inversión total |
| inversion_tot_pbt | Inversión total en producción bruta |
| part_venta_productos_elaborados_generados_o_extraidos_tot | Participación de venta de productos elaborados, generados o extraídos |
| part_ingr_abmi_tot | Participación de ingresos por actividades de alojamiento, bebidas y servicios de comida |
| part_imatmpp_2 | Participación de impuestos, aranceles y materias primas para procesamiento (variante 2) |
| part_mep_tot_act_fijos | Participación de maquinaria y equipo productor en activos fijos |
| part_cif_tot_act_fijos | Participación de construcción e inmuebles fijos en activos fijos |
| part_et_tot_act_fijos | Participación de equipo de transporte en activos fijos |
| part_ecp_tot_act_fijos | Participación de equipo de cómputo en activos fijos |
| margen_bruto_operacion | Margen bruto de operación |
| ing_princ_por_sum_bienes | Ingresos principales por suministro de bienes |
| gp_gcbs | Gastos en gastos de consumo de bienes y servicios |
| gp_ip | Gastos en ingresos principales |
| part_meo_otros_act_fijos_tot | Participación de máquinas, equipo y otros activos fijos |
| valor_act_fijos_per_ocupada | Valor de activos fijos por personal ocupada |
| maqui_equip_prod_a_prod_tot | Maquinaria y equipo productor a producción total |
| acti_fijo_brut_tot | Activos fijos bruto total |
| forma_brut_cap_fijo_acervo_tot | Formación bruta de capital fijo en acervo total |
| produccion_act_fijos_uso_propio_compras_act_fijos | Producción de activos fijos de uso propio y compra de activos fijos |
| otros_isbs_ti_suministro | Otros inmuebles, servicios, bienes y suministros en inversión total |
| gastos_no_derivados_actividad_gcbs | Gastos no derivados de la actividad en gastos de consumo |
| ingr_no_derivados_actividad_isbs | Ingresos no derivados de la actividad en ingresos y suministros |
| valor_promedio_maquinaria_equipo_per_ocupada_anuales | Valor promedio de maquinaria y equipo por personal ocupada anuales |
| ip_respecto_gp | Ingresos principales respecto a gastos principales |
| porcentaje_ip_ti_actividad_financieros | Porcentaje de ingresos principales en total de ingresos, actividades financieras |
| isbs_per_ocupada | Ingresos y suministros de bienes por personal ocupada |
| part_depreciacion_valor_act_fijos | Participación de depreciación en valor de activos fijos |
| tasa_rentabilidad_promedio | Tasa de rentabilidad promedio |
| salario_promedio_diarios_per_operativa | Salario promedio diario, personal operativo |
| sueldo_promedio_diario_per_administrativa | Sueldo promedio diario, personal administrativo |
| va_tot_act_fijos | Valor agregado total en activos fijos |
| part_muje_pers_ocupado_tot | Participación de mujeres en personal ocupado total |
| cve_ent | Clave de entidad federativa (solo para estatal y municipal) |
| cve_mun | Clave de municipio (solo para municipal) |

### stg_economico_nacional_2024 / stg_economico_estatal_2024 / stg_economico_municipal_2024

| Columna | Descripción |
|---------|-------------|
| sector | Clasificación por sector económico |
| subsector | Clasificación por subsector económico |
| rama | Clasificación por rama económica |
| subrama | Clasificación por subrama económica |
| clase | Clasificación por clase económica |
| censo_id | Referencia al censo económico 2024 |
| actividad_economica_id | Referencia a la actividad económica |
| estrato_id | Referencia al estrato de empleados |
| unidades_economicas | Cantidad de unidades económicas |
| pers_ocupado_tot | Personal ocupado total |
| pers_ocupado_tot_h | Personal ocupado total, hombres |
| pers_ocupado_tot_m | Personal ocupado total, mujeres |
| horas_pers_ocupado_tot_mh | Horas de personal ocupado total en miles de horas |
| pers_dep_razon_social | Personal dependiente de razón social |
| pers_dep_razon_social_h | Personal dependiente de razón social, hombres |
| pers_dep_razon_social_m | Personal dependiente de razón social, mujeres |
| horas_pers_dep_razon_social_mh | Horas de personal dependiente de razón social en miles de horas |
| pers_remu | Personal remunerado total |
| pers_remu_h | Personal remunerado, hombres |
| pers_remu_m | Personal remunerado, mujeres |
| horas_pers_remu_mh | Horas de personal remunerado en miles de horas |
| pers_no_remu | Personal no remunerado total |
| pers_no_remu_h | Personal no remunerado, hombres |
| pers_no_remu_m | Personal no remunerado, mujeres |
| horas_pers_no_remu_mh | Horas de personal no remunerado en miles de horas |
| pers_prod_ventas_servicios | Personal de producción, ventas y servicios |
| pers_prod_ventas_servicios_h | Personal de producción, ventas y servicios, hombres |
| pers_prod_ventas_servicios_m | Personal de producción, ventas y servicios, mujeres |
| horas_pers_prod_ventas_servicios_mh | Horas de personal de producción, ventas y servicios en miles de horas |
| pers_admin_contable_direccion | Personal administrativo, contable y de dirección |
| pers_admin_contable_direccion_h | Personal administrativo, contable y de dirección, hombres |
| pers_admin_contable_direccion_m | Personal administrativo, contable y de dirección, mujeres |
| horas_pers_admin_contable_direccion_mh | Horas de personal administrativo, contable y de dirección en miles de horas |
| pers_no_dep_razon_social | Personal no dependiente de razón social |
| pers_no_dep_razon_social_h | Personal no dependiente de razón social, hombres |
| pers_no_dep_razon_social_m | Personal no dependiente de razón social, mujeres |
| horas_pers_no_dep_razon_social_mh | Horas de personal no dependiente de razón social en miles de horas |
| pers_contratado_otra_razon_social | Personal contratado de otra razón social |
| pers_contratado_otra_razon_social_h | Personal contratado de otra razón social, hombres |
| pers_contratado_otra_razon_social_m | Personal contratado de otra razón social, mujeres |
| horas_pers_contratado_otra_razon_social_mh | Horas de personal contratado de otra razón social en miles de horas |
| pers_honorarios | Personal por honorarios |
| pers_honorarios_h | Personal por honorarios, hombres |
| pers_honorarios_m | Personal por honorarios, mujeres |
| horas_pers_honorarios_mh | Horas de personal por honorarios en miles de horas |
| remuneraciones_tot_mdp | Total de remuneraciones en millones de pesos |
| salarios_pers_prod_ventas_servicios_mdp | Salarios de personal de producción, ventas y servicios en millones de pesos |
| sueldos_pers_admin_contable_direccion_mdp | Sueldos de personal administrativo, contable y de dirección en millones de pesos |
| contribuciones_seguridad_social_mdp | Contribuciones a seguridad social en millones de pesos |
| otras_prestaciones_sociales_mdp | Otras prestaciones sociales en millones de pesos |
| utilidades_repartidas_mdp | Utilidades repartidas en millones de pesos |
| indemnizacion_liquidacion_mdp | Indemnización y liquidación en millones de pesos |
| gastos_consu_tot_mdp | Total de gastos de consumo en millones de pesos |
| mercancias_compradas_reventa_mdp | Mercancías compradas para reventa en millones de pesos |
| materiales_servicios_mdp | Materiales y servicios en millones de pesos |
| materias_primas_mdp | Materias primas en millones de pesos |
| combustibles_lubricantes_energeticos_mdp | Combustibles, lubricantes y energéticos en millones de pesos |
| renta_alquiler_bienes_mdp | Renta y alquiler de bienes en millones de pesos |
| servicios_profesionales_mdp | Servicios profesionales en millones de pesos |
| maquila_servicios_produccion_mdp | Maquila y servicios de producción en millones de pesos |
| otros_bienes_servicios_mdp | Otros bienes y servicios en millones de pesos |
| fletes_productos_vendidos_mdp | Fletes de productos vendidos en millones de pesos |
| papeleria_oficina_mdp | Papelería de oficina en millones de pesos |
| energia_electrica_mdp | Energía eléctrica en millones de pesos |
| pagos_pers_subcontratado_mdp | Pagos a personal subcontratado en millones de pesos |
| honorarios_comisiones_mdp | Honorarios y comisiones en millones de pesos |
| publicidad_mdp | Publicidad en millones de pesos |
| servicios_comunicacion_mdp | Servicios de comunicación en millones de pesos |
| envases_empaques_mdp | Envases y empaques en millones de pesos |
| reparaciones_refacciones_mdp | Reparaciones y refacciones en millones de pesos |
| consu_agua_mdp | Consumo de agua en millones de pesos |
| ingr_tot_mdp | Total de ingresos en millones de pesos |
| ingr_reventa_mercancias_mdp | Ingresos por reventa de mercancías en millones de pesos |
| ingr_servicios_profesionales_mdp | Ingresos por servicios profesionales en millones de pesos |
| ingr_venta_productos_mdp | Ingresos por venta de productos en millones de pesos |
| ingr_alquiler_bienes_mdp | Ingresos por alquiler de bienes en millones de pesos |
| otros_ingr_mdp | Otros ingresos en millones de pesos |
| otros_componentes_prod_bruta_mdp | Otros componentes de la producción bruta en millones de pesos |
| ingr_maquila_terceros_mdp | Ingresos por maquila de terceros en millones de pesos |
| prod_bruta_tot_mdp | Producción bruta total en millones de pesos |
| consu_intermedio_mdp | Consumo intermedio en millones de pesos |
| valor_agregado_censal_bruto_mdp | Valor agregado censal bruto en millones de pesos |
| inversion_tot_mdp | Inversión total en millones de pesos |
| form_brut_cap_mdp | Formación bruta de capital en millones de pesos |
| mar_por_rev_mdp | Margen por reventa en millones de pesos |
| gastos_tot_mdp | Total de gastos en millones de pesos |
| ingr_tot_general_mdp | Total de ingresos general en millones de pesos |
| valor_productos_elaborados_mdp | Valor de productos elaborados en millones de pesos |
| act_fijos_uso_propio_mdp | Activos fijos de uso propio en millones de pesos |
| invent_inic_mdp | Inventario inicial en millones de pesos |
| invent_final_mdp | Inventario final en millones de pesos |
| var_exis_mdp | Variación de existencias en millones de pesos |
| invent_inic_proceso_mdp | Inventario inicial en proceso en millones de pesos |
| invent_final_proceso_mdp | Inventario final en proceso en millones de pesos |
| var_invent_proceso_mdp | Variación de inventario en proceso en millones de pesos |
| invent_inic_reventa_mdp | Inventario inicial para reventa en millones de pesos |
| invent_final_reventa_mdp | Inventario final para reventa en millones de pesos |
| acervo_act_fijos_mdp | Acervo de activos fijos en millones de pesos |
| depreciacion_act_fijos_mdp | Depreciación de activos fijos en millones de pesos |
| compra_act_fijos_mdp | Compra de activos fijos en millones de pesos |
| ventas_act_fijos_mdp | Ventas de activos fijos en millones de pesos |
| acervo_maquinaria_equipo_mdp | Acervo de maquinaria y equipo en millones de pesos |
| acervo_bienes_inmuebles_mdp | Acervo de bienes inmuebles en millones de pesos |
| acervo_unidades_transporte_mdp | Acervo de unidades de transporte en millones de pesos |
| acervo_equipo_computo_mdp | Acervo de equipo de cómputo en millones de pesos |
| acervo_mobiliario_oficina_mdp | Acervo de mobiliario de oficina en millones de pesos |
| cve_ent | Clave de entidad federativa (solo para estatal y municipal) |
| cve_mun | Clave de municipio (solo para municipal) |

## Fuentes

| Nivel | Archivo | Variable de entorno |
|-------|---------|---------------------|
| Nacional y Estatal | Censos Económicos 2019 | INEGI_CE_2019_NAC, INEGI_CE_2019_ESTATAL |
| Municipal | Censos Económicos 2019 | INEGI_CE_2019_MUNICIPAL |
| Nacional y Estatal | Censos Económicos 2024 | INEGI_CE_2024_NAC, INEGI_CE_2024_ESTATAL |
| Municipal | Censos Económicos 2024 | INEGI_CE_2024_MUNICIPAL |

Los datos se descargan directamente de INEGI mediante:
- `https://www.inegi.org.mx/contenidos/programas/ce/2019/Datosabiertos/ce2019_{slug}_csv.zip`
- `https://www.inegi.org.mx/contenidos/programas/ce/2024/datosabiertos/conjunto_de_datos_ce_{slug}_2024_csv.zip`

## Actualización

Los Censos Económicos se publican cada 5 años (2019, 2024, 2029, etc.). La carga es manual cuando INEGI publica nuevos datos. Incluye información económica agregada (unidades, empleo, remuneraciones, producción) a nivel nacional, estatal y municipal, con clasificación por actividad económica y estrato de personal ocupado.
