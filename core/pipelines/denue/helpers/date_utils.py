from datetime import date, datetime

from core.db import Database
from core.pipelines.denue.schemas import CatActualizaciones
from core.utils.bulk_ops import get_last_update
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


def resolve_start_date(mode: str, start_date: date, db_name: str, database_url: str) -> date:
    if mode != "update":
        return start_date
    db = Database(db_name, database_url)
    db.connect()
    try:
        with db.get_session() as session:
            last_date = get_last_update(session, CatActualizaciones, CatActualizaciones.fecha_actualizacion.key)
    finally:
        db.disconnect()
    if last_date:
        logger.info(f"[resolve_start_date] Update mode: last actualizacion {last_date}")
        return last_date
    return start_date
