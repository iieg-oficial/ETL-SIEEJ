from core.pipelines.scian.attributes import ScianTables as T
from core.pipelines.scian.schemas import Clases, Ramas, Sectores, Subramas, Subsectores

SHEET_NAME = "Español"

REQUEST_TIMEOUT = 120

# La hoja no trae encabezado real: la fila 0 es el titulo del documento.
HEADER_ROWS = 1

# El nivel jerarquico se codifica como sangria: la celda del codigo vive en la
# columna del nivel y su descripcion en la siguiente.
SHEET_COLUMNS = ["col_0", "col_1", "col_2", "col_3", "col_4", "col_5"]

NIVELES = [T.SECTORES, T.SUBSECTORES, T.RAMAS, T.SUBRAMAS, T.CLASES]

# Sufijo que INEGI escribe como exponente al final de la descripcion: marca las
# categorias comparables a nivel trinacional con el NAICS de EUA y Canada.
# Nunca aparece en clases.
TRINACIONAL_SUFFIX = "T"

TRINACIONAL_NIVELES = [T.SECTORES, T.SUBSECTORES, T.RAMAS, T.SUBRAMAS]

NULL_VALUES = ["", "nan", "null", "n/a", "na"]

# Orden de carga: cada nivel necesita los ids del anterior para resolver su FK.
MODELOS = [Sectores, Subsectores, Ramas, Subramas, Clases]

PADRE_FK = {
    Subsectores: Subsectores.sector_id.key,
    Ramas: Ramas.subsector_id.key,
    Subramas: Subramas.rama_id.key,
    Clases: Clases.subrama_id.key,
}
