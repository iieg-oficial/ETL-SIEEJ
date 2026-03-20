import requests
import pandas as pd

from core.pipelines.datamexico.config import settings
from core.pipelines.datamexico.constants import CUBE, LOCALE, MEASURES
from core.utils.logger import get_logger

logger = get_logger("core.pipelines.datamexico.helpers.download_datamexico")


def fetch_catalog(drilldown: str) -> pd.DataFrame:
    records = _fetch([drilldown])
    return pd.DataFrame(records)


def fetch_trade_data(drilldowns: list[str], start_quarter: int = 20201) -> pd.DataFrame:
    quarters = _get_available_quarters(start_quarter)
    logger.info(f"Fetching {len(quarters)} quarters")
    frames = []
    for i, (quarter, label) in enumerate(quarters, 1):
        logger.info(f"Quarter {i}/{len(quarters)}: {label}")
        records = _fetch(drilldowns, quarter)
        if records:
            frames.append(pd.DataFrame(records))
    df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    logger.info(f"Downloaded {len(df)} records")
    return df


def _fetch(drilldowns: list[str], quarter: str | None = None) -> list[dict]:
    params = {
        "cube": CUBE,
        "drilldowns": ",".join(drilldowns),
        "measures": MEASURES,
        "locale": LOCALE,
    }
    if quarter:
        params["Quarter"] = quarter
    response = requests.get(settings.DATAMEXICO_URL, params=params, timeout=50)
    response.raise_for_status()
    return response.json().get("data", [])


def _get_available_quarters(start_quarter: int) -> list[tuple[str, str]]:
    data = _fetch(["Quarter"])
    if not data:
        return []
    df = pd.DataFrame(data)

    df = df[df["Quarter ID"].astype(int) >= start_quarter]
    return list(df[["Quarter ID", "Quarter"]].drop_duplicates().itertuples(index=False, name=None))
