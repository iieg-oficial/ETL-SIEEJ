from datetime import date
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.constants.geo import JALISCO_CVE_ENTIDAD
from core.pipelines.asg_imss.consts import (
    HASH_FIELDS,
    METRIC_FLOAT_COLUMNS,
    METRIC_INT_COLUMNS,
    PIPELINE_NAME,
)
from core.pipelines.stage import Stage
from core.utils.files import clean_directory
from core.utils.records import compute_record_hash


def _extract_sector2_catalogs(df: pd.DataFrame) -> list[dict]:
    cols = ["sector_economico_1", "sector_economico_2"]
    sub = df[cols].dropna().drop_duplicates()
    records = []
    for _, row in sub.iterrows():
        s1 = int(row["sector_economico_1"])
        s2 = int(row["sector_economico_2"])
        records.append(
            {
                "cve_sector_1": s1,
                "cve_sector_2": s2,
                "cve_sector_2_2pos": int(f"{s1}{s2}"),
                "descripcion": f"Subsector {s2}",
            }
        )
    return records


def _extract_sector4_catalogs(df: pd.DataFrame) -> list[dict]:
    cols = ["sector_economico_2", "sector_economico_4"]
    sub = df[cols].dropna().drop_duplicates()
    records = []
    for _, row in sub.iterrows():
        s2 = int(row["sector_economico_2"])
        s4 = int(row["sector_economico_4"])
        records.append(
            {
                "cve_sector_2": s2,
                "cve_sector_4": s4,
                "cve_sector_4_4pos": str(s4).zfill(4),
                "descripcion": f"Fracción {s4}",
            }
        )
    return records


class AsgImssTransformer(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "transform")
        self.mode = mode

    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data:
            raise ValueError("Transform no recibió datos de Extract.")
        return input_data

    def action(self, input_data: Optional[Any] = None) -> dict:
        downloaded: list[dict] = input_data.get("downloaded", [])

        transformed_files = []
        all_catalogs: dict[str, list[dict]] = {
            "delegacion": [],
            "subdelegacion": [],
            "entidad_municipio": [],
            "sector_1": [],
            "sector_2": [],
            "sector_4": [],
        }
        total_rows = 0

        for item in downloaded:
            date_str = item["date"]
            csv_path = Path(item["file_path"])

            if not csv_path.exists():
                self.logger.warning(f"Archivo no encontrado: {csv_path}")
                continue

            pkl_path = self.work_dir / f"asg-{date_str}.pkl"

            self.logger.info(f"Transformando: {csv_path.name}")
            for _enc in ("utf-8", "latin-1"):
                try:
                    df = pd.read_csv(csv_path, encoding=_enc, sep="|", dtype=str, low_memory=False)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                self.logger.error(f"No se detectó encoding válido (utf-8 o latin-1) en {csv_path.name}, omitiendo.")
                continue
            self.logger.info(f"  Leídas {len(df):,} filas — columnas: {list(df.columns)}")

            # Normalizar nombre de columna con ñ
            df.rename(columns={"tamaño_patron": "tamanio_patron"}, inplace=True)

            # Filtrar solo Jalisco
            if "cve_entidad" not in df.columns:
                self.logger.error(f"Columna 'cve_entidad' no encontrada en {csv_path.name}")
                continue
            df["cve_entidad"] = pd.to_numeric(df["cve_entidad"], errors="coerce")
            df = df[df["cve_entidad"] == JALISCO_CVE_ENTIDAD].copy()
            self.logger.info(f"  Registros de Jalisco: {len(df):,}")

            if df.empty:
                self.logger.warning(f"Sin datos de Jalisco en {csv_path.name}")
                continue

            # Convertir métricas enteras
            for col in METRIC_INT_COLUMNS:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

            # Convertir métricas float
            for col in METRIC_FLOAT_COLUMNS:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0).astype(float)

            # Convertir columnas dimensionales numéricas
            for col in ("cve_delegacion", "cve_subdelegacion", "cve_entidad", "sexo"):
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            for col in ("sector_economico_1", "sector_economico_2", "sector_economico_4"):
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            # Agregar fecha_corte como date
            df["fecha_corte"] = date.fromisoformat(date_str)

            # Calcular record_hash
            df["record_hash"] = df.apply(lambda row: compute_record_hash(row.to_dict(), HASH_FIELDS), axis=1)

            # Sanitizar NaN → None
            df = df.where(pd.notna(df), other=None)

            # Extraer catálogos dinámicos
            # delegacion
            if "cve_delegacion" in df.columns:
                for cve in df["cve_delegacion"].dropna().unique():
                    rec = {"cve_delegacion": int(cve), "descripcion": f"Delegación {int(cve)}"}
                    if rec not in all_catalogs["delegacion"]:
                        all_catalogs["delegacion"].append(rec)

            # subdelegacion
            if "cve_delegacion" in df.columns and "cve_subdelegacion" in df.columns:
                for _, row in df[["cve_delegacion", "cve_subdelegacion"]].dropna().drop_duplicates().iterrows():
                    rec = {
                        "cve_delegacion": int(row["cve_delegacion"]),
                        "cve_subdelegacion": int(row["cve_subdelegacion"]),
                        "descripcion": f"Subdelegación {int(row['cve_subdelegacion'])}",
                    }
                    if rec not in all_catalogs["subdelegacion"]:
                        all_catalogs["subdelegacion"].append(rec)

            # entidad_municipio
            mun_cols = [c for c in ("cve_municipio", "cve_delegacion", "cve_entidad") if c in df.columns]
            if len(mun_cols) == 3:
                for _, row in df[mun_cols].dropna().drop_duplicates().iterrows():
                    cve_mun = str(row["cve_municipio"]).strip()
                    rec = {
                        "cve_municipio": cve_mun,
                        "cve_delegacion": int(row["cve_delegacion"]),
                        "cve_entidad": int(row["cve_entidad"]),
                        "desc_entidad": "Jalisco",
                        "desc_municipio": cve_mun,
                    }
                    if rec["cve_municipio"] not in {r["cve_municipio"] for r in all_catalogs["entidad_municipio"]}:
                        all_catalogs["entidad_municipio"].append(rec)

            # sector_1
            if "sector_economico_1" in df.columns:
                for cve in df["sector_economico_1"].dropna().unique():
                    rec = {"cve_sector_1": int(cve), "descripcion": f"Sector {int(cve)}"}
                    if rec["cve_sector_1"] not in {r["cve_sector_1"] for r in all_catalogs["sector_1"]}:
                        all_catalogs["sector_1"].append(rec)

            # sector_2
            if "sector_economico_1" in df.columns and "sector_economico_2" in df.columns:
                new_s2 = _extract_sector2_catalogs(df)
                existing_keys = {(r["cve_sector_1"], r["cve_sector_2"]) for r in all_catalogs["sector_2"]}
                for rec in new_s2:
                    key = (rec["cve_sector_1"], rec["cve_sector_2"])
                    if key not in existing_keys:
                        all_catalogs["sector_2"].append(rec)
                        existing_keys.add(key)

            # sector_4
            if "sector_economico_2" in df.columns and "sector_economico_4" in df.columns:
                new_s4 = _extract_sector4_catalogs(df)
                existing_keys = {(r["cve_sector_2"], r["cve_sector_4"]) for r in all_catalogs["sector_4"]}
                for rec in new_s4:
                    key = (rec["cve_sector_2"], rec["cve_sector_4"])
                    if key not in existing_keys:
                        all_catalogs["sector_4"].append(rec)
                        existing_keys.add(key)

            df.to_pickle(pkl_path)
            self.logger.info(f"  Guardado pickle: {pkl_path.name} ({len(df):,} filas)")
            total_rows += len(df)
            transformed_files.append({"date": date_str, "file_path": str(pkl_path)})

        self.logger.info(f"Transformación completa. Total filas: {total_rows:,}")
        return {"files": transformed_files, "catalogs": all_catalogs, "row_count": total_rows}

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        extract_dir = Path(f"data/extract/{PIPELINE_NAME}")
        clean_directory(extract_dir, self.logger)
        row_count = input_data.get("row_count", 0) if input_data else 0
        self.logger.info(f"Transform finalizado. Filas procesadas: {row_count:,}")
        return input_data
