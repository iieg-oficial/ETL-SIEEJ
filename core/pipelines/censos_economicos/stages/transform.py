from typing import Any, Optional

import pandas as pd

from core.pipelines.censos_economicos.consts import CE_YEARS_CONFIG, KEY_COLUMNS, PIPELINE_NAME
from core.pipelines.stage import Stage
from core.utils.clean import list_values_to_null
from core.utils.normalize import lowercase_headers


class CETransformer(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "transform")
        self.mode = mode

    def source(self, input_data: Optional[Any] = None) -> dict:
        """Recibe y valida el inventario de la etapa Extract."""
        if not input_data or not input_data.get("years"):
            raise ValueError("La etapa Transform recibio un inventario vacio de Extract.")

        total_entries = sum(len(entries) for entries in input_data["years"].values())
        self.logger.info(f"Inventario recibido con {total_entries} entradas en {len(input_data['years'])} anio(s).")
        return input_data

    def action(self, input_data: Optional[Any] = None) -> dict:
        """Limpia CSVs de catalogos y valida encabezados de CSVs de datos."""
        inventory = input_data
        catalogs_by_year: dict[int, dict] = {}
        data_entries: list[dict] = []

        for year, entries in inventory["years"].items():
            # Buscar primer slug con catalogos (tipicamente "nac" -- los catalogos son identicos en todos los ZIPs)
            catalog_source = None
            for entry in entries:
                if entry.get("catalogs"):
                    catalog_source = entry
                    break

            year_catalogs = {}
            if catalog_source:
                cats = catalog_source["catalogs"]

                if "catalog_actividad" in cats:
                    year_catalogs["actividad"] = self._clean_actividad(cats["catalog_actividad"])

                if "catalog_entidad_municipio" in cats:
                    year_catalogs["entidad_municipio"] = self._clean_entidad_municipio(cats["catalog_entidad_municipio"])

                if "catalog_estrato" in cats:
                    year_catalogs["estrato"] = self._clean_estrato(cats["catalog_estrato"])

                if "diccionario" in cats:
                    year_catalogs["diccionario"] = self._clean_diccionario(cats["diccionario"], year)
            else:
                self.logger.warning(f"No se encontraron archivos de catalogo para el anio {year}.")

            catalogs_by_year[year] = year_catalogs

            # Validar encabezados de CSVs de datos y recolectar entradas para la etapa Load
            year_config = CE_YEARS_CONFIG.get(year, {})
            column_renames = year_config.get("column_renames", {})

            for entry in entries:
                data_csv = entry["data_csv"]
                try:
                    df_header = pd.read_csv(data_csv, nrows=0, dtype=str)
                    df_header.columns = [c.strip().lower() for c in df_header.columns]
                    df_header.rename(columns=column_renames, inplace=True)
                    missing_keys = [k for k in KEY_COLUMNS if k not in df_header.columns]
                    if missing_keys:
                        self.logger.warning(f"CSV de datos {data_csv} sin columnas clave: {missing_keys}")
                except Exception as e:
                    self.logger.error(f"Error al validar encabezados de {data_csv}: {e}")
                    continue

                data_entries.append(
                    {
                        "year": entry["year"],
                        "slug": entry["slug"],
                        "data_csv": entry["data_csv"],
                        "slug_dir": entry["slug_dir"],
                        "url": entry["url"],
                    }
                )

        self.logger.info(
            f"Catalogos limpiados para {len(catalogs_by_year)} anio(s). "
            f"Validados {len(data_entries)} CSV(s) de datos para carga."
        )

        return {
            "catalogs": catalogs_by_year,
            "data_entries": data_entries,
            "years": list(inventory["years"].keys()),
        }

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        """Pasa los datos limpios a la etapa Load."""
        return input_data

    def _read_and_clean(self, path: str) -> pd.DataFrame:
        """Pipeline comun de lectura y limpieza de CSV."""
        df = pd.read_csv(path, dtype=str, keep_default_na=False, index_col=False)
        lowercase_headers(df)
        df.columns = df.columns.str.strip()
        df = list_values_to_null(df)
        return df

    def _clean_actividad(self, path: str) -> list[dict]:
        self.logger.info(f"Limpiando catalogo de actividades: {path}")
        df = self._read_and_clean(path)

        records = []
        for _, row in df.iterrows():
            codigo = row.get("codigo")
            if not codigo:
                continue
            records.append(
                {
                    "codigo": codigo,
                    "descripcion": row.get("desc_codigo"),
                    "clasificador": row.get("clasificador_codigo"),
                }
            )

        self.logger.info(f"Se limpiaron {len(records)} codigos de actividad.")
        return records

    def _clean_entidad_municipio(self, path: str) -> list[dict]:
        self.logger.info(f"Limpiando catalogo de entidad-municipio: {path}")
        df = self._read_and_clean(path)

        # Detectar formato: 2024 tiene cvegeo/e03/e04/nom_ent, 2019 tiene entidad/municipio/nombre_entidad
        is_2024_format = "cvegeo" in df.columns

        records = []
        if is_2024_format:
            for _, row in df.iterrows():
                cvegeo = row.get("cvegeo")
                if not cvegeo:
                    continue
                records.append(
                    {
                        "cvegeo": cvegeo,
                        "cve_ent": row.get("e03"),
                        "nombre_entidad": row.get("nom_ent"),
                        "nombre_abreviado": row.get("nom_abr"),
                        "cve_mun": row.get("e04"),
                        "nombre_municipio": row.get("nom_mun"),
                    }
                )
        else:
            for _, row in df.iterrows():
                cve_ent = row.get("entidad")
                cve_mun = row.get("municipio")
                if not cve_ent or not cve_mun:
                    continue
                cvegeo = cve_ent + cve_mun
                records.append(
                    {
                        "cvegeo": cvegeo,
                        "cve_ent": cve_ent,
                        "nombre_entidad": row.get("nombre_entidad"),
                        "nombre_abreviado": None,
                        "cve_mun": cve_mun,
                        "nombre_municipio": row.get("nombre_municipio"),
                    }
                )

        self.logger.info(f"Se limpiaron {len(records)} entradas geograficas.")
        return records

    def _clean_estrato(self, path: str) -> list[dict]:
        self.logger.info(f"Limpiando catalogo de estratos: {path}")
        df = self._read_and_clean(path)

        records = []
        for _, row in df.iterrows():
            id_estrato = row.get("id_estrato") or ""
            records.append(
                {
                    "id_estrato": id_estrato,
                    "descripcion": row.get("desc_estrato"),
                }
            )

        self.logger.info(f"Se limpiaron {len(records)} entradas de estrato.")
        return records

    def _clean_diccionario(self, path: str, year: int) -> list[dict]:
        self.logger.info(f"Limpiando diccionario de datos: {path}")
        df = self._read_and_clean(path)

        records = []
        for _, row in df.iterrows():
            col_name = row.get("columna")
            if not col_name:
                continue
            records.append(
                {
                    "anio": year,
                    "nombre_columna": col_name,
                    "descripcion": row.get("descripcion"),
                    "tipo_dato": row.get("tipo_dato"),
                    "longitud": row.get("longitud"),
                    "codigos_validos": row.get("codigo_valido"),
                }
            )

        self.logger.info(f"Se limpiaron {len(records)} entradas de diccionario para el anio {year}.")
        return records
