from core.pipelines.nacimientos_dgis.queries.nacimientos_adolescentes import INSERT_NACIMIENTOS_ADOLESCENTES
from core.pipelines.nacimientos_dgis.queries.stg import COPY_STG, TRUNCATE_STG
from core.pipelines.nacimientos_dgis.queries.tasa_fecundidad import INSERT_TASA_FECUNDIDAD
from core.pipelines.nacimientos_dgis.queries.views import REFRESH_VIEWS

__all__ = [
    "COPY_STG",
    "TRUNCATE_STG",
    "INSERT_TASA_FECUNDIDAD",
    "INSERT_NACIMIENTOS_ADOLESCENTES",
    "REFRESH_VIEWS",
]
