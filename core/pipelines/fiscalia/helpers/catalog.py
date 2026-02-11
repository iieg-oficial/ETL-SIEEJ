from typing import Dict, List, Tuple
from sqlalchemy import func
from core.utils.logger import get_logger
from core.pipelines.fiscalia.helpers.normalize import normalize_text, drop_duplicates_col

logger = get_logger("catalog")


def get_catalog_mapping(session, model, col_name) -> Tuple[Dict[str, int], int]:
    """Retorna ({valor_normalizado: id}, max_id) desde la DB."""
    col_attr = getattr(model, col_name)
    results = session.query(col_attr, model.id).all()
    mapping = {normalize_text(getattr(row, col_name)): row.id for row in results}
    max_id = session.query(func.max(model.id)).scalar() or 0
    return mapping, max_id


def get_new_catalog_records(df, col_name, existing_map, max_id) -> Tuple[List[Dict], Dict]:
    """Encuentra valores nuevos, crea records con IDs desde max_id+1, retorna mapping actualizado."""
    unique_values = drop_duplicates_col(df, col_name).dropna(subset=[col_name])[col_name].values
    new_values = [v for v in unique_values if normalize_text(v) not in existing_map]

    if not new_values:
        return [], existing_map

    updated_map = dict(existing_map)
    new_records = []
    for i, v in enumerate(new_values, 1):
        new_id = max_id + i
        new_records.append({"id": new_id, col_name: v})
        updated_map[normalize_text(v)] = new_id

    logger.info(f"📝 {len(new_records)} new {col_name} values found")
    return new_records, updated_map
