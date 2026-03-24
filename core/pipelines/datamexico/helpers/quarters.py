from core.db import Database
from core.pipelines.datamexico.config import settings
from core.pipelines.datamexico.schemas import FlujoComercio
from core.utils.bulk_ops import get_last_update


def next_quarter(periodo: int) -> int:
    anio, trimestre = divmod(periodo, 10)
    if trimestre < 4:
        return periodo + 1
    return (anio + 1) * 10 + 1


def get_start_quarter() -> int:
    db = Database(settings.DB_NAME, settings.database_url)
    db.connect()
    try:
        with db.get_session() as session:
            last = get_last_update(session, FlujoComercio, FlujoComercio.periodo_id.key)
    finally:
        db.disconnect()
    return next_quarter(last) if last else settings.START_QUARTER
