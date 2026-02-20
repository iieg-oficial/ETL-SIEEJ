from typing import Any, Optional

import pandas as pd

from core.pipelines.stage import Stage
from core.utils import df_to_records
from core.utils.clean import list_values_to_null, drop_duplicates_col
from core.utils.logger import get_logger
from core.utils.normalize import capitalize_col, title_col
from core.utils.parse_datetime import parse_date
from core.pipelines.establecimientos_de_salud.attributes.establecimientos import EstablecimientosColMap, EstablecimientosTables as T
from core.pipelines.establecimientos_de_salud.schemas import Establecimientos, TiposUnidadMovil
from core.pipelines.establecimientos_de_salud.constants import (
    NULL_VALUES, CAPITALIZE_COLS, TITLE_COLS, DATE_COLS, GEO_CLAVE_COLS,
)
from core.pipelines.establecimientos_de_salud.helpers import sanitize_numero


class EstablecimientosTransform(Stage):
    def __init__(self, pipeline_name: str = 'establecimientos_de_salud', mode: str = 'bootstrap'):
        super().__init__(pipeline_name, 'transform')
        self.mode = mode
        self.logger = get_logger(f"{pipeline_name}.transform")

    def source(self, input_data: Optional[Any]) -> Any:
        pkl_path = self.work_dir.parent.parent / f"extract/establecimientos_de_salud/establecimientos_{self.mode}.pkl"
        self.logger.info(f"[source] Checking for existing pkl at {pkl_path}")
        if pkl_path.exists():
            self.logger.info(f"[source] Loading from pkl: {pkl_path}")
            return pd.read_pickle(pkl_path)
        self.logger.info(f"[source] pkl not found, using extract output ({len(input_data)} rows)")
        return input_data

    def _build_catalogs(self, df: pd.DataFrame) -> dict:
        def uniq(col):
            return drop_duplicates_col(df, col).dropna(subset=[col])

        instituciones = df_to_records(uniq("institucion"), ["institucion"])
        localidades = df_to_records(
            drop_duplicates_col(df, "localidad").dropna(subset=["clave_localidad", "municipio_id", "entidad_id"]),
            ["clave_localidad", "municipio_id", "entidad_id", "localidad"],
        )
        jurisdicciones = df_to_records(
            drop_duplicates_col(df, "jurisdiccion").dropna(subset=["jurisdiccion", "municipio_id", "entidad_id"]),
            ["jurisdiccion", "municipio_id", "entidad_id"],
        )
        tipologias = df_to_records(uniq("tipologia"), ["tipologia"])
        subtipologias = df_to_records(uniq("subtipologia"), ["subtipologia"])
        tipos_vialidad = df_to_records(uniq("tipo_vialidad"), ["tipo_vialidad"])
        vialidades = df_to_records(
            drop_duplicates_col(df, "vialidad").dropna(subset=["vialidad"]),
            ["vialidad", "tipo_vialidad"],
        )
        tipos_asentamiento = df_to_records(uniq("tipo_asentamiento"), ["tipo_asentamiento"])
        tipos_obra = df_to_records(uniq("tipo_obra"), ["tipo_obra"])
        rfc_establecimientos = df_to_records(uniq("rfc"), ["rfc"])
        marcas_moviles = df_to_records(
            drop_duplicates_col(df, "marca").dropna(subset=["marca"]),
            ["marca", "marca_especifica", "modelo"],
        )
        programas_moviles = df_to_records(uniq("programa_movil"), ["programa_movil"])
        unidades_moviles = df_to_records(
            drop_duplicates_col(df, "nombre_unidad_movil").dropna(subset=["nombre_unidad_movil"]),
            ["nombre_unidad_movil", "nombre_comercial"],
        )
        tipos_unidad_movil = df_to_records(uniq("tipo_unidad_movil"), ["tipo_unidad_movil"])
        tipologias_moviles = df_to_records(uniq("tipologia_movil"), ["tipologia_movil"])
        institutos_administracion = df_to_records(uniq("instituto_administracion"), ["instituto_administracion"])
        motivos_baja = df_to_records(uniq("motivo_baja"), ["motivo_baja"])

        return {
            T.INSTITUCIONES: instituciones,
            T.LOCALIDADES: localidades,
            T.JURISDICCIONES: jurisdicciones,
            T.TIPOLOGIAS: tipologias,
            T.SUBTIPOLOGIAS: subtipologias,
            T.TIPOS_VIALIDAD: tipos_vialidad,
            T.VIALIDADES: vialidades,
            T.TIPOS_ASENTAMIENTO: tipos_asentamiento,
            T.TIPOS_OBRA: tipos_obra,
            T.RFC_ESTABLECIMIENTOS: rfc_establecimientos,
            T.MARCAS_MOVILES: marcas_moviles,
            T.PROGRAMAS_MOVILES: programas_moviles,
            T.UNIDADES_MOVILES: unidades_moviles,
            T.TIPOS_UNIDAD_MOVIL: tipos_unidad_movil,
            T.TIPOLOGIAS_MOVILES: tipologias_moviles,
            T.INSTITUTOS_ADMINISTRACION: institutos_administracion,
            T.MOTIVOS_BAJA: motivos_baja,
        }

    def action(self, input_data: Any) -> Any:
        df = input_data.rename(columns=EstablecimientosColMap.rename())

        df["fecha_actualizacion"] = pd.to_datetime(df["fecha_actualizacion"])
        df[GEO_CLAVE_COLS] = df[GEO_CLAVE_COLS].astype(str)
        df["modelo"] = pd.to_numeric(df["modelo"], errors="coerce").apply(
            lambda x: str(int(x)) if pd.notna(x) else None
        )
        df = list_values_to_null(df, rm_list=NULL_VALUES)

        for col in CAPITALIZE_COLS:
            if col in df.columns:
                df[col] = df[col].str.rstrip(".")
                capitalize_col(df, col)

        for col in TITLE_COLS:
            if col in df.columns:
                df[col] = df[col].str.rstrip(".")
                title_col(df, col)

        df[GEO_CLAVE_COLS] = df[GEO_CLAVE_COLS].apply(pd.to_numeric, errors='coerce')

        df[EstablecimientosColMap.tipo_unidad_movil.name] = df[EstablecimientosColMap.tipo_unidad_movil.name].str.replace(r"(?i)^umm\s+", "", regex=True)

        df[EstablecimientosColMap.numero_exterior.name] = df[EstablecimientosColMap.numero_exterior.name].apply(sanitize_numero)
        df[EstablecimientosColMap.numero_interior.name] = df[EstablecimientosColMap.numero_interior.name].apply(sanitize_numero)

        for col in DATE_COLS:
            df[col] = parse_date(df[col], dayfirst=True)

        df["latitud"] = pd.to_numeric(df["latitud"], errors="coerce")
        df["longitud"] = pd.to_numeric(df["longitud"], errors="coerce")
        df = df[(df["longitud"] != 0.0) & (df["latitud"] != 0.0)]

        before = len(df)
        df = df.drop_duplicates(subset=["clues", "fecha_actualizacion"], keep="last")
        dupes = before - len(df)
        if dupes:
            self.logger.info(f"[action] Dropped {dupes} duplicate rows on (clues, fecha_actualizacion)")

        self.logger.info(f"[action] {len(df)} rows after sanitization")
        return {"df": df, "catalogs": self._build_catalogs(df)}

    def finalization(self, input_data: Any) -> Any:
        self.logger.info(f"[finalization] {len(input_data['df'])} rows passed through")
        return input_data
