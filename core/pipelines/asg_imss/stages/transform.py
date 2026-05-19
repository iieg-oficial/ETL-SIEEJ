from datetime import date
from pathlib import Path
from typing import Any, Optional

import openpyxl
import pandas as pd

from core.constants.geo import JALISCO_CVE_ENTIDAD
from core.pipelines.asg_imss.consts import (
    METRIC_FLOAT_COLUMNS,
    METRIC_INT_COLUMNS,
    NULL_VALUES,
    PIPELINE_NAME,
)
from core.pipelines.stage import Stage
from core.utils.files import clean_directory, detect_encoding
from core.utils.normalize import strip_accents

# Static catalog columns with str keys
_STR_CATALOG_COLS: dict[str, str] = {
    "tamanio_patron": "tamanio_patron",
    "rango_edad": "rango_edad",
    "rango_salarial": "rango_salarial",
    "rango_uma": "rango_uma",
}


def _parse_catalog_dict(xlsx_path: Path) -> dict:
    """Parse IMSS data dictionary Excel and return structured lookup dicts.

    Returns a dict with keys:
        delegaciones, subdelegaciones, entidades_municipio,
        sectores_1, sectores_2, sectores_4,
        tamanio_patron, sexo, rango_edad, rango_salarial, rango_uma.
    """
    wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)

    # delegacion / subdelegacion
    delegaciones: dict[int, str] = {}
    subdelegaciones: dict[tuple[int, int], str] = {}
    ws_deleg = wb["delegación-subdelegación"]
    for row in ws_deleg.iter_rows(min_row=3, values_only=True):
        cve_d, desc_d, cve_s, desc_s = row[0], row[1], row[2], row[3]
        if cve_d is None:
            continue
        try:
            delegaciones[int(cve_d)] = str(desc_d).strip()
            if cve_s is not None:
                subdelegaciones[(int(cve_d), int(cve_s))] = str(desc_s).strip()
        except (ValueError, TypeError):
            continue

    # entidad-municipio
    entidades_municipio: dict[str, dict] = {}
    ws_mun = wb["entidad-municipio"]
    for row in ws_mun.iter_rows(min_row=3, values_only=True):
        cve_mun, cve_d, cve_e, desc_e, desc_m = row[0], row[1], row[2], row[3], row[4]
        if cve_mun is None:
            continue
        try:
            entidades_municipio[str(cve_mun).strip()] = {
                "cve_delegacion": int(cve_d),
                "cve_entidad": int(str(cve_e).lstrip("0") or "0"),
                "desc_entidad": str(desc_e).strip(),
                "desc_municipio": str(desc_m).strip(),
            }
        except (ValueError, TypeError):
            continue

    # sector 1 — ranges like "2 - 3" are expanded into individual entries
    sectores_1: dict[int, str] = {}
    ws_s1 = wb["sector 1"]
    for row in ws_s1.iter_rows(min_row=3, values_only=True):
        cve_raw, desc = row[0], row[1]
        if cve_raw is None:
            continue
        desc_str = str(desc).strip()
        cve_str = str(cve_raw).strip()
        if "-" in cve_str:
            parts = cve_str.split("-")
            try:
                start, end = int(parts[0].strip()), int(parts[1].strip())
                for cve in range(start, end + 1):
                    sectores_1[cve] = desc_str
            except (ValueError, IndexError):
                continue
        else:
            try:
                sectores_1[int(cve_str)] = desc_str
            except ValueError:
                continue

    # sector 2
    sectores_2: dict[tuple[int, int], dict] = {}
    ws_s2 = wb["sector 2"]
    for row in ws_s2.iter_rows(min_row=3, values_only=True):
        s1, s2, s2_2pos, desc = row[0], row[1], row[2], row[3]
        if s1 is None or s2 is None:
            continue
        try:
            key = (int(s1), int(s2))
            sectores_2[key] = {
                "cve_sector_1": int(s1),
                "cve_sector_2": int(s2),
                "cve_sector_2_2pos": int(s2_2pos) if s2_2pos is not None else int(f"{int(s1)}{int(s2)}"),
                "descripcion": str(desc).strip(),
            }
        except (ValueError, TypeError):
            continue

    # sector 4
    sectores_4: dict[tuple[int, int], dict] = {}
    ws_s4 = wb["sector 4"]
    for row in ws_s4.iter_rows(min_row=3, values_only=True):
        _s1, s2, _s2_2pos, s4, s4_4pos, desc = row[0], row[1], row[2], row[3], row[4], row[5]
        if s2 is None or s4 is None:
            continue
        try:
            key = (int(s2), int(s4))
            sectores_4[key] = {
                "cve_sector_2": int(s2),
                "cve_sector_4": int(s4),
                "cve_sector_4_4pos": str(s4_4pos).strip() if s4_4pos is not None else str(int(s4)).zfill(4),
                "descripcion": str(desc).strip(),
            }
        except (ValueError, TypeError):
            continue

    # Tamaño de registro patronal — uppercase keys to match source data
    tamanio_patron: dict[str, str] = {}
    ws_tam = wb["Tamaño de registro patronal"]
    for row in ws_tam.iter_rows(min_row=3, values_only=True):
        cve, desc = row[0], row[1]
        if cve is None:
            continue
        cve_str = str(cve).strip().upper()
        if len(cve_str) > 5:
            continue
        tamanio_patron[cve_str] = str(desc).strip()

    # sexo
    sexo: dict[int, str] = {}
    ws_sexo = wb["sexo"]
    for row in ws_sexo.iter_rows(min_row=3, values_only=True):
        cve, desc = row[0], row[1]
        if cve is None:
            continue
        try:
            sexo[int(cve)] = str(desc).strip()
        except (ValueError, TypeError):
            continue

    # Rango edad
    rango_edad: dict[str, str] = {}
    ws_re = wb["Rango edad"]
    for row in ws_re.iter_rows(min_row=3, values_only=True):
        cve, desc = row[0], row[1]
        if cve is None:
            continue
        cve_str = str(cve).strip()
        if len(cve_str) > 5:
            continue
        rango_edad[cve_str] = str(desc).strip()

    # Rango salario
    rango_salarial: dict[str, str] = {}
    ws_rs = wb["Rango salario"]
    for row in ws_rs.iter_rows(min_row=3, values_only=True):
        cve, desc = row[0], row[1]
        if cve is None:
            continue
        cve_str = str(cve).strip()
        if len(cve_str) > 5:
            continue
        rango_salarial[cve_str] = str(desc).strip()

    # Rango UMA (sheet column is named "rango_salarial" but contains rango_uma codes)
    rango_uma: dict[str, str] = {}
    ws_uma = wb["Rango UMA"]
    for row in ws_uma.iter_rows(min_row=3, values_only=True):
        cve, desc = row[0], row[1]
        if cve is None:
            continue
        cve_str = str(cve).strip()
        if len(cve_str) > 5:
            continue
        rango_uma[cve_str] = str(desc).strip()

    wb.close()
    return {
        "delegaciones": delegaciones,
        "subdelegaciones": subdelegaciones,
        "entidades_municipio": entidades_municipio,
        "sectores_1": sectores_1,
        "sectores_2": sectores_2,
        "sectores_4": sectores_4,
        "tamanio_patron": tamanio_patron,
        "sexo": sexo,
        "rango_edad": rango_edad,
        "rango_salarial": rango_salarial,
        "rango_uma": rango_uma,
    }


def _collect_dynamic_catalogs(
    df: pd.DataFrame,
    all_catalogs: dict[str, list[dict]],
    excel_cats: Optional[dict] = None,
    unknown_keys: Optional[dict[str, set]] = None,
) -> None:
    """Collect delegacion, subdelegacion, and entidad_municipio entries from a DataFrame.

    When excel_cats is provided, descriptions are enriched from the dictionary.
    Entries absent from the dictionary are flagged in unknown_keys and assigned
    '[SIN DESCRIPCIÓN]' as description.
    """
    # delegacion
    if "cve_delegacion" in df.columns:
        existing_deleg = {r["cve_delegacion"] for r in all_catalogs["delegacion"]}
        for cve in df["cve_delegacion"].dropna().unique():
            cve_int = int(cve)
            if cve_int in existing_deleg:
                continue
            if excel_cats:
                desc = excel_cats["delegaciones"].get(cve_int)
                if desc is None:
                    if unknown_keys is not None:
                        unknown_keys["delegacion"].add(cve_int)
                    desc = "[SIN DESCRIPCIÓN]"
            else:
                desc = f"Delegación {cve_int}"
            all_catalogs["delegacion"].append({"cve_delegacion": cve_int, "descripcion": desc})
            existing_deleg.add(cve_int)

    # subdelegacion
    if "cve_delegacion" in df.columns and "cve_subdelegacion" in df.columns:
        existing_subdel = {(r["cve_delegacion"], r["cve_subdelegacion"]) for r in all_catalogs["subdelegacion"]}
        for _, row in df[["cve_delegacion", "cve_subdelegacion"]].dropna().drop_duplicates().iterrows():
            key = (int(row["cve_delegacion"]), int(row["cve_subdelegacion"]))
            if key in existing_subdel:
                continue
            if excel_cats:
                desc = excel_cats["subdelegaciones"].get(key)
                if desc is None:
                    if unknown_keys is not None:
                        unknown_keys["subdelegacion"].add(key)
                    desc = "[SIN DESCRIPCIÓN]"
            else:
                desc = f"Subdelegación {key[1]}"
            all_catalogs["subdelegacion"].append(
                {"cve_delegacion": key[0], "cve_subdelegacion": key[1], "descripcion": desc}
            )
            existing_subdel.add(key)

    # entidad_municipio
    mun_cols = [c for c in ("cve_municipio", "cve_delegacion", "cve_entidad") if c in df.columns]
    if len(mun_cols) == 3:
        existing_mun = {r["cve_municipio"] for r in all_catalogs["entidad_municipio"]}
        for _, row in df[mun_cols].dropna().drop_duplicates().iterrows():
            cve_mun = str(row["cve_municipio"]).strip()
            if cve_mun in existing_mun:
                continue
            if excel_cats:
                mun_info = excel_cats["entidades_municipio"].get(cve_mun)
                if mun_info:
                    rec = {
                        "cve_municipio": cve_mun,
                        "cve_delegacion": mun_info["cve_delegacion"],
                        "cve_entidad": mun_info["cve_entidad"],
                        "desc_entidad": mun_info["desc_entidad"],
                        "desc_municipio": mun_info["desc_municipio"],
                    }
                else:
                    if unknown_keys is not None:
                        unknown_keys["entidad_municipio"].add(cve_mun)
                    rec = {
                        "cve_municipio": cve_mun,
                        "cve_delegacion": int(row["cve_delegacion"]),
                        "cve_entidad": int(row["cve_entidad"]),
                        "desc_entidad": "[SIN DESCRIPCIÓN]",
                        "desc_municipio": "[SIN DESCRIPCIÓN]",
                    }
            else:
                rec = {
                    "cve_municipio": cve_mun,
                    "cve_delegacion": int(row["cve_delegacion"]),
                    "cve_entidad": int(row["cve_entidad"]),
                    "desc_entidad": "Jalisco",
                    "desc_municipio": cve_mun,
                }
            all_catalogs["entidad_municipio"].append(rec)
            existing_mun.add(cve_mun)


def _collect_sector_catalogs(df: pd.DataFrame, all_catalogs: dict[str, list[dict]]) -> None:
    """Collect sector catalog entries from a DataFrame (update mode fallback)."""
    # sector_1
    if "sector_economico_1" in df.columns:
        existing_s1 = {r["cve_sector_1"] for r in all_catalogs["sector_1"]}
        for cve in df["sector_economico_1"].dropna().unique():
            try:
                cve_int = int(cve)
            except (ValueError, TypeError):
                continue
            if cve_int not in existing_s1:
                all_catalogs["sector_1"].append({"cve_sector_1": cve_int, "descripcion": f"Sector {cve_int}"})
                existing_s1.add(cve_int)

    # sector_2
    if "sector_economico_1" in df.columns and "sector_economico_2" in df.columns:
        existing_s2 = {(r["cve_sector_1"], r["cve_sector_2"]) for r in all_catalogs["sector_2"]}
        for _, row in df[["sector_economico_1", "sector_economico_2"]].dropna().drop_duplicates().iterrows():
            try:
                s1, s2 = int(row["sector_economico_1"]), int(row["sector_economico_2"])
            except (ValueError, TypeError):
                continue
            key = (s1, s2)
            if key not in existing_s2:
                all_catalogs["sector_2"].append(
                    {
                        "cve_sector_1": s1,
                        "cve_sector_2": s2,
                        "cve_sector_2_2pos": int(f"{s1}{s2}"),
                        "descripcion": f"Subsector {s2}",
                    }
                )
                existing_s2.add(key)

    # sector_4
    if "sector_economico_2" in df.columns and "sector_economico_4" in df.columns:
        existing_s4 = {(r["cve_sector_2"], r["cve_sector_4"]) for r in all_catalogs["sector_4"]}
        for _, row in df[["sector_economico_2", "sector_economico_4"]].dropna().drop_duplicates().iterrows():
            try:
                s2, s4 = int(row["sector_economico_2"]), int(row["sector_economico_4"])
            except (ValueError, TypeError):
                continue
            key = (s2, s4)
            if key not in existing_s4:
                all_catalogs["sector_4"].append(
                    {
                        "cve_sector_2": s2,
                        "cve_sector_4": s4,
                        "cve_sector_4_4pos": str(s4).zfill(4),
                        "descripcion": f"Fracción {s4}",
                    }
                )
                existing_s4.add(key)


def _detect_unknown_static_values(df: pd.DataFrame, excel_cats: dict, unknown_keys: dict[str, set]) -> None:
    """Flag values in static catalog columns absent from the Excel dictionary."""
    for col, cat_key in _STR_CATALOG_COLS.items():
        if col not in df.columns:
            continue
        known = set(excel_cats[cat_key].keys())
        for val in df[col].dropna().unique():
            if str(val) not in known:
                unknown_keys[cat_key].add(str(val))

    if "sexo" in df.columns:
        known_sexo = set(excel_cats["sexo"].keys())
        for val in df["sexo"].dropna().unique():
            try:
                if int(val) not in known_sexo:
                    unknown_keys["sexo"].add(int(val))
            except (ValueError, TypeError):
                continue

    if "sector_economico_1" in df.columns:
        known_s1 = set(excel_cats["sectores_1"].keys())
        for val in df["sector_economico_1"].dropna().unique():
            try:
                if int(val) not in known_s1:
                    unknown_keys["sector_1"].add(int(val))
            except (ValueError, TypeError):
                continue

    if "sector_economico_1" in df.columns and "sector_economico_2" in df.columns:
        known_s2 = set(excel_cats["sectores_2"].keys())
        for _, row in df[["sector_economico_1", "sector_economico_2"]].dropna().drop_duplicates().iterrows():
            try:
                key = (int(row["sector_economico_1"]), int(row["sector_economico_2"]))
                if key not in known_s2:
                    unknown_keys["sector_2"].add(key)
            except (ValueError, TypeError):
                continue

    if "sector_economico_2" in df.columns and "sector_economico_4" in df.columns:
        known_s4 = set(excel_cats["sectores_4"].keys())
        for _, row in df[["sector_economico_2", "sector_economico_4"]].dropna().drop_duplicates().iterrows():
            try:
                key = (int(row["sector_economico_2"]), int(row["sector_economico_4"]))
                if key not in known_s4:
                    unknown_keys["sector_4"].add(key)
            except (ValueError, TypeError):
                continue


def _build_unknown_catalog_entries(all_catalogs: dict[str, list[dict]], unknown_keys: dict[str, set]) -> None:
    """Append '[SIN DESCRIPCIÓN]' placeholder entries for unknown catalog values."""
    for cve in unknown_keys.get("tamanio_patron", set()):
        all_catalogs["tamanio_patron"].append({"cve": str(cve), "descripcion": "[SIN DESCRIPCIÓN]"})

    for cve in unknown_keys.get("sexo", set()):
        all_catalogs["sexo"].append({"cve": int(cve), "descripcion": "[SIN DESCRIPCIÓN]"})

    for cve in unknown_keys.get("rango_edad", set()):
        all_catalogs["rango_edad"].append({"cve": str(cve), "descripcion": "[SIN DESCRIPCIÓN]"})

    for cve in unknown_keys.get("rango_salarial", set()):
        all_catalogs["rango_salarial"].append({"cve": str(cve), "descripcion": "[SIN DESCRIPCIÓN]"})

    for cve in unknown_keys.get("rango_uma", set()):
        all_catalogs["rango_uma"].append({"cve": str(cve), "descripcion": "[SIN DESCRIPCIÓN]"})

    existing_s1 = {r["cve_sector_1"] for r in all_catalogs["sector_1"]}
    for cve in unknown_keys.get("sector_1", set()):
        if cve not in existing_s1:
            all_catalogs["sector_1"].append({"cve_sector_1": int(cve), "descripcion": "[SIN DESCRIPCIÓN]"})

    existing_s2 = {(r["cve_sector_1"], r["cve_sector_2"]) for r in all_catalogs["sector_2"]}
    for key in unknown_keys.get("sector_2", set()):
        if key not in existing_s2:
            s1, s2 = key
            all_catalogs["sector_2"].append(
                {
                    "cve_sector_1": s1,
                    "cve_sector_2": s2,
                    "cve_sector_2_2pos": int(f"{s1}{s2}"),
                    "descripcion": "[SIN DESCRIPCIÓN]",
                }
            )

    existing_s4 = {(r["cve_sector_2"], r["cve_sector_4"]) for r in all_catalogs["sector_4"]}
    for key in unknown_keys.get("sector_4", set()):
        if key not in existing_s4:
            s2, s4 = key
            all_catalogs["sector_4"].append(
                {
                    "cve_sector_2": s2,
                    "cve_sector_4": s4,
                    "cve_sector_4_4pos": str(s4).zfill(4),
                    "descripcion": "[SIN DESCRIPCIÓN]",
                }
            )


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
        catalog_file_path: Optional[str] = input_data.get("catalog_file_path")

        # Parse catalog dictionary (bootstrap only)
        excel_cats: Optional[dict] = None
        if self.mode == "bootstrap":
            if catalog_file_path and Path(catalog_file_path).exists():
                try:
                    excel_cats = _parse_catalog_dict(Path(catalog_file_path))
                    self.logger.info("Diccionario de datos IMSS parseado correctamente.")
                except Exception as exc:
                    self.logger.warning(f"No se pudo parsear el diccionario: {exc}. Usando extracción dinámica.")
            else:
                self.logger.warning(
                    "Diccionario de datos no disponible. Los catálogos se extraerán de los archivos fuente."
                )

        transformed_files = []
        all_catalogs: dict[str, list[dict]] = {
            "delegacion": [],
            "subdelegacion": [],
            "entidad_municipio": [],
            "sector_1": [],
            "sector_2": [],
            "sector_4": [],
            "tamanio_patron": [],
            "sexo": [],
            "rango_edad": [],
            "rango_salarial": [],
            "rango_uma": [],
        }

        # Populate static + sector catalogs from Excel (bootstrap with dictionary)
        if excel_cats:
            all_catalogs["sector_1"] = [
                {"cve_sector_1": cve, "descripcion": desc} for cve, desc in excel_cats["sectores_1"].items()
            ]
            all_catalogs["sector_2"] = list(excel_cats["sectores_2"].values())
            all_catalogs["sector_4"] = list(excel_cats["sectores_4"].values())
            all_catalogs["tamanio_patron"] = [
                {"cve": cve, "descripcion": desc} for cve, desc in excel_cats["tamanio_patron"].items()
            ]
            all_catalogs["sexo"] = [{"cve": cve, "descripcion": desc} for cve, desc in excel_cats["sexo"].items()]
            all_catalogs["rango_edad"] = [
                {"cve": cve, "descripcion": desc} for cve, desc in excel_cats["rango_edad"].items()
            ]
            all_catalogs["rango_salarial"] = [
                {"cve": cve, "descripcion": desc} for cve, desc in excel_cats["rango_salarial"].items()
            ]
            all_catalogs["rango_uma"] = [
                {"cve": cve, "descripcion": desc} for cve, desc in excel_cats["rango_uma"].items()
            ]

        # Track catalog values found in CSV data but absent from the Excel dictionary
        unknown_keys: dict[str, set] = {
            k: set()
            for k in [
                "delegacion",
                "subdelegacion",
                "entidad_municipio",
                "sector_1",
                "sector_2",
                "sector_4",
                "tamanio_patron",
                "sexo",
                "rango_edad",
                "rango_salarial",
                "rango_uma",
            ]
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
            _csv_kwargs = dict(sep="|", dtype=str, low_memory=False, keep_default_na=False, na_values=NULL_VALUES)
            try:
                df = pd.read_csv(csv_path, encoding="utf-8", **_csv_kwargs)
            except UnicodeDecodeError:
                df = pd.read_csv(csv_path, encoding=detect_encoding(str(csv_path)), **_csv_kwargs)
            df.columns = [strip_accents(c) for c in df.columns]
            df.rename(columns={"tamano_patron": "tamanio_patron"}, inplace=True)
            self.logger.info(f"  Leídas {len(df):,} filas — columnas: {list(df.columns)}")

            # Filter to Jalisco
            if "cve_entidad" not in df.columns:
                self.logger.error(f"Columna 'cve_entidad' no encontrada en {csv_path.name}")
                continue
            df["cve_entidad"] = pd.to_numeric(df["cve_entidad"], errors="coerce")
            df = df[df["cve_entidad"] == JALISCO_CVE_ENTIDAD].copy()
            self.logger.info(f"  Registros de Jalisco: {len(df):,}")

            if df.empty:
                self.logger.warning(f"Sin datos de Jalisco en {csv_path.name}")
                continue

            # Convert integer metric columns
            for col in METRIC_INT_COLUMNS:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

            # Convert float metric columns
            for col in METRIC_FLOAT_COLUMNS:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0).astype(float)

            # Convert numeric dimension columns
            for col in ("cve_delegacion", "cve_subdelegacion", "cve_entidad", "sexo"):
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            for col in ("sector_economico_1", "sector_economico_2", "sector_economico_4"):
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            df["fecha_corte"] = date.fromisoformat(date_str)

            # Convert NaN to None (string catalog codes such as "NA" are preserved)
            df = df.where(pd.notna(df), other=None)

            # Collect catalog entries
            _collect_dynamic_catalogs(df, all_catalogs, excel_cats, unknown_keys if excel_cats else None)
            if excel_cats:
                _detect_unknown_static_values(df, excel_cats, unknown_keys)
            else:
                _collect_sector_catalogs(df, all_catalogs)

            df.to_pickle(pkl_path)
            self.logger.info(f"  Guardado pickle: {pkl_path.name} ({len(df):,} filas)")
            total_rows += len(df)
            transformed_files.append({"date": date_str, "file_path": str(pkl_path)})

        # Add placeholder entries for unknown catalog values (bootstrap with dictionary only)
        if excel_cats:
            _build_unknown_catalog_entries(all_catalogs, unknown_keys)

        unknown_catalog_values = {k: sorted(v, key=str) for k, v in unknown_keys.items() if v}
        if unknown_catalog_values:
            for cat, values in unknown_catalog_values.items():
                self.logger.warning(f"Valores no encontrados en diccionario — {cat}: {values}")

        self.logger.info(f"Transformación completa. Total filas: {total_rows:,}")
        return {
            "files": transformed_files,
            "catalogs": all_catalogs,
            "unknown_catalog_values": unknown_catalog_values,
            "row_count": total_rows,
        }

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        extract_dir = Path(f"data/extract/{PIPELINE_NAME}")
        clean_directory(extract_dir, self.logger)
        row_count = input_data.get("row_count", 0) if input_data else 0
        self.logger.info(f"Transform finalizado. Filas procesadas: {row_count:,}")
        return input_data
