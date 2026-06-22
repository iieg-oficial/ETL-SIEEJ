from typing import Iterable

from core.utils.logger import get_console_logger

logger = get_console_logger(__name__)


def refresh_materialized_views(
    db,
    views: Iterable[str],
    concurrently: bool = True,
) -> None:
    """Refresh one or more materialized views through a raw connection.

    Args:
        db: Connected Database instance (exposes get_connection()).
        views: Materialized view names to refresh, in order.
        concurrently: Use REFRESH ... CONCURRENTLY (default) to avoid read
            locks. Each view must have a unique index and have been populated
            at least once. Set False only for views with no unique index.
    """
    clause = "CONCURRENTLY " if concurrently else ""
    statements = "\n".join(f"REFRESH MATERIALIZED VIEW {clause}{view};" for view in views)

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(statements)
        cursor.close()

    logger.info("[refresh] materialized views refreshed")
