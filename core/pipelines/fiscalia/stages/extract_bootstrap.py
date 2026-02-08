
from typing import Any, Optional
import pandas as pd

from core.utils.logger import get_logger
from core.pipelines.fiscalia.config import settings
from core.pipelines.stage import Stage
from core.pipelines.fiscalia.attributes.data_columns import HistoricalCols, RenameHistoricalCols, RenameLocalidades
from core.pipelines.fiscalia.helpers.gdrive import download_files_from_folder


class FiscaliaExtractBootstrap(Stage):
    def __init__(self, pipeline_name: str = 'Fiscalia', mode: str = 'bootstrap'):
        super().__init__(pipeline_name, 'extract')
        self.mode = mode
        self.logger = get_logger(f"{pipeline_name}.extract")

    def source(self, input_data: Optional[Any] = None) -> Any:
        self.logger.info("[source] Retrieving fiscalia data")
        file_paths = download_files_from_folder(
            folder_url=settings.BOOTSTRAP_CSV_FOLDER,
            output_folder="data/extract/Fiscalia",
            filenames=["fiscalia_data.csv", "localidades.csv"]
        )

        return {
            "fiscalia": pd.read_csv(file_paths["fiscalia_data.csv"], encoding="utf-8"),
            "localidades": pd.read_csv(file_paths["localidades.csv"], encoding="utf-8")
        }

    def action(self, input_data: dict) -> Any:
        fiscalia_df = input_data["fiscalia"]
        localidades_df = input_data["localidades"]
        self.logger.info(f"[action] Reading fiscalia data with {len(fiscalia_df)} values")

        try:
            fiscalia_df = fiscalia_df.rename(columns=RenameHistoricalCols.rename())
            fiscalia_df = fiscalia_df[HistoricalCols.get_values()]

            localidades_df = localidades_df.rename(columns=RenameLocalidades.rename())
            localidades_df = localidades_df[RenameLocalidades.get_values()]

        except Exception as e:
            self.logger.error(f"[action] {e}")

        return {
            "fiscalia": fiscalia_df,
            "localidades": localidades_df
        }

    def finalization(self, input_data: Optional[Any]) -> Any:
        self.logger.info(f"[finalization]: fiscalia={len(input_data['fiscalia'])} rows, localidades={len(input_data['localidades'])} rows")
        self.logger.info(f"[finalization]: Columnas de fiscalía {input_data['fiscalia'].columns}")
        self.logger.info(f"[finalization]: Columnas de localidades {input_data['localidades'].columns}")
        return input_data

if __name__ == "__main__":

    stage_instance = FiscaliaExtractBootstrap()
    input_data = stage_instance.source()
    input_data = stage_instance.action(input_data)
    stage_instance.finalization(input_data)


#TODO: Obtener los valores de localidades del csv del inegi.
#TODO: para el caso de los datos de update, hacer el mapeo de 18 de Marzo a -> dieciocho de marzo
# * Important : Es necesario revisar que el mapping se haga correctamente
# * En caso de que cuando se quiera mapear el id de la tabla localidades, a la tabla casos, el nombre de la localidad no haga match,
# * mapear a null, debe imprimir el nombre del municipio que mandó a null, para saber si hay que hacer un renaming antes
#

#* Important!: Como ahorita no hay valores en calles, en la tabla historica, entonces se debe mapear las calles a null
#
#
    # import pandas as pd
    # from num2words import num2words
    # import re

    # def convertir_fecha_a_texto(fecha_str):
    #     match = re.search(r'(\d+)', fecha_str)
    #     if match:
    #         numero = int(match.group(1))
    #         texto_numero = num2words(numero, lang='es')
    #         return re.sub(r'\d+', texto_numero, fecha_str)
    #     return fecha_str

    # # df['fecha_texto'] = df['fecha'].apply(convertir_fecha_a_texto)
    # print(convertir_fecha_a_texto("18 de marzo").title())
    # print(convertir_fecha_a_texto("1 de agosto").title())
    # print(convertir_fecha_a_texto("12 de diciembre"))
