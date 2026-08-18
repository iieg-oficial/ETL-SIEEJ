"""Qué DAG corre cuándo. Solo datos: ver docs/airflow.md para elegir horario.

Los DAGs bootstrap no están aquí: declaran `schedule=None` y corren bajo demanda.
"""

from typing import Final

from core.schedules.policy import Schedule

SCHEDULES: Final[dict[str, Schedule]] = {
    "etl_emec_update": Schedule("emec", "0 0 1 * *", "cada mes, el día 1"),
    "etl_emim_update": Schedule("emim", "0 0 1 * *", "cada mes, el día 1"),
    "etl_ems_update": Schedule("ems", "0 0 1 * *", "cada mes, el día 1"),
    "etl_enec_update": Schedule("enec", "0 0 1 * *", "cada mes, el día 1"),
    "etl_establecimientos_de_salud_update": Schedule("establecimientos_de_salud", "0 0 1 * *", "cada mes, el día 1"),
    "etl_fiscalia_update": Schedule("fiscalia", "0 0 1 * *", "cada mes, el día 1"),
    "etl_inpc_update": Schedule("inpc", "0 0 1 * *", "cada mes, el día 1"),
    "etl_rastros_update": Schedule("rastros", "0 0 1 * *", "cada mes, el día 1"),
    "etl_repd_update": Schedule("repd", "0 3 1 * *", "cada mes, el día 1"),
    "etl_delitos_fuero_comun_update": Schedule("delitos_fuero_comun", "0 12 1 * *", "cada mes, el día 1"),
    "etl_datamexico_update": Schedule("datamexico", "0 8 1 */3 *", "cada 3 meses, el día 1"),
    "etl_etef_update": Schedule("etef", "0 0 1 */3 *", "cada 3 meses, el día 1"),
    "etl_agropecuario_siap_update": Schedule("agropecuario_siap", "0 0 1 1 *", "cada año, el 1 de enero"),
    "etl_nacimientos_dgis_update": Schedule("nacimientos_dgis", "0 0 1 1 *", "cada año, el 1 de enero"),
    "etl_produccion_ganadera_update": Schedule("produccion_ganadera", "0 0 1 1 *", "cada año, el 1 de enero"),
    "etl_ilmm_update": Schedule("ilmm", "0 0 1 6 *", "cada año, el 1 de junio"),
    "etl_defunciones_update": Schedule("defunciones", "0 4 1 7 *", "cada año, el 1 de julio"),
    "etl_enoe_microdatos_incremental": Schedule("enoe_microdatos", "0 0 10 3,6,9,12 *", "cada 3 meses, el día 10"),
    "etl_enoe_update": Schedule("enoe", "0 3 10 3,6,9,12 *", "cada 3 meses, el día 10"),
    "etl_asg_imss_update": Schedule("asg_imss", "0 12 10 * *", "cada mes, el día 10"),
}


def schedule_for(dag_id: str) -> str:
    try:
        return SCHEDULES[dag_id].cron
    except KeyError:
        raise KeyError(f"{dag_id} no está registrado en core/schedules/registry.py. Ver docs/airflow.md.") from None
