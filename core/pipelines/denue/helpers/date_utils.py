from datetime import datetime

from core.utils.logger import get_console_logger

logger = get_console_logger(__name__)


def parse_periodo(data: str) -> datetime | None:
    try:
        text = data.strip()
        if len(text) == 4 and text.isdigit():
            return datetime.strptime(f"01/01/{text}", "%d/%m/%Y")
        if "/" in text and len(text.split("/")) == 2:
            return datetime.strptime(f"01/{text}", "%d/%m/%Y")
        return datetime.strptime(text, "%d/%m/%Y")
    except Exception as e:
        logger.warning(f"Error parsing date from '{data}': {e}")
        return None
