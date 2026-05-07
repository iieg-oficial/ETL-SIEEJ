PIPELINE_NAME = "pobreza_multidimensional"

# Nombre de la hoja del XLSX a procesar
EXCEL_SHEET = "Concentrado municipal"

# Filas a omitir al inicio (títulos, encabezados multi-nivel, filas en blanco)
# La primera fila de datos está en la fila 9 (1-based) → skiprows=8
EXCEL_SKIP_ROWS = 8

# Columnas a leer (0-based, cols 1-145 = fuente cols 2-146; col 0 siempre None)
EXCEL_USE_COLS = list(range(1, 146))

# Nombres de columnas en formato wide, en el mismo orden que EXCEL_USE_COLS
EXCEL_COL_NAMES: list[str] = [
    # Identificadores (cols fuente 2-5)
    "cve_ent",
    "nombre_ent",
    "cve_mun",
    "nombre_municipio",
    # Población por año (cols fuente 6-8)
    "poblacion_2010",
    "poblacion_2015",
    "poblacion_2020",
    # Pobreza (cols fuente 9-17)
    "pobreza_porcentaje_2010",
    "pobreza_porcentaje_2015",
    "pobreza_porcentaje_2020",
    "pobreza_personas_2010",
    "pobreza_personas_2015",
    "pobreza_personas_2020",
    "pobreza_promedio_2010",
    "pobreza_promedio_2015",
    "pobreza_promedio_2020",
    # Pobreza extrema (cols fuente 18-26)
    "pobreza_ext_porcentaje_2010",
    "pobreza_ext_porcentaje_2015",
    "pobreza_ext_porcentaje_2020",
    "pobreza_ext_personas_2010",
    "pobreza_ext_personas_2015",
    "pobreza_ext_personas_2020",
    "pobreza_ext_promedio_2010",
    "pobreza_ext_promedio_2015",
    "pobreza_ext_promedio_2020",
    # Pobreza moderada (cols fuente 27-35)
    "pobreza_mod_porcentaje_2010",
    "pobreza_mod_porcentaje_2015",
    "pobreza_mod_porcentaje_2020",
    "pobreza_mod_personas_2010",
    "pobreza_mod_personas_2015",
    "pobreza_mod_personas_2020",
    "pobreza_mod_promedio_2010",
    "pobreza_mod_promedio_2015",
    "pobreza_mod_promedio_2020",
    # Vulnerables por carencia social (cols fuente 36-44)
    "vul_carencia_porcentaje_2010",
    "vul_carencia_porcentaje_2015",
    "vul_carencia_porcentaje_2020",
    "vul_carencia_personas_2010",
    "vul_carencia_personas_2015",
    "vul_carencia_personas_2020",
    "vul_carencia_promedio_2010",
    "vul_carencia_promedio_2015",
    "vul_carencia_promedio_2020",
    # Vulnerables por ingreso (cols fuente 45-50) — sin carencias_promedio
    "vul_ingreso_porcentaje_2010",
    "vul_ingreso_porcentaje_2015",
    "vul_ingreso_porcentaje_2020",
    "vul_ingreso_personas_2010",
    "vul_ingreso_personas_2015",
    "vul_ingreso_personas_2020",
    # No pobre y no vulnerable (cols fuente 51-56) — sin carencias_promedio
    "no_pobre_porcentaje_2010",
    "no_pobre_porcentaje_2015",
    "no_pobre_porcentaje_2020",
    "no_pobre_personas_2010",
    "no_pobre_personas_2015",
    "no_pobre_personas_2020",
    # Rezago educativo (cols fuente 57-65)
    "rez_edu_porcentaje_2010",
    "rez_edu_porcentaje_2015",
    "rez_edu_porcentaje_2020",
    "rez_edu_personas_2010",
    "rez_edu_personas_2015",
    "rez_edu_personas_2020",
    "rez_edu_promedio_2010",
    "rez_edu_promedio_2015",
    "rez_edu_promedio_2020",
    # Carencia acceso servicios de salud (cols fuente 66-74)
    "car_salud_porcentaje_2010",
    "car_salud_porcentaje_2015",
    "car_salud_porcentaje_2020",
    "car_salud_personas_2010",
    "car_salud_personas_2015",
    "car_salud_personas_2020",
    "car_salud_promedio_2010",
    "car_salud_promedio_2015",
    "car_salud_promedio_2020",
    # Carencia acceso seguridad social (cols fuente 75-83)
    "car_seg_soc_porcentaje_2010",
    "car_seg_soc_porcentaje_2015",
    "car_seg_soc_porcentaje_2020",
    "car_seg_soc_personas_2010",
    "car_seg_soc_personas_2015",
    "car_seg_soc_personas_2020",
    "car_seg_soc_promedio_2010",
    "car_seg_soc_promedio_2015",
    "car_seg_soc_promedio_2020",
    # Carencia calidad y espacios de vivienda (cols fuente 84-92)
    "car_viv_porcentaje_2010",
    "car_viv_porcentaje_2015",
    "car_viv_porcentaje_2020",
    "car_viv_personas_2010",
    "car_viv_personas_2015",
    "car_viv_personas_2020",
    "car_viv_promedio_2010",
    "car_viv_promedio_2015",
    "car_viv_promedio_2020",
    # Carencia servicios básicos de la vivienda (cols fuente 93-101)
    "car_sbv_porcentaje_2010",
    "car_sbv_porcentaje_2015",
    "car_sbv_porcentaje_2020",
    "car_sbv_personas_2010",
    "car_sbv_personas_2015",
    "car_sbv_personas_2020",
    "car_sbv_promedio_2010",
    "car_sbv_promedio_2015",
    "car_sbv_promedio_2020",
    # Carencia acceso a la alimentación (cols fuente 102-110)
    "car_ali_porcentaje_2010",
    "car_ali_porcentaje_2015",
    "car_ali_porcentaje_2020",
    "car_ali_personas_2010",
    "car_ali_personas_2015",
    "car_ali_personas_2020",
    "car_ali_promedio_2010",
    "car_ali_promedio_2015",
    "car_ali_promedio_2020",
    # Al menos una carencia social (cols fuente 111-119)
    "al_1_car_porcentaje_2010",
    "al_1_car_porcentaje_2015",
    "al_1_car_porcentaje_2020",
    "al_1_car_personas_2010",
    "al_1_car_personas_2015",
    "al_1_car_personas_2020",
    "al_1_car_promedio_2010",
    "al_1_car_promedio_2015",
    "al_1_car_promedio_2020",
    # Tres o más carencias sociales (cols fuente 120-128)
    "tres_mas_car_porcentaje_2010",
    "tres_mas_car_porcentaje_2015",
    "tres_mas_car_porcentaje_2020",
    "tres_mas_car_personas_2010",
    "tres_mas_car_personas_2015",
    "tres_mas_car_personas_2020",
    "tres_mas_car_promedio_2010",
    "tres_mas_car_promedio_2015",
    "tres_mas_car_promedio_2020",
    # Ingreso < línea de pobreza (cols fuente 129-137)
    "lpi_porcentaje_2010",
    "lpi_porcentaje_2015",
    "lpi_porcentaje_2020",
    "lpi_personas_2010",
    "lpi_personas_2015",
    "lpi_personas_2020",
    "lpi_promedio_2010",
    "lpi_promedio_2015",
    "lpi_promedio_2020",
    # Ingreso < línea de pobreza extrema (cols fuente 138-146)
    "lpei_porcentaje_2010",
    "lpei_porcentaje_2015",
    "lpei_porcentaje_2020",
    "lpei_personas_2010",
    "lpei_personas_2015",
    "lpei_personas_2020",
    "lpei_promedio_2010",
    "lpei_promedio_2015",
    "lpei_promedio_2020",
]

# Años disponibles en la fuente
DATA_YEARS: list[int] = [2010, 2015, 2020]

# Prefijos de indicadores y si tienen columna car_prom en la fuente
# Tupla: (prefijo, tiene_car_prom)
INDICATOR_PREFIXES: list[tuple[str, bool]] = [
    ("pobreza", True),
    ("pobreza_ext", True),
    ("pobreza_mod", True),
    ("vul_carencia", True),
    ("vul_ingreso", False),
    ("no_pobre", False),
    ("rez_edu", True),
    ("car_salud", True),
    ("car_seg_soc", True),
    ("car_viv", True),
    ("car_sbv", True),
    ("car_ali", True),
    ("al_1_car", True),
    ("tres_mas_car", True),
    ("lpi", True),
    ("lpei", True),
]

# Valores que se tratan como nulo en la fuente
NULL_VALUES: list[str] = ["N/A", "NA", "n/a", "nan", ""]
