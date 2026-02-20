from enum import auto, unique

from core.pipelines.establecimientos_de_salud.attributes.base import BaseClass


class EstablecimientosTables(BaseClass):
    LOCALIDADES = auto()
    JURISDICCIONES = auto()
    INSTITUCIONES = auto()
    TIPOS_ESTABLECIMIENTO = auto()
    TIPOLOGIAS = auto()
    SUBTIPOLOGIAS = auto()
    TIPOS_VIALIDAD = auto()
    VIALIDADES = auto()
    TIPOS_ASENTAMIENTO = auto()
    ESTATUS_ESTABLECIMIENTO = auto()
    NIVEL_ATENCION = auto()
    ESTRATO_UNIDAD = auto()
    TIPOS_OBRA = auto()
    RFC_ESTABLECIMIENTOS = auto()
    MARCAS_MOVILES = auto()
    PROGRAMAS_MOVILES = auto()
    UNIDADES_MOVILES = auto()
    TIPOS_UNIDAD_MOVIL = auto()
    TIPOLOGIAS_MOVILES = auto()
    INSTITUTOS_ADMINISTRACION = auto()
    MOVIMIENTOS = auto()
    MOTIVOS_BAJA = auto()
    ESTABLECIMIENTOS = auto()


class SourceColumns(BaseClass):
    CLUES = "CLUES"
    NOMBRE_INSTITUCION = "NOMBRE DE LA INSTITUCION"
    CLAVE_ENTIDAD = "CLAVE DE LA ENTIDAD"
    ENTIDAD = "ENTIDAD"
    CLAVE_MUNICIPIO = "CLAVE DEL MUNICIPIO"
    MUNICIPIO = "MUNICIPIO"
    CLAVE_LOCALIDAD = "CLAVE DE LA LOCALIDAD"
    LOCALIDAD = "LOCALIDAD"
    JURISDICCION = "JURISDICCION"
    CLAVE_TIPO_ESTABLECIMIENTO = "CLAVE DEL TIPO ESTABLECIMIENTO"
    NOMBRE_TIPO_ESTABLECIMIENTO = "NOMBRE TIPO ESTABLECIMIENTO"
    NOMBRE_TIPOLOGIA = "NOMBRE DE TIPOLOGIA"
    NOMBRE_SUBTIPOLOGIA = "NOMBRE DE SUBTIPOLOGIA"
    NOMBRE_UNIDAD = "NOMBRE DE LA UNIDAD"
    NOMBRE_COMERCIAL = "NOMBRE COMERCIAL"
    TIPO_VIALIDAD = "TIPO DE VIALIDAD"
    VIALIDAD = "VIALIDAD"
    NUMERO_EXTERIOR = "NUMERO EXTERIOR"
    NUMERO_INTERIOR = "NUMERO INTERIOR"
    CLAVE_TIPO_ASENTAMIENTO = "CLAVE TIPO DE ASENTAMIENTO"
    TIPO_ASENTAMIENTO = "TIPO DE ASENTAMIENTO"
    CLAVE_ESTATUS = "CLAVE ESTATUS DE OPERACION"
    ESTATUS = "ESTATUS DE OPERACION"
    RFC = "RFC DEL ESTABLECIMIENTO"
    MARCA = "UNIDAD MOVIL MARCA"
    MARCA_ESPECIFICA = "UNIDAD MOVIL MARCA ESPECIFICA"
    MODELO = "UNIDAD MOVIL MODELO"
    PROGRAMA_MOVIL = "UNIDAD MOVIL PROGRAMA"
    TIPO_UNIDAD_MOVIL = "UNIDAD MOVIL TIPO"
    TIPOLOGIA_MOVIL = "UNIDAD MOVIL TIPOLOGIA"
    INSTITUTO_ADM = "NOMBRE DE LA INS ADM"
    CLAVE_NIVEL_ATENCION = "CLAVE NIVEL ATENCION"
    NIVEL_ATENCION = "NIVEL ATENCION"
    CLAVE_ESTRATO_UNIDAD = "CLAVE ESTRATO UNIDAD"
    ESTRATO_UNIDAD = "ESTRATO UNIDAD"
    CLAVE_TIPO_OBRA = "CLAVE TIPO OBRA"
    TIPO_OBRA = "TIPO OBRA"
    ULTIMO_MOVIMIENTO = "ULTIMO MOVIMIENTO"
    FECHA_ULTIMO_MOVIMIENTO = "FECHA ULTIMO MOVIMIENTO"
    MOTIVO_BAJA = "MOTIVO BAJA"
    FECHA_EFECTIVA_BAJA = "FECHA EFECTIVA DE BAJA"
    TELEFONO_1 = "TELEFONO 1 DEL ESTABLECIMIENTO"
    EXTENSION_1 = "EXTENSION TELEFONICA 1 DEL ESTABLECIMIENTO"
    TELEFONO_2 = "TELEFONO 2 DEL ESTABLECIMIENTO"
    EXTENSION_2 = "EXTENSION TELEFONICA 2 DEL ESTABLECIMIENTO"
    FECHA_CONSTRUCCION = "FECHA DE CONSTRUCCION"
    FECHA_INICIO_OPERACION = "FECHA DE INICIO DE OPERACION"
    LATITUD = "LATITUD"
    LONGITUD = "LONGITUD"


@unique
class EstablecimientosColMap(BaseClass):
    clues = SourceColumns.CLUES
    institucion = SourceColumns.NOMBRE_INSTITUCION
    entidad_id = SourceColumns.CLAVE_ENTIDAD
    entidad = SourceColumns.ENTIDAD
    municipio_id = SourceColumns.CLAVE_MUNICIPIO
    municipio = SourceColumns.MUNICIPIO
    clave_localidad = SourceColumns.CLAVE_LOCALIDAD
    localidad = SourceColumns.LOCALIDAD
    jurisdiccion = SourceColumns.JURISDICCION
    tipo_establecimiento = SourceColumns.NOMBRE_TIPO_ESTABLECIMIENTO
    tipologia = SourceColumns.NOMBRE_TIPOLOGIA
    subtipologia = SourceColumns.NOMBRE_SUBTIPOLOGIA
    nombre_unidad_movil = SourceColumns.NOMBRE_UNIDAD
    nombre_comercial = SourceColumns.NOMBRE_COMERCIAL
    tipo_vialidad = SourceColumns.TIPO_VIALIDAD
    vialidad = SourceColumns.VIALIDAD
    numero_exterior = SourceColumns.NUMERO_EXTERIOR
    numero_interior = SourceColumns.NUMERO_INTERIOR
    tipo_asentamiento = SourceColumns.TIPO_ASENTAMIENTO
    estatus_establecimiento = SourceColumns.ESTATUS
    rfc = SourceColumns.RFC
    marca = SourceColumns.MARCA
    marca_especifica = SourceColumns.MARCA_ESPECIFICA
    modelo = SourceColumns.MODELO
    programa_movil = SourceColumns.PROGRAMA_MOVIL
    tipo_unidad_movil = SourceColumns.TIPO_UNIDAD_MOVIL
    tipologia_movil = SourceColumns.TIPOLOGIA_MOVIL
    instituto_administracion = SourceColumns.INSTITUTO_ADM
    nivel_atencion = SourceColumns.NIVEL_ATENCION
    estrato_unidad = SourceColumns.ESTRATO_UNIDAD
    tipo_obra = SourceColumns.TIPO_OBRA
    movimiento = SourceColumns.ULTIMO_MOVIMIENTO
    fecha_ultimo_movimiento = SourceColumns.FECHA_ULTIMO_MOVIMIENTO
    motivo_baja = SourceColumns.MOTIVO_BAJA
    fecha_efectiva_baja = SourceColumns.FECHA_EFECTIVA_BAJA
    telefono_1 = SourceColumns.TELEFONO_1
    extension_1 = SourceColumns.EXTENSION_1
    telefono_2 = SourceColumns.TELEFONO_2
    extension_2 = SourceColumns.EXTENSION_2
    fecha_construccion = SourceColumns.FECHA_CONSTRUCCION
    fecha_inicio_operacion = SourceColumns.FECHA_INICIO_OPERACION
    latitud = SourceColumns.LATITUD
    longitud = SourceColumns.LONGITUD
