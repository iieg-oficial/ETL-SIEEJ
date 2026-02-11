from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func
from more_itertools import chunked
from typing import List, Dict

from core.utils.logger import get_logger
from core.utils import normalize_text

logger = get_logger("bulk_ops")

def insert_records(session, data: List[Dict], model, conflict_keys: List[str]) -> None:
    for item in data:
        stmt = insert(model).values(**item)
        stmt = stmt.on_conflict_do_nothing(index_elements=conflict_keys)
        session.execute(stmt)
    session.flush()

def upsert_records(session, data: List[Dict], model, conflict_keys: List[str]) -> None:
    stmt = insert(model).values(data)
    stmt = stmt.on_conflict_do_update(
        index_elements=conflict_keys,
        set_={k: stmt.excluded[k] for k in data[0].keys() if k not in conflict_keys}
    )
    session.execute(stmt)
    session.flush()

def bulk_insert(session, data: List[Dict], model, chunk_size: int = None) -> None:
    table_name = model.__tablename__
    total = len(data)
    logger.info(f"📦 Inserting {total} records into '{table_name}'")

    if chunk_size:
        for i, chunk in enumerate(chunked(data, chunk_size), start=1):
            session.bulk_insert_mappings(model, chunk)
            logger.info(f"  chunk {i}: {min(i * chunk_size, total)}/{total}")
    else:
        session.bulk_insert_mappings(model, data)

    session.flush()

def count_records(session, model, filter_column: str = None, filter_value = None) -> int:
    query = session.query(model)
    if filter_column and filter_value:
        query = query.filter(getattr(model, filter_column) == filter_value)
    return query.count()

def get_all_records(session, model, columns: List[str] = None) -> List[Dict]:
    if columns:
        results = session.query(*[getattr(model, col) for col in columns]).all()
        return [dict(zip(columns, row)) for row in results]
    return [row.__dict__ for row in session.query(model).all()]

def sync_id_sequence(session, model) -> None:
    max_id = session.query(func.max(model.id)).scalar() or 0
    session.execute(
        func.setval(func.pg_get_serial_sequence(model.__tablename__, 'id'), max_id + 1, False)
    )

def get_mapping(session, model, key_column: str, value_column: str, is_normalize: bool = False) -> Dict:
    results = session.query(
        getattr(model, key_column),
        getattr(model, value_column)
    ).all()
    if is_normalize:
        return {normalize_text(row[0]): row[1] for row in results}
    return {row[0]: row[1] for row in results}
