REFRESH_GOLD = "REFRESH MATERIALIZED VIEW vw_gold_delitos_fuero_comun;"

_SECRETARIADO_VIEWS = [
    "vwm_datos_delitos_abuso_sexual_secretariado",
    "vwm_datos_delitos_feminicidio_secretariado",
    "vwm_datos_delitos_homicidio_doloso_secretariado",
    "vwm_datos_delitos_lesiones_dolosas_secretariado",
    "vwm_datos_delitos_robo_autopartes_secretariado",
    "vwm_datos_delitos_robo_casa_habitacion_secretariado",
    "vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado",
    "vwm_datos_delitos_robo_institucion_bancaria_secretariado",
    "vwm_datos_delitos_robo_motocicleta_secretariado",
    "vwm_datos_delitos_robo_negocio_secretariado",
    "vwm_datos_delitos_robo_transeunte_via_publica_secretariado",
    "vwm_datos_delitos_robo_transportista_secretariado",
    "vwm_datos_delitos_violacion_secretariado",
    "vwm_datos_delitos_violencia_familiar_secretariado",
    "vwm_datos_delitos_violencia_genero_no_familiar_secretariado",
]

REFRESH_SECRETARIADO = [f"REFRESH MATERIALIZED VIEW {v};" for v in _SECRETARIADO_VIEWS]
