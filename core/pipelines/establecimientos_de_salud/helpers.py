import pandas as pd

from core.pipelines.establecimientos_de_salud.constants import SIN_NUMERO_RAW
from core.utils.normalize import normalize_text


COL_MAPPINGS = {
    "NOMBRE DE LA ENTIDAD": "ENTIDAD",
    "NOMBRE DEL MUNICIPIO": "MUNICIPIO",
    "NOMBRE DE LA LOCALIDAD": "LOCALIDAD",
    "NOMBRE DE LA JURISDICCION": "JURISDICCION",
    "CLAVE DE VIALIDAD": "CLAVE TIPO DE VIALIDAD",
    "CLAVE DEL TIPO DE ASENTAMIENTO": "CLAVE TIPO DE ASENTAMIENTO",
    "CLAVE DE ESTATUS DE OPERACION": "CLAVE ESTATUS DE OPERACION",
    "CLAVE TIPO ESTABLECIMIENTO": "CLAVE DEL TIPO ESTABLECIMIENTO",
}

SIN_NUMERO_NORMALIZED = {normalize_text(v.strip()) for v in SIN_NUMERO_RAW}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols_to_rename = {col: COL_MAPPINGS[col] for col in df.columns if col in COL_MAPPINGS}
    return df.rename(columns=cols_to_rename)


def sanitize_numero(val) -> str | None:
    if pd.isna(val) or val is None:
        return None
    s = str(val).strip()
    if not s or s == "0":
        return None
    if normalize_text(s) in SIN_NUMERO_NORMALIZED:
        return None
    return s
