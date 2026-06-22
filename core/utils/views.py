from typing import Iterable

from core.utils.logger import get_console_logger

logger = get_console_logger(__name__)


def refresh_materialized_views(
    db,
    views: Iterable[str],
    concurrently: bool = True,
) -> None:
    """Refresh one or more materialized views through a raw connection.

    When *concurrently* is True and a view has never been populated, the
    first refresh is done without CONCURRENTLY (PostgreSQL requirement).

    Args:
        db: Connected Database instance (exposes get_connection()).
        views: Materialized view names to refresh, in order.
        concurrently: Use REFRESH ... CONCURRENTLY (default) to avoid read
            locks. Each view must have a unique index and have been populated
            at least once. Set False only for views with no unique index.
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        for view in views:
            if concurrently:
                cursor.execute(
                    "SELECT relispopulated FROM pg_class WHERE relname = %s AND relkind = 'm'",
                    (view,),
                )
                row = cursor.fetchone()
                is_populated = row[0] if row else True
                clause = "CONCURRENTLY " if is_populated else ""
            else:
                clause = ""

            cursor.execute(f"REFRESH MATERIALIZED VIEW {clause}{view};")
            logger.info(f"[refresh] {view} refreshed{' concurrently' if clause else ''}")
        cursor.close()
