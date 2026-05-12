from datetime import datetime

from core.db import Database
from core.pipelines.produccion_ganadera.config import settings
from core.pipelines.produccion_ganadera.schemas import StgGanadera
from core.utils.bulk_ops import get_last_update


def get_update_start_year() -> int:
    current_year = datetime.now().year
    db = Database(settings.DB_NAME, settings.database_url)
    db.connect()
    try:
        with db.get_session() as session:
            last_year = get_last_update(session, StgGanadera, StgGanadera.anio.key)
    finally:
        db.disconnect()

    return (last_year + 1) if last_year else settings.START_DATE
