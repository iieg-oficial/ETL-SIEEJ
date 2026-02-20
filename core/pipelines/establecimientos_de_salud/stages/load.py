import numpy as np
from typing import Any, Optional

from core.db import Database
from core.pipelines.stage import Stage
from core.utils import df_to_records, normalize_text, normalize_col, map_multiindex
from core.utils.files import cleanup_pipeline_data
from core.utils.logger import get_logger
from core.utils.bulk_ops import (
    insert_records, bulk_insert, count_records, get_mapping, sync_id_sequence, get_all_records,
)
from core.pipelines.establecimientos_de_salud.schemas import (
    SaludBase,
    Localidades, Jurisdicciones, Instituciones,
    TiposEstablecimiento, Tipologias, Subtipologias,
    TiposVialidad, Vialidades, TiposAsentamiento,
    EstatusEstablecimiento, NivelAtencion, EstratoUnidad, TiposObra,
    RfcEstablecimientos, MarcasMoviles, ProgramasMoviles,
    UnidadesMoviles, TiposUnidadMovil, TipologiasMoviles,
    InstitutosAdministracion, Movimientos, MotivosBaja,
    Establecimientos,
)
from core.pipelines.establecimientos_de_salud.config import settings
from core.pipelines.establecimientos_de_salud.attributes.establecimientos import EstablecimientosTables as T
from core.pipelines.establecimientos_de_salud.mappings import (
    TiposEstablecimiento as TiposEstablecimientoMap,
    EstratoUnidad as EstratoUnidadMap,
    EstatusEstablecimiento as EstatusEstablecimientoMap,
    Movimientos as MovimientosMap,
    NivelAtencion as NivelAtencionMap,
)


class EstablecimientosLoad(Stage):
    def __init__(self, pipeline_name: str = 'establecimientos_de_salud', mode: str = 'bootstrap'):
        super().__init__(pipeline_name, 'load')
        self.mode = mode
        self.logger = get_logger(f"{pipeline_name}.load")
        self.db = Database("establecimientos_de_salud", settings.database_url)

    def _load_catalogs(self, session, catalogs):
        for model in [
            Localidades, Jurisdicciones, Instituciones,
            Tipologias, Subtipologias, TiposVialidad, Vialidades,
            TiposAsentamiento, TiposObra,
            RfcEstablecimientos, MarcasMoviles, ProgramasMoviles,
            UnidadesMoviles, TiposUnidadMovil, TipologiasMoviles,
            InstitutosAdministracion, MotivosBaja,
        ]:
            sync_id_sequence(session, model)

        insert_records(session, catalogs[T.INSTITUCIONES], Instituciones, conflict_keys=[Instituciones.institucion.key])
        insert_records(session, catalogs[T.LOCALIDADES], Localidades, conflict_keys=[Localidades.municipio_id.key, Localidades.entidad_id.key, Localidades.clave_localidad.key])
        insert_records(session, catalogs[T.JURISDICCIONES], Jurisdicciones, conflict_keys=[Jurisdicciones.jurisdiccion.key])
        insert_records(session, TiposEstablecimientoMap.to_records(TiposEstablecimiento.tipo_establecimiento.key), TiposEstablecimiento, conflict_keys=[TiposEstablecimiento.id.key])
        insert_records(session, catalogs[T.TIPOLOGIAS], Tipologias, conflict_keys=[Tipologias.tipologia.key])
        insert_records(session, catalogs[T.SUBTIPOLOGIAS], Subtipologias, conflict_keys=[Subtipologias.subtipologia.key])
        insert_records(session, catalogs[T.TIPOS_VIALIDAD], TiposVialidad, conflict_keys=[TiposVialidad.tipo_vialidad.key])

        tipo_vialidad_map = get_mapping(session, TiposVialidad, TiposVialidad.tipo_vialidad.key, TiposVialidad.id.key)
        vialidades_records = [
            {Vialidades.vialidad.key: r[Vialidades.vialidad.key], Vialidades.tipo_vialidad_id.key: tipo_vialidad_map.get(r[TiposVialidad.tipo_vialidad.key])}
            for r in catalogs[T.VIALIDADES]
            if tipo_vialidad_map.get(r[TiposVialidad.tipo_vialidad.key]) is not None
        ]
        insert_records(session, vialidades_records, Vialidades, conflict_keys=[Vialidades.vialidad.key, Vialidades.tipo_vialidad_id.key])

        insert_records(session, catalogs[T.TIPOS_ASENTAMIENTO], TiposAsentamiento, conflict_keys=[TiposAsentamiento.tipo_asentamiento.key])
        insert_records(session, EstatusEstablecimientoMap.to_records(EstatusEstablecimiento.estatus_establecimiento.key), EstatusEstablecimiento, conflict_keys=[EstatusEstablecimiento.id.key])
        insert_records(session, NivelAtencionMap.to_records(NivelAtencion.nivel_atencion.key), NivelAtencion, conflict_keys=[NivelAtencion.id.key])
        insert_records(session, EstratoUnidadMap.to_records(EstratoUnidad.estrato_unidad.key), EstratoUnidad, conflict_keys=[EstratoUnidad.id.key])
        insert_records(session, catalogs[T.TIPOS_OBRA], TiposObra, conflict_keys=[TiposObra.tipo_obra.key])
        insert_records(session, MovimientosMap.to_records(Movimientos.movimiento.key), Movimientos, conflict_keys=[Movimientos.id.key])
        insert_records(session, catalogs[T.RFC_ESTABLECIMIENTOS], RfcEstablecimientos, conflict_keys=[RfcEstablecimientos.rfc.key])
        insert_records(session, catalogs[T.MARCAS_MOVILES], MarcasMoviles, conflict_keys=[MarcasMoviles.marca.key, MarcasMoviles.marca_especifica.key, MarcasMoviles.modelo.key])
        insert_records(session, catalogs[T.PROGRAMAS_MOVILES], ProgramasMoviles, conflict_keys=[ProgramasMoviles.programa_movil.key])
        insert_records(session, catalogs[T.UNIDADES_MOVILES], UnidadesMoviles, conflict_keys=[UnidadesMoviles.nombre_unidad_movil.key])
        insert_records(session, catalogs[T.TIPOS_UNIDAD_MOVIL], TiposUnidadMovil, conflict_keys=[TiposUnidadMovil.tipo_unidad_movil.key])
        insert_records(session, catalogs[T.TIPOLOGIAS_MOVILES], TipologiasMoviles, conflict_keys=[TipologiasMoviles.tipologia_movil.key])
        insert_records(session, catalogs[T.INSTITUTOS_ADMINISTRACION], InstitutosAdministracion, conflict_keys=[InstitutosAdministracion.instituto_administracion.key])
        insert_records(session, catalogs[T.MOTIVOS_BAJA], MotivosBaja, conflict_keys=[MotivosBaja.motivo_baja.key])

    def _map_foreign_keys(self, session, df):
        instituciones_map = get_mapping(session, Instituciones, Instituciones.institucion.key, Instituciones.id.key)
        tipologias_map = get_mapping(session, Tipologias, Tipologias.tipologia.key, Tipologias.id.key)
        subtipologias_map = get_mapping(session, Subtipologias, Subtipologias.subtipologia.key, Subtipologias.id.key)
        tipo_vialidad_map = get_mapping(session, TiposVialidad, TiposVialidad.tipo_vialidad.key, TiposVialidad.id.key)
        rfc_map = get_mapping(session, RfcEstablecimientos, RfcEstablecimientos.rfc.key, RfcEstablecimientos.id.key)
        programas_map = get_mapping(session, ProgramasMoviles, ProgramasMoviles.programa_movil.key, ProgramasMoviles.id.key)
        unidades_moviles_map = get_mapping(session, UnidadesMoviles, UnidadesMoviles.nombre_unidad_movil.key, UnidadesMoviles.id.key)
        tipos_unidad_movil_map = get_mapping(session, TiposUnidadMovil, TiposUnidadMovil.tipo_unidad_movil.key, TiposUnidadMovil.id.key)
        tipologias_moviles_map = get_mapping(session, TipologiasMoviles, TipologiasMoviles.tipologia_movil.key, TipologiasMoviles.id.key)
        institutos_map = get_mapping(session, InstitutosAdministracion, InstitutosAdministracion.instituto_administracion.key, InstitutosAdministracion.id.key)
        movimientos_map = get_mapping(session, Movimientos, Movimientos.movimiento.key, Movimientos.id.key, is_normalize=True)
        motivos_map = get_mapping(session, MotivosBaja, MotivosBaja.motivo_baja.key, MotivosBaja.id.key)
        jurisdicciones_map = get_mapping(session, Jurisdicciones, Jurisdicciones.jurisdiccion.key, Jurisdicciones.id.key)


        localidades_rows = get_all_records(session, Localidades, [Localidades.id.key, Localidades.clave_localidad.key, Localidades.municipio_id.key, Localidades.entidad_id.key])
        localidades_map = {(r[Localidades.municipio_id.key], r[Localidades.entidad_id.key], r[Localidades.clave_localidad.key]): r[Localidades.id.key] for r in localidades_rows}

        vialidades_rows = get_all_records(session, Vialidades, [Vialidades.id.key, Vialidades.vialidad.key, Vialidades.tipo_vialidad_id.key])
        vialidades_map = {(normalize_text(r[Vialidades.vialidad.key]), r[Vialidades.tipo_vialidad_id.key]): r[Vialidades.id.key] for r in vialidades_rows}

        marcas_rows = get_all_records(session, MarcasMoviles, [MarcasMoviles.id.key, MarcasMoviles.marca.key, MarcasMoviles.marca_especifica.key, MarcasMoviles.modelo.key])
        marcas_map = {(normalize_text(r[MarcasMoviles.marca.key]), normalize_text(r[MarcasMoviles.marca_especifica.key]), normalize_text(r[MarcasMoviles.modelo.key])): r[MarcasMoviles.id.key] for r in marcas_rows}

        df = df.copy()
        tipos_establecimiento_map = get_mapping(session, TiposEstablecimiento, TiposEstablecimiento.tipo_establecimiento.key, TiposEstablecimiento.id.key, is_normalize=True)
        tipos_asentamiento_map = get_mapping(session, TiposAsentamiento, TiposAsentamiento.tipo_asentamiento.key, TiposAsentamiento.id.key, is_normalize=True)
        estatus_map = get_mapping(session, EstatusEstablecimiento, EstatusEstablecimiento.estatus_establecimiento.key, EstatusEstablecimiento.id.key, is_normalize=True)
        nivel_atencion_map = get_mapping(session, NivelAtencion, NivelAtencion.nivel_atencion.key, NivelAtencion.id.key, is_normalize=True)
        estrato_unidad_map = get_mapping(session, EstratoUnidad, EstratoUnidad.estrato_unidad.key, EstratoUnidad.id.key, is_normalize=True)
        tipo_obra_map = get_mapping(session, TiposObra, TiposObra.tipo_obra.key, TiposObra.id.key, is_normalize=True)

        df[Establecimientos.institucion_id.key] = df[Instituciones.institucion.key].map(instituciones_map)
        df[Establecimientos.localidad_id.key] = map_multiindex(
            localidades_map,
            [df[Localidades.municipio_id.key], df[Localidades.entidad_id.key], df[Localidades.clave_localidad.key]],
        )
        df[Establecimientos.jurisdiccion_id.key] = df[Jurisdicciones.jurisdiccion.key].map(jurisdicciones_map)
        df[Establecimientos.tipologia_id.key] = df[Tipologias.tipologia.key].map(tipologias_map)
        df[Establecimientos.subtipologia_id.key] = df[Subtipologias.subtipologia.key].map(subtipologias_map)

        df[Establecimientos.vialidad_id.key] = map_multiindex(
            vialidades_map,
            [df[Vialidades.vialidad.key].map(normalize_text), df[TiposVialidad.tipo_vialidad.key].map(tipo_vialidad_map)],
        )

        df[Establecimientos.rfc_id.key] = df[RfcEstablecimientos.rfc.key].map(rfc_map)
        df[Establecimientos.marca_movil_id.key] = map_multiindex(
            marcas_map,
            [df[MarcasMoviles.marca.key].map(normalize_text), df[MarcasMoviles.marca_especifica.key].map(normalize_text), df[MarcasMoviles.modelo.key].map(normalize_text)],
        )
        df[Establecimientos.programa_movil_id.key] = df[ProgramasMoviles.programa_movil.key].map(programas_map)
        df[Establecimientos.unidad_movil_id.key] = df[UnidadesMoviles.nombre_unidad_movil.key].map(unidades_moviles_map)
        df[Establecimientos.tipo_unidad_movil_id.key] = df[TiposUnidadMovil.tipo_unidad_movil.key].map(tipos_unidad_movil_map)
        df[Establecimientos.tipologia_movil_id.key] = df[TipologiasMoviles.tipologia_movil.key].map(tipologias_moviles_map)
        df[Establecimientos.instituto_adm_id.key] = df[InstitutosAdministracion.instituto_administracion.key].map(institutos_map)
        df[Establecimientos.movimiento_id.key] = normalize_col(df, Movimientos.movimiento.key).map(movimientos_map)
        df[Establecimientos.motivo_baja_id.key] = df[MotivosBaja.motivo_baja.key].map(motivos_map)

        df[Establecimientos.tipo_establecimiento_id.key] = normalize_col(df, TiposEstablecimiento.tipo_establecimiento.key).map(tipos_establecimiento_map)
        df[Establecimientos.tipo_asentamiento_id.key] = normalize_col(df, TiposAsentamiento.tipo_asentamiento.key).map(tipos_asentamiento_map)
        df[Establecimientos.estatus_id.key] = normalize_col(df, EstatusEstablecimiento.estatus_establecimiento.key).map(estatus_map)
        df[Establecimientos.nivel_atencion_id.key] = normalize_col(df, NivelAtencion.nivel_atencion.key).map(nivel_atencion_map)
        df[Establecimientos.estrato_unidad_id.key] = normalize_col(df, EstratoUnidad.estrato_unidad.key).map(estrato_unidad_map)
        df[Establecimientos.tipo_obra_id.key] = normalize_col(df, TiposObra.tipo_obra.key).map(tipo_obra_map)

        return df.replace({np.nan: None})

    def source(self, input_data: Optional[Any]) -> Any:
        self.logger.info(f"[source] {len(input_data['df'])} rows received")
        return input_data

    def action(self, input_data: Any) -> Any:
        self.logger.info("[action] Loading data into DB")
        df = input_data["df"]
        catalogs = input_data["catalogs"]

        self.db.connect()
        SaludBase.metadata.create_all(self.db.engine)

        with self.db.get_session() as session:
            self._load_catalogs(session, catalogs)
            df = self._map_foreign_keys(session, df)

            records_before = count_records(session, Establecimientos)

            records = df_to_records(df, Establecimientos.columns())
            bulk_insert(
                session, records, Establecimientos,
                chunk_size=50_000 if self.mode == "bootstrap" else 10_000,
            )

        return {"data": input_data, "records_before": records_before}

    def finalization(self, input_data: Any) -> Any:
        with self.db.get_session() as session:
            total = count_records(session, Establecimientos)
            inserted = total - input_data["records_before"]

        self.db.disconnect()
        cleanup_pipeline_data(self.pipeline_name)

        self.logger.info(f"[finalization] {format(total, ',')} establecimientos in database")
        self.logger.info(f"[finalization] {format(inserted, ',')} establecimientos inserted")
        return input_data["data"]
