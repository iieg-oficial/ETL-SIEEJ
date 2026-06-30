from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.censos_economicos.attributes import CensosEconomicosTablesN as T


class CensosEconomicosBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class CatCensos(CensosEconomicosBase):
    __tablename__ = T.CAT_CENSOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    anio: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_publicacion: Mapped[date] = mapped_column(Date, nullable=False)
    fuente: Mapped[str | None] = mapped_column(Text, nullable=True)


class CatClasificadoresCodigos(CensosEconomicosBase):
    __tablename__ = T.CAT_CLASIFICADORES_CODIGOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    clasificador: Mapped[str] = mapped_column(Text, nullable=False)


class CatActividadesEconomicas(CensosEconomicosBase):
    __tablename__ = T.CAT_ACTIVIDADES_ECONOMICAS
    __table_args__ = (
        UniqueConstraint(
            "codigo",
            "codigo_id",
            "censo_id",
            name="uq_actividad_codigo_clas_censo",
            postgresql_nulls_not_distinct=True,
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    censo_id: Mapped[int] = mapped_column(ForeignKey(f"{T.CAT_CENSOS}.id"), nullable=False)
    codigo: Mapped[str | None] = mapped_column(Text, nullable=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    codigo_id: Mapped[int] = mapped_column(ForeignKey(f"{T.CAT_CLASIFICADORES_CODIGOS}.id"), nullable=False)


class CatEstratos(CensosEconomicosBase):
    __tablename__ = T.CAT_ESTRATOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    codigo: Mapped[int | None] = mapped_column(Integer, nullable=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)


class StgEconomicoBase(CensosEconomicosBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    censo_id: Mapped[int] = mapped_column(ForeignKey(f"{T.CAT_CENSOS}.id"), nullable=False)
    actividad_economica_id: Mapped[int | None] = mapped_column(
        ForeignKey(f"{T.CAT_ACTIVIDADES_ECONOMICAS}.id"), nullable=True
    )
    estrato_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.CAT_ESTRATOS}.id"), nullable=True)


class StgEconomico2018Base(StgEconomicoBase):
    __abstract__ = True

    unidades_economicas: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_ocupado_tot: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_ocupado_tot_h: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_ocupado_tot_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_pers_ocupado_tot_mh: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_dep_razon_social: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_dep_razon_social_h: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_dep_razon_social_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_pers_dep_razon_social_mh: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_remu: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_remu_h: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_remu_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_pers_remu_mh: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_no_remu: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_no_remu_h: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_no_remu_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_pers_no_remu_mh: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_prod_ventas_servicios: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_prod_ventas_servicios_h: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_prod_ventas_servicios_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_pers_prod_ventas_servicios_mh: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_admin_contable_direccion: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_admin_contable_direccion_h: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_admin_contable_direccion_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_pers_admin_contable_direccion_mh: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_no_dep_razon_social: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_no_dep_razon_social_h: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_no_dep_razon_social_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_pers_no_dep_razon_social_mh: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_contratado_otra_razon_social: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_contratado_otra_razon_social_h: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_contratado_otra_razon_social_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_pers_contratado_otra_razon_social_mh: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_honorarios: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_honorarios_h: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_honorarios_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_pers_honorarios_mh: Mapped[float | None] = mapped_column(Float, nullable=True)
    remuneraciones_tot_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    salarios_pers_prod_ventas_servicios_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    sueldos_pers_admin_contable_direccion_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    contribuciones_seguridad_social_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    otras_prestaciones_sociales_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    utilidades_repartidas_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    indemnizacion_liquidacion_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    gastos_consu_tot_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    mercancias_compradas_reventa_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    materiales_servicios_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    materias_primas_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    combustibles_lubricantes_energeticos_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    renta_alquiler_bienes_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    servicios_profesionales_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    maquila_servicios_produccion_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    otros_bienes_servicios_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    fletes_productos_vendidos_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    papeleria_oficina_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    energia_electrica_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    pagos_pers_subcontratado_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    honorarios_comisiones_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    publicidad_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    servicios_comunicacion_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    envases_empaques_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    reparaciones_refacciones_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    consu_agua_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    ingr_tot_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    ingr_reventa_mercancias_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    ingr_servicios_profesionales_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    ingr_venta_productos_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    ingr_alquiler_bienes_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    otros_ingr_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    otros_componentes_prod_bruta_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    ingr_maquila_terceros_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    prod_bruta_tot_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    consu_intermedio_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    valor_agregado_censal_bruto_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    inversion_tot_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    form_brut_cap_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    mar_por_rev_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    gastos_tot_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    ingr_tot_general_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    valor_productos_elaborados_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    act_fijos_uso_propio_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    invent_inic_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    invent_final_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    var_exis_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    invent_inic_proceso_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    invent_final_proceso_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    var_invent_proceso_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    invent_inic_reventa_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    invent_final_reventa_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    acervo_act_fijos_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    depreciacion_act_fijos_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    compra_act_fijos_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    ventas_act_fijos_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    acervo_maquinaria_equipo_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    acervo_bienes_inmuebles_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    acervo_unidades_transporte_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    acervo_equipo_computo_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    acervo_mobiliario_oficina_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_bienes_elab_gen_ext_pbt: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_imatmpp: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_act_fijos_producidos_uso_propio_pb: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_var_exist_prod_proceso_pbt: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_mar_rev_merc_pbt: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_serv_prof_cient_tec_pbt: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_ingr_abmi_produccion: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_otros_comp_pbt: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_ssen_tr: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_salarios_ppvs_tr: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_sueldos_pers_acd_tr: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_dependiente_pers_ocup_tot_porcentaje: Mapped[float | None] = mapped_column(Float, nullable=True)
    pnr_perasonal_ocupado_tot: Mapped[float | None] = mapped_column(Float, nullable=True)
    pnr_po_dependiente: Mapped[float | None] = mapped_column(Float, nullable=True)
    prest_soc_util_rep_tot_rem: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_urt_tr: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_mt_pers_remu: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_mt_po_produccion_ventas_servicios: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_mt_po_acd: Mapped[float | None] = mapped_column(Float, nullable=True)
    prest_soc_tot_rem: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_prestaciones_sociales_utilidades_sueldos_salarios: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_mt_pfotn: Mapped[float | None] = mapped_column(Float, nullable=True)
    tot_prestaciones_ss: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_mt_pcpor: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_mt_phcs: Mapped[float | None] = mapped_column(Float, nullable=True)
    remuneracion_media_per_ocupada_remu: Mapped[float | None] = mapped_column(Float, nullable=True)
    salario_pers_operativo_anual: Mapped[float | None] = mapped_column(Float, nullable=True)
    sueldo_pers_administrativo_anual: Mapped[float | None] = mapped_column(Float, nullable=True)
    pagos_promedio_per_suministrada: Mapped[float | None] = mapped_column(Float, nullable=True)
    pagos_promedio_pers_comisiones_u_honorarios: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_remuneraciones_gcbs: Mapped[float | None] = mapped_column(Float, nullable=True)
    per_no_dep_pers_ocup_tot: Mapped[float | None] = mapped_column(Float, nullable=True)
    indem_liqui_remu_tot: Mapped[float | None] = mapped_column(Float, nullable=True)
    remuneracion_media_per_remu: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_dia_trab_prom_pers_remu: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_dia_trab_prom_pers_no_remu: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_dia_trab_prom_ppvs: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_dia_trab_prom_empleados_administrativos_control: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_dia_trab_prom_pers_comisiones_honorarios: Mapped[float | None] = mapped_column(Float, nullable=True)
    valor_agregado_censal_bruto_pbt: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_consu_intermedio_pbt: Mapped[float | None] = mapped_column(Float, nullable=True)
    va_promedio_per_ocupada: Mapped[float | None] = mapped_column(Float, nullable=True)
    pbt_pers_ocupado_tot: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_mpms_gastos_consu_bienes: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_mcs_gcbs: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_cae_gcbs: Mapped[float | None] = mapped_column(Float, nullable=True)
    inversion_ti_tot: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_gastos_consu_otros_bienes_servicios_gastos_consu: Mapped[float | None] = mapped_column(Float, nullable=True)
    inversion_tot_act_fijos: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_ivm_ti_suministro_bienes: Mapped[float | None] = mapped_column(Float, nullable=True)
    inversion_tot_valor_agregado_censal_bruto: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_servi_prof_cient: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_otros_isbs_ti: Mapped[float | None] = mapped_column(Float, nullable=True)
    inversion_tot_pbt: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_venta_productos_elaborados_generados_o_extraidos_tot: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    part_ingr_abmi_tot: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_imatmpp_2: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_mep_tot_act_fijos: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_cif_tot_act_fijos: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_et_tot_act_fijos: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_ecp_tot_act_fijos: Mapped[float | None] = mapped_column(Float, nullable=True)
    margen_bruto_operacion: Mapped[float | None] = mapped_column(Float, nullable=True)
    ing_princ_por_sum_bienes: Mapped[float | None] = mapped_column(Float, nullable=True)
    gp_gcbs: Mapped[float | None] = mapped_column(Float, nullable=True)
    gp_ip: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_meo_otros_act_fijos_tot: Mapped[float | None] = mapped_column(Float, nullable=True)
    valor_act_fijos_per_ocupada: Mapped[float | None] = mapped_column(Float, nullable=True)
    maqui_equip_prod_a_prod_tot: Mapped[float | None] = mapped_column(Float, nullable=True)
    acti_fijo_brut_tot: Mapped[float | None] = mapped_column(Float, nullable=True)
    forma_brut_cap_fijo_acervo_tot: Mapped[float | None] = mapped_column(Float, nullable=True)
    produccion_act_fijos_uso_propio_compras_act_fijos: Mapped[float | None] = mapped_column(Float, nullable=True)
    otros_isbs_ti_suministro: Mapped[float | None] = mapped_column(Float, nullable=True)
    gastos_no_derivados_actividad_gcbs: Mapped[float | None] = mapped_column(Float, nullable=True)
    ingr_no_derivados_actividad_isbs: Mapped[float | None] = mapped_column(Float, nullable=True)
    valor_promedio_maquinaria_equipo_per_ocupada_anuales: Mapped[float | None] = mapped_column(Float, nullable=True)
    ip_respecto_gp: Mapped[float | None] = mapped_column(Float, nullable=True)
    porcentaje_ip_ti_actividad_financieros: Mapped[float | None] = mapped_column(Float, nullable=True)
    isbs_per_ocupada: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_depreciacion_valor_act_fijos: Mapped[float | None] = mapped_column(Float, nullable=True)
    tasa_rentabilidad_promedio: Mapped[float | None] = mapped_column(Float, nullable=True)
    salario_promedio_diarios_per_operativa: Mapped[float | None] = mapped_column(Float, nullable=True)
    sueldo_promedio_diario_per_administrativa: Mapped[float | None] = mapped_column(Float, nullable=True)
    va_tot_act_fijos: Mapped[float | None] = mapped_column(Float, nullable=True)
    part_muje_pers_ocupado_tot: Mapped[float | None] = mapped_column(Float, nullable=True)


class StgEconomico2023Base(StgEconomicoBase):
    __abstract__ = True

    sector: Mapped[str | None] = mapped_column(Text, nullable=True)
    subsector: Mapped[str | None] = mapped_column(Text, nullable=True)
    rama: Mapped[str | None] = mapped_column(Text, nullable=True)
    subrama: Mapped[str | None] = mapped_column(Text, nullable=True)
    clase: Mapped[str | None] = mapped_column(Text, nullable=True)
    unidades_economicas: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_ocupado_tot: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_ocupado_tot_h: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_ocupado_tot_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_pers_ocupado_tot_mh: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_dep_razon_social: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_dep_razon_social_h: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_dep_razon_social_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_pers_dep_razon_social_mh: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_remu: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_remu_h: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_remu_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_pers_remu_mh: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_no_remu: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_no_remu_h: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_no_remu_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_pers_no_remu_mh: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_prod_ventas_servicios: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_prod_ventas_servicios_h: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_prod_ventas_servicios_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_pers_prod_ventas_servicios_mh: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_admin_contable_direccion: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_admin_contable_direccion_h: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_admin_contable_direccion_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_pers_admin_contable_direccion_mh: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_no_dep_razon_social: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_no_dep_razon_social_h: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_no_dep_razon_social_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_pers_no_dep_razon_social_mh: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_contratado_otra_razon_social: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_contratado_otra_razon_social_h: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_contratado_otra_razon_social_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_pers_contratado_otra_razon_social_mh: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_honorarios: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_honorarios_h: Mapped[float | None] = mapped_column(Float, nullable=True)
    pers_honorarios_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_pers_honorarios_mh: Mapped[float | None] = mapped_column(Float, nullable=True)
    remuneraciones_tot_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    salarios_pers_prod_ventas_servicios_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    sueldos_pers_admin_contable_direccion_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    contribuciones_seguridad_social_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    otras_prestaciones_sociales_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    utilidades_repartidas_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    indemnizacion_liquidacion_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    gastos_consu_tot_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    mercancias_compradas_reventa_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    materiales_servicios_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    materias_primas_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    combustibles_lubricantes_energeticos_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    renta_alquiler_bienes_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    servicios_profesionales_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    maquila_servicios_produccion_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    otros_bienes_servicios_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    fletes_productos_vendidos_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    papeleria_oficina_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    energia_electrica_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    pagos_pers_subcontratado_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    honorarios_comisiones_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    publicidad_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    servicios_comunicacion_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    envases_empaques_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    reparaciones_refacciones_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    consu_agua_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    ingr_tot_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    ingr_reventa_mercancias_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    ingr_servicios_profesionales_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    ingr_venta_productos_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    ingr_alquiler_bienes_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    otros_ingr_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    otros_componentes_prod_bruta_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    ingr_maquila_terceros_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    prod_bruta_tot_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    consu_intermedio_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    valor_agregado_censal_bruto_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    inversion_tot_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    form_brut_cap_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    mar_por_rev_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    gastos_tot_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    ingr_tot_general_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    valor_productos_elaborados_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    act_fijos_uso_propio_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    invent_inic_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    invent_final_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    var_exis_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    invent_inic_proceso_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    invent_final_proceso_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    var_invent_proceso_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    invent_inic_reventa_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    invent_final_reventa_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    acervo_act_fijos_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    depreciacion_act_fijos_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    compra_act_fijos_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    ventas_act_fijos_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    acervo_maquinaria_equipo_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    acervo_bienes_inmuebles_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    acervo_unidades_transporte_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    acervo_equipo_computo_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)
    acervo_mobiliario_oficina_mdp: Mapped[float | None] = mapped_column(Float, nullable=True)


class StgEconomicoNacional2018(StgEconomico2018Base):
    __tablename__ = T.STG_ECONOMICO_NACIONAL_2018


class StgEconomicoEstatal2018(StgEconomico2018Base):
    __tablename__ = T.STG_ECONOMICO_ESTATAL_2018

    cve_ent: Mapped[int] = mapped_column(Integer, nullable=False)


class StgEconomicoMunicipal2018(StgEconomico2018Base):
    __tablename__ = T.STG_ECONOMICO_MUNICIPAL_2018

    cve_ent: Mapped[int] = mapped_column(Integer, nullable=False)
    cve_mun: Mapped[int] = mapped_column(Integer, nullable=False)


class StgEconomicoNacional2023(StgEconomico2023Base):
    __tablename__ = T.STG_ECONOMICO_NACIONAL_2023


class StgEconomicoEstatal2023(StgEconomico2023Base):
    __tablename__ = T.STG_ECONOMICO_ESTATAL_2023

    cve_ent: Mapped[int] = mapped_column(Integer, nullable=False)


class StgEconomicoMunicipal2023(StgEconomico2023Base):
    __tablename__ = T.STG_ECONOMICO_MUNICIPAL_2023

    cve_ent: Mapped[int] = mapped_column(Integer, nullable=False)
    cve_mun: Mapped[int] = mapped_column(Integer, nullable=False)
