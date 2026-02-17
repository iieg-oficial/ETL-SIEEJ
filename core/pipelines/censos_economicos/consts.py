PIPELINE_NAME = "censos_economicos"

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

# Configuracion por anio: plantillas URL, patrones de archivo, rutas de catalogos
# Para agregar un anio censal, agregar una entrada con todos los campos autocontenidos.
CE_YEARS_CONFIG: dict[int, dict] = {
    2024: {
        "url_template": (
            "https://www.inegi.org.mx/contenidos/programas/ce/2024/"
            "datosabiertos/conjunto_de_datos_ce_{slug}_2024_csv.zip"
        ),
        "slugs": {
            "nac": "nac",
            "01": "ags",
            "02": "bc",
            "03": "bcs",
            "04": "camp",
            "05": "coah",
            "06": "col",
            "07": "chis",
            "08": "chih",
            "09": "cdmx",
            "10": "dgo",
            "11": "gto",
            "12": "gro",
            "13": "hgo",
            "14": "jal",
            "15": "mex",
            "16": "mich",
            "17": "mor",
            "18": "nay",
            "19": "nl",
            "20": "oax",
            "21": "pue",
            "22": "qro",
            "23": "qroo",
            "24": "slp",
            "25": "sin",
            "26": "son",
            "27": "tab",
            "28": "tamps",
            "29": "tlax",
            "30": "ver",
            "31": "yuc",
            "32": "zac",
        },
        "data_csv_pattern": "conjunto_de_datos/tr_ce_{slug}_2024.csv",
        "catalog_actividad": "catalogos/tc_codigo_actividad.csv",
        "catalog_entidad_municipio": "catalogos/tc_entidad_municipio.csv",
        "catalog_estrato": "catalogos/tc_estrato_ce2024.csv",
        "diccionario": "diccionario_de_datos/diccionario_de_datos_ce2024.csv",
    },
}

# Clasificacion de tipo de archivo segun rutas internas del ZIP
FILE_TYPE_MAP: dict[str, str] = {
    "conjunto_de_datos": "data",
    "catalogos/tc_codigo_actividad": "catalogo_actividad",
    "catalogos/tc_entidad_municipio": "catalogo_entidad_municipio",
    "catalogos/tc_estrato": "catalogo_estrato",
    "diccionario_de_datos": "diccionario",
}


def classify_file_type(filename: str) -> str:
    """Determina el tipo de archivo a partir de la ruta interna del ZIP."""
    for prefix, file_type in FILE_TYPE_MAP.items():
        if filename.startswith(prefix):
            return file_type
    return "other"


# Columnas clave - cadena vacia '' cuando estan ausentes (no NULL) para soportar restriccion unica
KEY_COLUMNS = ["e03", "e04", "codigo", "id_estrato"]

# Columnas de jerarquia de clasificacion SCIAN (nulables)
CLASSIFICATION_COLUMNS = ["sector", "subsector", "rama", "subrama", "clase"]

# 98 columnas de variables economicas (Float, nulables - NULL = dato confidencial suprimido por INEGI)
# Descripciones cortas extraidas del diccionario de datos INEGI (diccionario_de_datos_ce2024.csv)
CE_ECONOMIC_COLUMNS: dict[str, str] = {
    "ue": "Unidades económicas",
    "h001a": "Personal ocupado total",
    "h000a": "Personal dependiente de la razón social total",
    "h010a": "Personal remunerado total",
    "h020a": "Personas propietarias, familiares y otro personal no remunerado total",
    "i000a": "Personal no dependiente de la razón social total",
    "j000a": "Total de remuneraciones (millones de pesos)",
    "k000a": "Total de gastos por consumo de bienes y servicios (millones de pesos)",
    "m000a": "Total de ingresos por suministro de bienes y servicios (millones de pesos)",
    "a111a": "Producción bruta total (millones de pesos)",
    "a121a": "Consumo intermedio (millones de pesos)",
    "a131a": "Valor agregado censal bruto (millones de pesos)",
    "a211a": "Inversión total (millones de pesos)",
    "a221a": "Formación bruta de capital fijo (millones de pesos)",
    "p000c": "Variación total de existencias (millones de pesos)",
    "q000a": "Acervo total de activos fijos (millones de pesos)",
    "q000b": "Depreciación total de activos fijos (millones de pesos)",
    "a700a": "Total de gastos (millones de pesos)",
    "a800a": "Total de ingresos (millones de pesos)",
    "q000c": "Compra y adquisición total de activos fijos y reformas mayores (millones de pesos)",
    "q000d": "Ventas totales de activos fijos (millones de pesos)",
    "p000a": "Total de inventario inicial (millones de pesos)",
    "p000b": "Total de inventario final (millones de pesos)",
    "o010a": "Valor de productos elaborados, bienes generados y extraídos (millones de pesos)",
    "o020a": "Activos fijos producidos para uso propio (millones de pesos)",
    "m700a": "Ingresos por maquilar o transformar materias primas propiedad de terceros (millones de pesos)",
    "p030c": "Variación de inventarios de productos en proceso (millones de pesos)",
    "a511a": "Margen por reventa de mercancías (millones de pesos)",
    "m020a": "Ingresos por prestación de servicios profesionales, científicos y técnicos (millones de pesos)",
    "m050a": "Ingresos por alquiler de bienes muebles e inmuebles (millones de pesos)",
    "m091a": "Otros componentes de la producción bruta total (millones de pesos)",
    "h001b": "Personal ocupado total, hombres",
    "h001c": "Personal ocupado total, mujeres",
    "h001d": "Horas trabajadas por personal ocupado total (miles de horas)",
    "h000b": "Personal dependiente de la razón social, hombres",
    "h000c": "Personal dependiente de la razón social, mujeres",
    "h000d": "Horas trabajadas por personal dependiente de la razón social (miles de horas)",
    "h010b": "Personal remunerado, hombres",
    "h010c": "Personal remunerado, mujeres",
    "h010d": "Horas trabajadas por personal remunerado (miles de horas)",
    "h101a": "Personal de producción, ventas y servicios total",
    "h101b": "Personal de producción, ventas y servicios, hombres",
    "h101c": "Personal de producción, ventas y servicios, mujeres",
    "h101d": "Horas trabajadas por personal de producción, ventas y servicios (miles de horas)",
    "h203a": "Personal administrativo, contable y de dirección total",
    "h203b": "Personal administrativo, contable y de dirección, hombres",
    "h203c": "Personal administrativo, contable y de dirección, mujeres",
    "h203d": "Horas trabajadas por personal administrativo, contable y de dirección (miles de horas)",
    "h020b": "Personas propietarias, familiares y otro personal no remunerado, hombres",
    "h020c": "Personas propietarias, familiares y otro personal no remunerado, mujeres",
    "h020d": "Horas trabajadas por personas propietarias, familiares y otro personal no remunerado (miles de horas)",
    "i000b": "Personal no dependiente de la razón social, hombres",
    "i000c": "Personal no dependiente de la razón social, mujeres",
    "i000d": "Horas trabajadas por personal no dependiente de la razón social (miles de horas)",
    "i100a": "Personal contratado y proporcionado por otra razón social total",
    "i100b": "Personal contratado y proporcionado por otra razón social, hombres",
    "i100c": "Personal contratado y proporcionado por otra razón social, mujeres",
    "i100d": "Horas trabajadas por personal contratado y proporcionado por otra razón social (miles de horas)",
    "i200a": "Personal por honorarios o comisiones sin sueldo o salario fijo total",
    "i200b": "Personal por honorarios o comisiones sin sueldo o salario fijo, hombres",
    "i200c": "Personal por honorarios o comisiones sin sueldo o salario fijo, mujeres",
    "i200d": "Horas trabajadas por personal por honorarios o comisiones sin sueldo o salario fijo (miles de horas)",
    "j010a": "Total de salarios al personal de producción, ventas y servicios (millones de pesos)",
    "j203a": "Total de sueldos al personal administrativo, contable y de dirección (millones de pesos)",
    "j300a": "Contribuciones patronales a regímenes de seguridad social (millones de pesos)",
    "j400a": "Otras prestaciones sociales (millones de pesos)",
    "j500a": "Utilidades repartidas al personal (millones de pesos)",
    "j600a": "Gastos por indemnización o liquidación del personal (millones de pesos)",
    "k010a": "Mercancías y bienes comprados para la reventa (millones de pesos)",
    "k020a": "Materiales e insumos consumidos para la prestación de servicios (millones de pesos)",
    "k030a": "Materias primas y materiales que se integran a la producción (millones de pesos)",
    "k311a": "Gastos por consumo de papelería y artículos de oficina (millones de pesos)",
    "k042a": "Consumo de combustibles, lubricantes y energéticos (millones de pesos)",
    "k412a": "Gasto por consumo de energía eléctrica (millones de pesos)",
    "k050a": "Renta y alquiler de bienes muebles e inmuebles (millones de pesos)",
    "k610a": "Pagos a otra razón social que contrató y proporcionó personal (millones de pesos)",
    "k620a": "Gastos por honorarios o comisiones sin sueldo o salario fijo (millones de pesos)",
    "k060a": "Contratación de servicios profesionales, científicos y técnicos (millones de pesos)",
    "k070a": "Maquila y servicios de producción de bienes por contrato (millones de pesos)",
    "k810a": "Gastos por publicidad (millones de pesos)",
    "k820a": "Gastos por servicios de comunicación (millones de pesos)",
    "k910a": "Gastos por consumo de envases y empaques (millones de pesos)",
    "k950a": "Reparaciones y refacciones para mantenimiento corriente (millones de pesos)",
    "k096a": "Fletes de productos vendidos (millones de pesos)",
    "k976a": "Consumo de agua (millones de pesos)",
    "k090a": "Consumo de otros bienes y servicios (millones de pesos)",
    "m010a": "Ingresos por la reventa de mercancías y bienes (millones de pesos)",
    "m030a": "Venta de productos elaborados, generados o extraídos (millones de pesos)",
    "m090a": "Otros ingresos por suministro de bienes y servicios (millones de pesos)",
    "p100a": "Total de inventario inicial de mercancías compradas para reventa (millones de pesos)",
    "p100b": "Total de inventario final de mercancías compradas para reventa (millones de pesos)",
    "p030a": "Total de inventario inicial de productos en proceso (millones de pesos)",
    "p030b": "Total de inventario final de productos en proceso (millones de pesos)",
    "q010a": "Acervo total de maquinaria y equipo de producción (millones de pesos)",
    "q020a": "Acervo total de bienes inmuebles (millones de pesos)",
    "q030a": "Acervo total de unidades y equipo de transporte (millones de pesos)",
    "q400a": "Acervo total de equipo de cómputo y periféricos (millones de pesos)",
    "q900a": "Acervo total de mobiliario, equipo de oficina y otros activos fijos (millones de pesos)",
}
