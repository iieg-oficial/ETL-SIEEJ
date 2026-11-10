from typing import Any

import numpy as np


def whole_number_to_str(value: Any) -> Any:
    """Render ints and whole floats as text without the ".0" suffix; leave the rest as is."""
    if isinstance(value, (bool, np.bool_)):
        return value
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    if isinstance(value, (float, np.floating)) and float(value).is_integer():
        return str(int(value))
    return value
