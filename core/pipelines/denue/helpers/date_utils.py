from datetime import date, datetime

from sqlalchemy import func, select

from core.db import Database
from core.pipelines.denue.constants import ENTIDAD_JALISCO
from core.pipelines.denue.schemas import CatActualizaciones, StgEstEntResumen, StgEstJal
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


def _last_loaded_query(entidad: int):
    query = select(func.max(CatActualizaciones.fecha_actualizacion))
    if entidad == ENTIDAD_JALISCO:
        return query.join(StgEstJal, StgEstJal.actualizacion_id == CatActualizaciones.id)
    return query.join(StgEstEntResumen, StgEstEntResumen.actualizacion_id == CatActualizaciones.id).where(
        StgEstEntResumen.entidad_id == entidad
    )


def resolve_start_date(mode: str, start_date: date, entidad: int, db_name: str, database_url: str) -> date:
    if mode != "update":
        return start_date
    db = Database(db_name, database_url)
    db.connect()
    try:
        with db.get_session() as session:
            last_date = session.execute(_last_loaded_query(entidad)).scalar()
    finally:
        db.disconnect()
    if last_date:
        logger.info(f"[resolve_start_date] Update mode: entidad {entidad} last loaded {last_date}")
        return last_date
    return start_date
