import requests

from datetime import date
from retry import retry

from core.pipelines.inpc.config import settings
from core.utils.logger import get_logger

logger = get_logger("inpc.download")


@retry((requests.RequestException, ConnectionError), tries=6, delay=5, jitter=3, logger=logger)
def download_inpc_csv(
    id_estructura: str,
    series_ids: list[str],
    start_year: int = 1979,
    anio_fin: int = date.today().year,
) -> str:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.inegi.org.mx",
        }
    )

    series_str = f"e|{','.join(series_ids)},"

    data = {
        "idEstructura": id_estructura,
        "_formato": "CSV",
        "_anioI": str(start_year),
        "_anioF": str(anio_fin),
        "_meta": "1",
        "_tipo": "Niveles",
        "_info": "Índices",
        "_orient": "vertical",
        "esquema": "0",
        "st": "",
        "pf": "inp",
        "cuadro": id_estructura,
        "_series": series_str,
        "cvEstructura": id_estructura,
    }

    response = session.post(
        url=settings.INPC_BASE_URL,
        params={"INPtipoExporta": "CSV"},
        data=data,
        timeout=30,
    )
    response.raise_for_status()

    return response.text
