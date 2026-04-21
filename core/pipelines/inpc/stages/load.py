import pandas as pd
from pathlib import Path
from typing import Any, Optional

from core.db import Database
from core.pipelines.stage import Stage
from core.utils import df_to_records, normalize_col
from core.utils.files import cleanup_pipeline_data
from core.utils.bulk_ops import (
    insert_records,
    bulk_insert,
    count_records,
    sync_id_sequence,
    get_cvegeo_mapping,
)
from core.pipelines.inpc.attributes import InpcTables as T
from core.pipelines.inpc.constants import ENTITY_NAME_ALIASES
from core.pipelines.inpc.schemas import (
    Ciudades,
    ObjetosGasto,
    InpcCiudades,
    InpcEntidades,
    InpcNacional,
)
from core.pipelines.inpc.config import settings


class InpcLoad(Stage):
    def __init__(self):
        super().__init__("inpc", "load")
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> dict:
        result = {"dfs": {}, "catalogs": input_data["catalogs"] if input_data else {}}
        for name in ("cities", "entities", "national"):
            pkl_path = Path(f"data/transform/inpc/inpc_{name}.pkl")
            if pkl_path.exists():
                self.logger.info(f"[source] Loading {pkl_path}")
                result["dfs"][name] = pd.read_pickle(pkl_path)
            else:
                self.logger.info(f"[source] pkl not found for {name}, using transform output")
                result["dfs"][name] = input_data["dfs"][name]
        return result

    def _load_catalogs(self, session, catalogs: dict) -> None:
        insert_records(
            session,
            catalogs[T.OBJETOS_GASTO],
            ObjetosGasto,
            conflict_keys=[ObjetosGasto.id.key],
        )
        sync_id_sequence(session, Ciudades)
        insert_records(
            session,
            catalogs[T.CIUDADES],
            Ciudades,
            conflict_keys=[Ciudades.id.key],
        )
        sync_id_sequence(session, Ciudades)

    def _map_foreign_keys(self, session, dfs: dict) -> dict:
        estados_map = get_cvegeo_mapping(
            session,
            table="cvegeo_states",
            key="nom_ent",
            value="cve_ent",
            is_normalize=True,
        )
        df_entities = dfs["entities"].copy()
        df_entities["entity"] = df_entities["entity"].replace(ENTITY_NAME_ALIASES)
        df_entities[InpcEntidades.entidad_id.key] = normalize_col(df_entities, "entity").map(estados_map)
        df_entities = df_entities.drop(columns=["entity"])
        return {**dfs, "entities": df_entities}

    def action(self, input_data: dict) -> dict:
        self.logger.info("[action] Loading data into DB")
        catalogs = input_data["catalogs"]

        main_tables = [
            (InpcCiudades, "cities"),
            (InpcEntidades, "entities"),
            (InpcNacional, "national"),
        ]

        try:
            self.db.connect()
            with self.db.get_session() as session:
                self._load_catalogs(session, catalogs)
                dfs = self._map_foreign_keys(session, input_data["dfs"])

                records_before = {name: count_records(session, model) for model, name in main_tables}

                for model, name in main_tables:
                    cols = [c for c in model.columns() if c != "id"]
                    records = df_to_records(dfs[name], cols)
                    bulk_insert(session, records, model, chunk_size=10_000)

        except Exception:
            self.db.disconnect()
            raise

        return {"data": input_data, "records_before": records_before}

    def finalization(self, input_data: dict) -> dict:
        cleanup_pipeline_data(self.pipeline_name)
        try:
            with self.db.get_session() as session:
                for model, name in [(InpcCiudades, "cities"), (InpcEntidades, "entities"), (InpcNacional, "national")]:
                    total = count_records(session, model)
                    inserted = total - input_data["records_before"][name]
                    self.logger.info(
                        f"[finalization] {model.__tablename__}: {format(total, ',')} total, {format(inserted, ',')} inserted"
                    )
        finally:
            self.db.disconnect()

        return input_data["data"]
