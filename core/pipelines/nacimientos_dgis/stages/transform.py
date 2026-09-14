from datetime import date
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.nacimientos_dgis.attributes import NacimientosDgisTables as T
from core.pipelines.nacimientos_dgis.constants import (
    AGGREGATE_FILE,
    CATALOG_DIR,
    CATALOGS_FILE,
    EDAD_SENTINELS,
    FACTS_DIR,
    JALISCO_CVE_ENTIDAD,
    MANIFEST_NAME,
    MUNICIPIO_FACTOR,
    PIPELINE_NAME,
)
from core.pipelines.nacimientos_dgis.helpers.catalogs import catalog_records
from core.pipelines.nacimientos_dgis.helpers.facts import normalize_certificates
from core.pipelines.stage import Stage
from core.utils.logger import get_logger

CERTIFICATE_COLUMNS = [
    "anio",
    "fecha_nacimiento",
    "hora_nacimiento",
    "cve_geo",
    "localidad_residencia",
    "edad_madre",
    "edad_padre",
    "se_considera_indigena",
    "habla_lengua_indigena",
    "estado_conyugal",
    "escolaridad",
    "interrumpio_estudios",
    "ocupacion_habitual",
    "trabaja_actualmente",
    "afiliacion",
    "numero_embarazos",
    "atencion_prenatal",
    "total_consultas",
    "sobrevivio_parto",
    "sexo",
    "edad_gestacional",
    "talla",
    "peso",
    "producto_embarazo",
    "orden_producto",
    "total_productos",
    "diagnostico_1",
    "diagnostico_2",
    "lugar_nacimiento",
    "establecimiento_salud",
    "tiempo_traslado_minutos",
    "resolucion_embarazo",
    "entidad_parto",
    "municipio_parto",
    "localidad_parto",
]


class NacimientosDgisTransform(Stage):
    """Construye en paralelo el agregado por edad de la madre y el microdato.

    Los dos salen del mismo DataFrame ya filtrado a Jalisco, así que los totales
    del agregado y el conteo de certificados no se pueden separar.
    """

    def __init__(self):
        super().__init__(PIPELINE_NAME, "transform")
        self.logger = get_logger(f"{PIPELINE_NAME}.transform")
        self.extract_dir = Path(f"data/extract/{PIPELINE_NAME}")

    def source(self, input_data: Optional[Any] = None) -> dict[int, pd.DataFrame]:
        cached = {}
        for pkl in sorted(self.extract_dir.glob("sinac_*.pkl")):
            year = int(pkl.stem.split("_")[1])
            cached[year] = pd.read_pickle(pkl)
            self.logger.info(f"[source] {year}: loaded {len(cached[year]):,} rows from extract")

        return cached or input_data

    # ------------------------------------------------------------------
    # Catálogos
    # ------------------------------------------------------------------
    def _catalog_packages(self, years: list[int]) -> list[str]:
        manifest_path = self.extract_dir / MANIFEST_NAME
        if not manifest_path.exists():
            return []
        manifest = pd.read_pickle(manifest_path)
        # Orden ascendente: el paquete más reciente gana al deduplicar.
        return list(dict.fromkeys(manifest[year] for year in sorted(years) if year in manifest))

    def _build_catalogs(self, years: list[int]) -> dict[str, list[dict]]:
        catalogs: dict[str, list[dict]] = {str(table): [] for table in T.catalogs()}

        for package in self._catalog_packages(years):
            for table in catalogs:
                path = self.extract_dir / CATALOG_DIR / package / f"{table}.pkl"
                if path.exists():
                    catalogs[table].extend(catalog_records(pd.read_pickle(path), table))

        return {table: self._deduplicate(records) for table, records in catalogs.items()}

    @staticmethod
    def _deduplicate(records: list[dict]) -> list[dict]:
        if not records:
            return []
        # La edición más reciente gana cuando DGIS corrige una descripción.
        frame = pd.DataFrame(records).drop_duplicates(subset=["clave"], keep="last")
        return frame.astype(object).where(frame.notna(), None).to_dict("records")

    # ------------------------------------------------------------------
    # Hechos
    # ------------------------------------------------------------------
    def _jalisco(self, year: int, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["ENTIDADRESIDENCIA"] = pd.to_numeric(df["ENTIDADRESIDENCIA"], errors="coerce")
        df = df[df["ENTIDADRESIDENCIA"] == JALISCO_CVE_ENTIDAD]
        self.logger.info(f"[action] {year}: {len(df):,} rows after Jalisco filter")

        df["MUNICIPIORESIDENCIA"] = pd.to_numeric(df["MUNICIPIORESIDENCIA"], errors="coerce")

        # Los centinelas se anulan antes de cualquier cuenta: un 99 tomado por
        # edad real mete al padre en `nac_padre_18_mas` y sube el indicador de
        # madres de 10-14 varios puntos.
        for column in ("EDAD", "EDADPADRE"):
            values = pd.to_numeric(df[column], errors="coerce")
            df[column] = values.where(~values.isin(EDAD_SENTINELS))

        df["cve_geo"] = (df["ENTIDADRESIDENCIA"] * MUNICIPIO_FACTOR + df["MUNICIPIORESIDENCIA"]).astype("Int64")
        df["fecha_nacimiento"] = pd.to_datetime(df["FECHANACIMIENTO"], format="%d/%m/%Y", errors="coerce")
        df["anio"] = df["fecha_nacimiento"].dt.year

        df = df.dropna(subset=["anio", "cve_geo", "EDAD"])
        df["anio"] = df["anio"].astype(int)
        df["cve_geo"] = df["cve_geo"].astype(int)
        return df

    def _aggregate(self, year: int, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        # Los centinelas ya se anularon en `_jalisco`.
        df["padre_conocido"] = df["EDADPADRE"].notna()
        df["padre_18_y_mas"] = df["padre_conocido"] & (df["EDADPADRE"] >= 18)
        df["padre_25_y_mas"] = df["padre_conocido"] & (df["EDADPADRE"] >= 25)

        grouped = (
            df.groupby(["anio", "cve_geo", "EDAD"])
            .agg(
                tot_nac=("EDAD", "size"),
                nac_padre_conocido=("padre_conocido", "sum"),
                nac_padre_18_mas=("padre_18_y_mas", "sum"),
                nac_padre_25_mas=("padre_25_y_mas", "sum"),
            )
            .reset_index()
        )

        grouped = grouped.rename(columns={"EDAD": "edad_madre"})
        for column in ("edad_madre", "nac_padre_conocido", "nac_padre_18_mas", "nac_padre_25_mas"):
            grouped[column] = grouped[column].astype(int)
        grouped["fecha_actualizacion"] = date.today()

        self.logger.info(f"[action] {year}: {len(grouped):,} aggregated rows")
        return grouped

    def _certificates(self, year: int, df: pd.DataFrame) -> pd.DataFrame:
        frame = normalize_certificates(df)
        frame["fecha_nacimiento"] = frame["fecha_nacimiento"].dt.date
        frame["fecha_actualizacion"] = date.today()

        columns = [column for column in CERTIFICATE_COLUMNS if column in frame.columns]
        frame = frame[[*columns, "fecha_actualizacion"]]

        self.logger.info(f"[action] {year}: {len(frame):,} certificados normalizados")
        return frame

    def action(self, input_data: dict[int, pd.DataFrame]) -> dict[str, Any]:
        if not input_data:
            self.logger.info("[action] Empty input, skipping transform")
            return {"aggregate": pd.DataFrame(), "catalogs": {}, "editions": []}

        facts_dir = self.work_dir / FACTS_DIR
        facts_dir.mkdir(parents=True, exist_ok=True)

        frames, editions = [], []
        for year in sorted(input_data):
            df = input_data[year]
            if df.empty:
                continue
            jalisco = self._jalisco(year, df)
            frames.append(self._aggregate(year, jalisco))
            self._certificates(year, jalisco).to_pickle(facts_dir / f"{year}.pkl")
            editions.append(year)

        aggregate = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        self.logger.info(f"[action] {len(aggregate):,} total aggregated rows")

        return {
            "aggregate": aggregate,
            "catalogs": self._build_catalogs(editions),
            "editions": editions,
        }

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        aggregate = input_data["aggregate"]
        if not aggregate.empty:
            aggregate.to_pickle(self.work_dir / AGGREGATE_FILE)
            self.logger.info(f"[finalization] {len(aggregate):,} rows saved")

        catalogs = input_data["catalogs"]
        pd.to_pickle(catalogs, self.work_dir / CATALOGS_FILE)
        for table, records in sorted(catalogs.items()):
            self.logger.info(f"[finalization] {table}: {len(records)} registros")

        return {"editions": input_data["editions"]}
