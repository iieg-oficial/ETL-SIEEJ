import numpy as np
import pandas as pd
from pathlib import Path
from typing import Any, Optional

from core.db import Database
from core.pipelines.stage import Stage
from core.utils import df_to_records, normalize_col
from core.utils.files import cleanup_pipeline_data
from core.utils.logger import get_logger
from core.utils.bulk_ops import (
    insert_records,
    count_records,
    get_mapping,
    sync_id_sequence,
    get_all_records,
)
from core.pipelines.centros_educativos.schemas import (
    Turnos,
    TiposEducativos,
    NivelesEducativos,
    ServiciosEducativos,
    TiposControles,
    TiposSostenimiento,
    Localidades,
    Domicilios,
    Colonias,
    Centros,
)
from core.pipelines.centros_educativos.config import settings
from core.pipelines.centros_educativos.attributes.centros_educativos import CentrosEducativosTables as T
from core.pipelines.centros_educativos.mappings.secondary_tables import (
    TurnosMap,
    TipoEducativoMap,
    NivelEducativoMap,
    ServicioEducativoMap,
    NombreControlMap,
    TipoSostenimientoMap,
)


class CentrosEducativosLoad(Stage):
    def __init__(self, pipeline_name: str = "centros_educativos", mode: str = "bootstrap", entidad: int = None):
        super().__init__(pipeline_name, "load")
        self.mode = mode
        self.logger = get_logger(f"{pipeline_name}.load")
        self.entidad = entidad
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(self, input_data: Optional[Any]) -> Any:
        pkl_df_path = Path(f"data/transform/centros_educativos/centros_educativos_df_{self.entidad}.pkl")
        pkl_catalogs_path = Path(f"data/transform/centros_educativos/centros_educativos_catalogs_{self.entidad}.pkl")

        self.logger.info(f"[source] Checking for existing pkl files")
        if pkl_df_path.exists() and pkl_catalogs_path.exists():
            self.logger.info(f"[source] Loading from pkl files")
            df = pd.read_pickle(pkl_df_path)
            catalogs = pd.read_pickle(pkl_catalogs_path).to_dict()
            return {"df": df, "catalogs": catalogs}

        self.logger.info(f"[source] pkl files not found, using transform output")
        output_data = input_data
        return output_data

    def _load_catalogs(self, session, catalogs):
        self.logger.info("[_load_catalogs] Syncing ID sequences for dynamic tables")
        for model in [Localidades, Domicilios, Colonias]:
            sync_id_sequence(session, model)

        self.logger.info("[_load_catalogs] Loading turnos static catalog")
        insert_records(session, TurnosMap.to_records("turno"), Turnos, conflict_keys=[Turnos.id.key])

        self.logger.info("[_load_catalogs] Loading tipos_educativos static catalog")
        insert_records(
            session,
            TipoEducativoMap.to_records("tipo_educativo"),
            TiposEducativos,
            conflict_keys=[TiposEducativos.id.key],
        )

        self.logger.info("[_load_catalogs] Loading niveles_educativos static catalog")
        insert_records(
            session,
            NivelEducativoMap.to_records("nivel_educativo"),
            NivelesEducativos,
            conflict_keys=[NivelesEducativos.id.key],
        )

        self.logger.info("[_load_catalogs] Loading servicios_educativos static catalog")
        insert_records(
            session,
            ServicioEducativoMap.to_records("servicio_educativo"),
            ServiciosEducativos,
            conflict_keys=[ServiciosEducativos.id.key],
        )

        self.logger.info("[_load_catalogs] Loading tipos_controles static catalog")
        insert_records(
            session, NombreControlMap.to_records("tipo_control"), TiposControles, conflict_keys=[TiposControles.id.key]
        )

        self.logger.info("[_load_catalogs] Loading tipos_sostenimiento static catalog")
        insert_records(
            session,
            TipoSostenimientoMap.to_records("tipo_sostenimiento"),
            TiposSostenimiento,
            conflict_keys=[TiposSostenimiento.id.key],
        )

        self.logger.info(f"[_load_catalogs] Loading {len(catalogs[T.LOCALIDADES])} localidades")
        insert_records(session, catalogs[T.LOCALIDADES], Localidades, conflict_keys=[Localidades.cve_geo_id.key])

        self.logger.info(f"[_load_catalogs] Loading {len(catalogs[T.DOMICILIOS])} domicilios")
        insert_records(
            session,
            catalogs[T.DOMICILIOS],
            Domicilios,
            conflict_keys=[Domicilios.domicilio.key, Domicilios.numero_exterior.key, Domicilios.codigo_postal.key],
        )

        self.logger.info("[_load_catalogs] Getting localidades for colonias mapping")
        localidades_rows = get_all_records(session, Localidades, [Localidades.id.key, Localidades.cve_geo_id.key])
        localidades_map_for_colonias = {r[Localidades.cve_geo_id.key]: r[Localidades.id.key] for r in localidades_rows}
        self.logger.info(f"[_load_catalogs] Built localidades map with {len(localidades_map_for_colonias)} entries")

        self.logger.info(f"[_load_catalogs] Processing {len(catalogs[T.COLONIAS])} colonias for loading")
        colonias_records = []
        for colonia_record in catalogs[T.COLONIAS]:
            cve_geo_id = int(
                f"{colonia_record['entidad_id']:02}{colonia_record['municipio_id']:03}{colonia_record['localidad_id']:04}"
            )
            localidad_id = localidades_map_for_colonias.get(cve_geo_id)
            if localidad_id:
                colonias_records.append(
                    {Colonias.colonia.key: colonia_record["colonia"], Colonias.localidad_id.key: localidad_id}
                )

        self.logger.info(f"[_load_catalogs] Loading {len(colonias_records)} colonias to database")
        insert_records(
            session, colonias_records, Colonias, conflict_keys=[Colonias.colonia.key, Colonias.localidad_id.key]
        )

    def _map_foreign_keys(self, session, df):
        self.logger.info("[_map_foreign_keys] Building foreign key mappings")

        self.logger.info("[_map_foreign_keys] Getting turnos mapping")
        turnos_map = get_mapping(session, Turnos, Turnos.turno.key, Turnos.id.key, is_normalize=True)

        self.logger.info("[_map_foreign_keys] Getting tipos_educativos mapping")
        tipos_educativos_map = get_mapping(
            session, TiposEducativos, TiposEducativos.tipo_educativo.key, TiposEducativos.id.key, is_normalize=True
        )

        self.logger.info("[_map_foreign_keys] Getting niveles_educativos mapping")
        niveles_educativos_map = get_mapping(
            session,
            NivelesEducativos,
            NivelesEducativos.nivel_educativo.key,
            NivelesEducativos.id.key,
            is_normalize=True,
        )

        self.logger.info("[_map_foreign_keys] Getting servicios_educativos mapping")
        servicios_educativos_map = get_mapping(
            session,
            ServiciosEducativos,
            ServiciosEducativos.servicio_educativo.key,
            ServiciosEducativos.id.key,
            is_normalize=True,
        )

        self.logger.info("[_map_foreign_keys] Getting tipos_controles mapping")
        tipos_controles_map = get_mapping(
            session, TiposControles, TiposControles.tipo_control.key, TiposControles.id.key, is_normalize=True
        )

        self.logger.info("[_map_foreign_keys] Getting tipos_sostenimiento mapping")
        tipos_sostenimiento_map = get_mapping(
            session,
            TiposSostenimiento,
            TiposSostenimiento.tipo_sostenimiento.key,
            TiposSostenimiento.id.key,
            is_normalize=True,
        )

        self.logger.info("[_map_foreign_keys] Getting domicilios mapping")
        domicilios_map = get_mapping(session, Domicilios, Domicilios.domicilio.key, Domicilios.id.key)

        self.logger.info("[_map_foreign_keys] Getting colonias mapping")
        colonias_map = get_mapping(session, Colonias, Colonias.colonia.key, Colonias.id.key)

        self.logger.info("[_map_foreign_keys] Getting localidades mapping")
        localidades_rows = get_all_records(session, Localidades, [Localidades.id.key, Localidades.cve_geo_id.key])
        localidades_map = {r[Localidades.cve_geo_id.key]: r[Localidades.id.key] for r in localidades_rows}

        self.logger.info("[_map_foreign_keys] Applying foreign key mappings to dataframe")
        df = df.copy()
        df[Centros.turno_id.key] = normalize_col(df, Turnos.turno.key).map(turnos_map)
        df[Centros.tipos_educativos_id.key] = normalize_col(df, TiposEducativos.tipo_educativo.key).map(
            tipos_educativos_map
        )
        df[Centros.nivel_educativo_id.key] = normalize_col(df, NivelesEducativos.nivel_educativo.key).map(
            niveles_educativos_map
        )
        df[Centros.servicio_educativo_id.key] = normalize_col(df, ServiciosEducativos.servicio_educativo.key).map(
            servicios_educativos_map
        )
        df[Centros.tipo_control_id.key] = normalize_col(df, TiposControles.tipo_control.key).map(tipos_controles_map)
        df[Centros.tipo_sostenimiento_id.key] = normalize_col(df, TiposSostenimiento.tipo_sostenimiento.key).map(
            tipos_sostenimiento_map
        )

        self.logger.info("[_map_foreign_keys] Mapping geographic locations")
        df["cve_geo_id"] = df.apply(
            lambda row: int(f"{row['entidad_id']:02}{row['municipio_id']:03}{row['localidad_id']:04}")
            if pd.notna(row["entidad_id"]) and pd.notna(row["municipio_id"]) and pd.notna(row["localidad_id"])
            else None,
            axis=1,
        )
        df[Centros.localidades_id.key] = df["cve_geo_id"].map(localidades_map)

        df[Centros.domicilios_id.key] = df[Domicilios.domicilio.key].map(domicilios_map)
        df[Centros.colonias_id.key] = df[Colonias.colonia.key].map(colonias_map)

        self.logger.info("[_map_foreign_keys] Foreign key mapping completed")
        return df.replace({np.nan: None})

    def action(self, input_data: Any) -> Any:
        df = input_data["df"]
        if df.empty:
            self.logger.info("[action] Empty DataFrame, skipping load")
            return None

        self.logger.info(f"[action] Loading {len(df)} rows into DB")
        catalogs = input_data["catalogs"]
        self.logger.info(f"[action] Catalogs available: {list(catalogs.keys())}")

        try:
            self.db.connect()
            self.logger.info("[action] Database connected successfully")
            with self.db.get_session() as session:
                records_before = count_records(session, Centros)
                self.logger.info(f"[action] Found {records_before:,} existing records in Centros table")

                self.logger.info("[action] Loading catalog tables")
                self._load_catalogs(session, catalogs)

                self.logger.info("[action] Mapping foreign keys")
                df = self._map_foreign_keys(session, df)

                self.logger.info(f"[action] Converting {len(df)} rows to records")
                records = df_to_records(df, Centros.columns())
                self.logger.info(f"[action] Starting insert of {len(records):,} Centros records")
                insert_records(
                    session,
                    records,
                    Centros,
                    conflict_keys=[Centros.clave_centro_trabajo.key],
                )
                self.logger.info("[action] Centros records inserted successfully")
        except Exception as e:
            self.logger.error(f"[action] Error during load: {e}")
            self.db.disconnect()
            raise

        return {"data": input_data, "records_before": records_before}

    def finalization(self, input_data: Any) -> Any:
        cleanup_pipeline_data(self.pipeline_name)
        if input_data is None:
            return None
        try:
            with self.db.get_session() as session:
                total = count_records(session, Centros)
                inserted = total - input_data["records_before"]
            self.logger.info(f"[finalization] {format(total, ',')} centros_educativos in database")
            self.logger.info(f"[finalization] {format(inserted, ',')} centros_educativos inserted")
        finally:
            self.db.disconnect()

        return input_data["data"]
