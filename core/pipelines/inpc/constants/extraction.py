from typing import Dict
from core.pipelines.inpc.constants.cities import INPC_CITIES
from core.pipelines.inpc.constants.states import INPC_ENTITIES


SKIP_ROWS: int = 8

LOCATION_ITEMS: Dict[str, list] = {
    "City": list(INPC_CITIES.items()),
    "Entity": list(INPC_ENTITIES.items()),
    "National": [(None, None)],
}
