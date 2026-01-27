from sqlalchemy.dialects.postgresql import insert
from typing import List, Dict

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

def bulk_insert(session, data: List[Dict], model) -> None:
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

def get_mapping(session, model, key_column: str, value_column: str) -> Dict:
    results = session.query(
        getattr(model, key_column),
        getattr(model, value_column)
    ).all()
    return {row[0]: row[1] for row in results}
