from typing import Final
from core.pipelines.centros_educativos.mappings import NivelEducativo, ServicioEducativo

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
     'U.S.A.E.R.': ServicioEducativo.USAER.value[1],
     'CAM': NivelEducativo.CAM.value[1],
}

RENAME_HEADER = {
    "clavecct": "clave_centro_trabajo",
    "turno": "turno_id",
    "nombretur": "turno",
    "nombrect": "nombre_centro_trabajo",
    "tipoeducativo": "tipo_educativo",
    "nombreniv": "nivel_educativo",
    "servicioeducativo": "servicio_educativo",
    "nombrecont": "tipo_control",
    "sistenimiento": "tipo_sostenimiento",
    "claveentidad": "entidad_id",
    "nombreent": "entidad",
    "clavemunicipio": "municipio_id",
    "nombremun": "municipio",
    "clavelocalidad": "localidad_id",
    "nombreloc": "localidad",
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
    "apellidodir2": "apellido_materno_director",
    "aulasuso": "aulas_en_uso",
    "aulasexistentes": "aulas_existentes",
    "latitud": "latitud",
    "longitud": "longitud",
}

LIST_TO_NULL = [
    "ninguno ninguno", "ninguno"
]
