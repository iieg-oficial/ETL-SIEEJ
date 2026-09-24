import re

PIPELINE_NAME = "fosas_clandestinas"

MONTHS = {
    "ENERO": 1,
    "FEBRERO": 2,
    "MARZO": 3,
    "ABRIL": 4,
    "MAYO": 5,
    "JUNIO": 6,
    "JULIO": 7,
    "AGOSTO": 8,
    "SEPTIEMBRE": 9,
    "OCTUBRE": 10,
    "NOVIEMBRE": 11,
    "DICIEMBRE": 12,
    "ENE": 1,
    "FEB": 2,
    "MAR": 3,
    "ABR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AGO": 8,
    "SEPT": 9,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DIC": 12,
}

PDF_CONTENT_TYPE = "application/pdf"

# Filenames that belong to the public register table
REGISTER_FILE_RE = re.compile(r"(TABLA|FOSAS|INHUMACIONES).*\.PDF$")

# Cut-off month and year inside the filename; longest names first so ABRIL wins over ABR
_MONTH_ALT = "|".join(sorted(MONTHS, key=len, reverse=True))
CUTOFF_RE = re.compile(rf"(?<![A-Z])({_MONTH_ALT})[-_ ]?(\d{{4}})")

# Autoindex row: href plus "Last modified" column
INDEX_ROW_RE = re.compile(r'<a href="([^"?/][^"]*)">[^<]*</a></td><td[^>]*>\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2})')
INDEX_DIR_RE = re.compile(r'<a href="(\d{2,4})/">')

PUBLICACIONES_FILE = "publicaciones.pkl"
STG_FILE = "stg_fosas_clandestinas.pkl"

# Header keyword -> target column; first match wins, checked in order
HEADER_KEYWORDS = (
    ("denominacion", "denominacion"),
    ("municipio", "municipio"),
    ("inicio", "fecha_inicio"),
    ("fin", "fecha_fin"),
    ("localizadas", "pre_victimas_loc"),
    ("identificadas2", "pre_victimas_ide"),
    ("victimas identificadas", "pre_victimas_ide"),
    ("hombres", "pre_hom_ide"),
    ("mujeres", "pre_muj_ide"),
)
COUNT_COLS = ["pre_victimas_loc", "pre_victimas_ide", "pre_hom_ide", "pre_muj_ide"]
PDF_COLS = ["consecutivo", "denominacion", "municipio", "fecha_inicio", "fecha_fin", *COUNT_COLS]
STG_COLS = [
    "fecha_corte",
    "consecutivo",
    "periodo",
    "denominacion",
    "municipio",
    "fecha_inicio",
    "fecha_fin",
    "en_proceso",
    *COUNT_COLS,
    "estatus_loc",
]

# First site is printed as "oct-18" (Excel date autoformat); it has no real number
UNNUMBERED_SITE = "oct-18"
UNNUMBERED_CONSECUTIVO = 0

# PROCESANDO, EN PROCESAMIENTO, PROCESAMIENTO PENDIENTE and typos like PROCESNADO
EN_PROCESO_TEXT = "PROCES"
EMPTY_VALUES = {"", "-"}
MONTH_YEAR_RE = re.compile(r"^(\d{1,2})/(\d{2,4})$")
# Early editions print CONCLUIDA instead of an end date
UNDATED_VALUES = {"", "-", "CONCLUIDA"}

TITLE_COLS = ["denominacion"]
