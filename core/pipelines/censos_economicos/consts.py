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
CE_ECONOMIC_COLUMNS = [
    "ue",
    "h001a",
    "h000a",
    "h010a",
    "h020a",
    "i000a",
    "j000a",
    "k000a",
    "m000a",
    "a111a",
    "a121a",
    "a131a",
    "a211a",
    "a221a",
    "p000c",
    "q000a",
    "q000b",
    "a700a",
    "a800a",
    "q000c",
    "q000d",
    "p000a",
    "p000b",
    "o010a",
    "o020a",
    "m700a",
    "p030c",
    "a511a",
    "m020a",
    "m050a",
    "m091a",
    "h001b",
    "h001c",
    "h001d",
    "h000b",
    "h000c",
    "h000d",
    "h010b",
    "h010c",
    "h010d",
    "h101a",
    "h101b",
    "h101c",
    "h101d",
    "h203a",
    "h203b",
    "h203c",
    "h203d",
    "h020b",
    "h020c",
    "h020d",
    "i000b",
    "i000c",
    "i000d",
    "i100a",
    "i100b",
    "i100c",
    "i100d",
    "i200a",
    "i200b",
    "i200c",
    "i200d",
    "j010a",
    "j203a",
    "j300a",
    "j400a",
    "j500a",
    "j600a",
    "k010a",
    "k020a",
    "k030a",
    "k311a",
    "k042a",
    "k412a",
    "k050a",
    "k610a",
    "k620a",
    "k060a",
    "k070a",
    "k810a",
    "k820a",
    "k910a",
    "k950a",
    "k096a",
    "k976a",
    "k090a",
    "m010a",
    "m030a",
    "m090a",
    "p100a",
    "p100b",
    "p030a",
    "p030b",
    "q010a",
    "q020a",
    "q030a",
    "q400a",
    "q900a",
]
