from typing import Final, List

from core.pipelines.centros_educativos.mappings.secondary_tables import NivelEducativoMap, ServicioEducativoMap

URL_HEADER: Final[dict] = {
    "Accept-Language": "es-ES,es;q=0.9",
    "Cache-Control": "no-cache",
    "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
    "Origin": "https://siged.sep.gob.mx",
    "Pragma": "no-cache",
    "Referer": "https://siged.sep.gob.mx/",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36",
}

REPLACE_VALUES: dict = {
    "U.S.A.E.R.": ServicioEducativoMap.USAER.value[1],
    "CAM": NivelEducativoMap.CAM.value[1],
}

RENAME_HEADER: Final[dict] = {
    "cct": "clave_centro_trabajo",
    "turno": "turno_id",
    "nombretur": "turno",
    "nombrect": "nombre_centro_trabajo",
    "tipoedu": "tipo_educativo",
    "nivel": "nivel_educativo",
    "subnivel": "servicio_educativo",
    "control": "tipo_control",
    "subcontrol": "tipo_sostenimiento",
    "claveentidad": "entidad_id",
    "entidad": "entidad",
    "clavemunicipio": "municipio_id",
    "municipio": "municipio",
    "clavelocalidad": "localidad_id",
    "localidad": "localidad",
    "domicilio": "domicilio",
    "numext": "numero_exterior",
    "entrecalle": "entre_calle",
    "ycalle": "y_calle",
    "calleposterior": "calle_posterior",
    "nombrecolonia": "colonia",
    "cp": "codigo_postal",
    "hombrestotal": "total_alumnos_hombres",
    "mujerestotal": "total_alumnas_mujeres",
    "docenteshom": "total_docentes_hombres",
    "docentesmuj": "total_docentes_mujeres",
    "nombredir": "nombre_director",
    "apellidodir1": "apellido_paterno_director",
    "aulasuso": "aulas_en_uso",
    "aulasexistentes": "aulas_existentes",
    "latitud": "latitud",
    "longitud": "longitud",
    "fecha_actualizacion": "fecha_actualizacion",
}

NULL_VALUES: Final[List[str]] = ["ninguno ninguno", "ninguno", "no disponible", "n/a", "na", "null", ""]

CAPITALIZE_COLS: Final[List[str]] = [
    "tipo_educativo",
    "nivel_educativo",
    "servicio_educativo",
    "tipo_control",
    "tipo_sostenimiento",
]

TITLE_COLS: Final[List[str]] = [
    "nombre_centro_trabajo",
    "entidad",
    "municipio",
    "localidad",
    "domicilio",
    "entre_calle",
    "y_calle",
    "calle_posterior",
    "colonia",
]

ENTIDADES_MEXICO: Final[List[int]] = list(range(1, 33))
