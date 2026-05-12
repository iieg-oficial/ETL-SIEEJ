import io

import pandas as pd
import requests
import urllib3

from core.pipelines.produccion_ganadera.config import settings
from core.utils.logger import get_logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = get_logger(settings.PIPELINE_NAME)


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
