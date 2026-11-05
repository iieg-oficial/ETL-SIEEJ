from core.pipelines.nacimientos_dgis.queries.nacimientos_adolescentes import INSERT_NACIMIENTOS_ADOLESCENTES
from core.pipelines.nacimientos_dgis.queries.stg import (
    COPY_CERTIFICADOS,
    COPY_STG,
    TRUNCATE_CERTIFICADOS,
    TRUNCATE_STG,
)
from core.pipelines.nacimientos_dgis.queries.tasa_fecundidad import INSERT_TASA_FECUNDIDAD
from core.pipelines.nacimientos_dgis.queries.views import MATERIALIZED_VIEWS
