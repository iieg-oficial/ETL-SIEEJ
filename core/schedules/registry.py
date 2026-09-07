"""Cronógrama de los DAGs. Para elegir horario ver: docs/airflow.md."""

from typing import Final

from core.schedules.policy import Schedule

# Un DAG por hora en el día 1, para que mensuales, trimestrales y anuales que
# caen en la misma fecha no compartan instante.
SCHEDULES: Final[dict[str, Schedule]] = {
    "etl_emec_update": Schedule("emec", "0 0 1 * *", "cada mes, el día 1"),
    "etl_emim_update": Schedule("emim", "0 1 1 * *", "cada mes, el día 1"),
    "etl_ems_update": Schedule("ems", "0 2 1 * *", "cada mes, el día 1"),
    "etl_repd_update": Schedule("repd", "0 3 1 * *", "cada mes, el día 1"),
    "etl_enec_update": Schedule("enec", "0 4 1 * *", "cada mes, el día 1"),
    "etl_establecimientos_de_salud_update": Schedule("establecimientos_de_salud", "0 5 1 * *", "cada mes, el día 1"),
    "etl_fiscalia_update": Schedule("fiscalia", "0 6 1 * *", "cada mes, el día 1"),
    "etl_inpc_update": Schedule("inpc", "0 7 1 * *", "cada mes, el día 1"),
    "etl_datamexico_update": Schedule("datamexico", "0 8 1 */3 *", "cada 3 meses, el día 1"),
    "etl_rastros_update": Schedule("rastros", "0 9 1 * *", "cada mes, el día 1"),
    "etl_etef_update": Schedule("etef", "0 10 1 */3 *", "cada 3 meses, el día 1"),
    "etl_denue_update": Schedule("denue", "0 11 11 * *", "cada mes, el día 11"),
    "etl_delitos_fuero_comun_update": Schedule("delitos_fuero_comun", "0 12 1 * *", "cada mes, el día 1"),
    "etl_agropecuario_siap_update": Schedule("agropecuario_siap", "0 13 1 1 *", "cada año, el 1 de enero"),
    "etl_nacimientos_dgis_update": Schedule("nacimientos_dgis", "0 14 1 1 *", "cada año, el 1 de enero"),
    "etl_produccion_ganadera_update": Schedule("produccion_ganadera", "0 15 1 1 *", "cada año, el 1 de enero"),
    "etl_ilmm_update": Schedule("ilmm", "0 16 1 6 *", "cada año, el 1 de junio"),
    "etl_defunciones_update": Schedule("defunciones", "0 17 1 7 *", "cada año, el 1 de julio"),
    "etl_defunciones_inegi_update": Schedule("defunciones_inegi", "0 18 1 12 *", "cada año, el 1 de diciembre"),
    "etl_enoe_microdatos_incremental": Schedule("enoe_microdatos", "0 0 10 3,6,9,12 *", "cada 3 meses, el día 10"),
    "etl_enoe_update": Schedule("enoe", "0 3 10 3,6,9,12 *", "cada 3 meses, el día 10"),
    "etl_asg_imss_update": Schedule("asg_imss", "0 12 10 * *", "cada mes, el día 10"),
}


def schedule_for(dag_id: str) -> str:
    try:
        return SCHEDULES[dag_id].cron
    except KeyError:
        raise KeyError(f"{dag_id} no está registrado en core/schedules/registry.py. Ver docs/airflow.md.") from None
