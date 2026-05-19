import io
import pandas as pd
import requests
import urllib3

from core.pipelines.agropecuario_siap.config import settings
from core.pipelines.agropecuario_siap.constants import RENAME_HEADER_BASE
from core.utils.logger import get_logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = get_logger(settings.PIPELINE_NAME)


def rename_header(year: int) -> dict:
    header = dict(RENAME_HEADER_BASE)
    header["Nomcultivo Sin Um" if 2015 <= year <= 2020 else "Nomcultivo"] = "cultivo"
    header["Precio" if year <= 2020 else "Preciomediorural"] = "precio_med_rural"
    return header


def year_has_data(year: int) -> bool:
    url = settings.SIAP_URL.format(anio=year)
    try:
        r = requests.get(url, verify=False, timeout=30)
        r.raise_for_status()
        df = pd.read_csv(io.BytesIO(r.content), encoding="latin-1", nrows=1)
        return not df.empty
    except Exception as exc:
        logger.warning(f"[update] Year {year} check failed: {exc}")
        return False
