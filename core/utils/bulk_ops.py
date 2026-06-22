from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func, text
from more_itertools import chunked
from typing import List, Dict

from core.utils import normalize_text
from core.utils.logger import get_console_logger

logger = get_console_logger(__name__)


def insert_records(session, data: List[Dict], model, conflict_keys: List[str]) -> None:
    logger.info(f"Inserting {len(data)} records into '{model.__tablename__}'")
    for item in data:
        stmt = insert(model).values(**item)
        stmt = stmt.on_conflict_do_nothing(index_elements=conflict_keys)
        session.execute(stmt)
    session.flush()


def upsert_records(
    session, data: List[Dict], model, conflict_keys: List[str], update_keys: List[str] = None, chunk_size: int = 10_000
) -> None:
    table_name = model.__tablename__
    total = len(data)
    logger.info(f"Upserting {total} records into '{table_name}'")
    for i, chunk in enumerate(chunked(data, chunk_size), start=1):
        stmt = insert(model).values(chunk)

        exclude_keys = set(conflict_keys)
        updatable = update_keys or [k for k in chunk[0].keys() if k not in exclude_keys]

        stmt = stmt.on_conflict_do_update(index_elements=conflict_keys, set_={k: stmt.excluded[k] for k in updatable})
        logger.info(f"  chunk {i}: {min(i * chunk_size, total)}/{total}")
        session.execute(stmt)
    session.flush()


def bulk_insert(session, data: List[Dict], model, chunk_size: int = None) -> None:
    table_name = model.__tablename__
    total = len(data)
    logger.info(f"Bulk inserting {total} records into '{table_name}'")

    if chunk_size:
        for i, chunk in enumerate(chunked(data, chunk_size), start=1):
            session.bulk_insert_mappings(model, chunk)
            logger.info(f"  chunk {i}: {min(i * chunk_size, total)}/{total}")
    else:
        session.bulk_insert_mappings(model, data)

    session.flush()


def count_records(session, model, filter_column: str = None, filter_value=None) -> int:
    query = session.query(model)
    if filter_column and filter_value:
        query = query.filter(getattr(model, filter_column) == filter_value)
    count = query.count()
    logger.info(f"Count '{model.__tablename__}': {count}")
    return count


def get_all_records(session, model, columns: List[str] = None) -> List[Dict]:
    if columns:
        results = session.query(*[getattr(model, col) for col in columns]).all()
        return [dict(zip(columns, row)) for row in results]
    return [row.__dict__ for row in session.query(model).all()]


def bulk_insert_do_nothing(session, data: List[Dict], model, conflict_keys: List[str], chunk_size: int = 1000) -> None:
    """Bulk INSERT ... ON CONFLICT DO NOTHING, safe for re-runs."""
    table = model.__table__
    total = len(data)
    logger.info(f"Bulk inserting {total} records into '{table.name}' (ON CONFLICT DO NOTHING)")
    for i, chunk in enumerate(chunked(data, chunk_size), start=1):
        stmt = insert(model).values(chunk).on_conflict_do_nothing(index_elements=conflict_keys)
        session.execute(stmt)
        logger.info(f"  chunk {i}: {min(i * chunk_size, total)}/{total}")
    session.flush()


def sync_id_sequence(session, model) -> None:
    max_id = session.query(func.max(model.id)).scalar() or 0
    logger.info(f"Syncing sequence for '{model.__tablename__}' to {max_id + 1}")
    session.execute(func.setval(func.pg_get_serial_sequence(model.__tablename__, "id"), max_id + 1, False))


def get_last_update(session, model, date_column: str):
    return session.query(func.max(getattr(model, date_column))).scalar()


def get_mapping(session, model, key_column: str, value_column: str, is_normalize: bool = False) -> Dict:
    results = session.query(getattr(model, key_column), getattr(model, value_column)).all()
    logger.info(f"Mapping '{model.__tablename__}' ({key_column} -> {value_column}): {len(results)} entries")
    if is_normalize:
        return {normalize_text(row[0]): row[1] for row in results}
    return {row[0]: row[1] for row in results}


def get_cvegeo_mapping(
    session,
    table: str = "cvegeo_municipalities",
    key: str = "nomgeo",
    value: str = "cve_mun",
    cve_ent: int = None,
    is_normalize: bool = False,
) -> Dict:
    query = f"SELECT {key}, {value} FROM {table}"
    if cve_ent is not None:
        query += f" WHERE cve_ent = {cve_ent}"
    results = session.execute(text(query)).all()
    logger.info(f"Mapping '{table}' ({key} -> {value}): {len(results)} entries")
    if is_normalize:
        return {normalize_text(row[0]): row[1] for row in results}
    return {row[0]: row[1] for row in results}
