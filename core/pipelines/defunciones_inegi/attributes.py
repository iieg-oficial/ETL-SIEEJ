from enum import StrEnum, auto

CATALOG_PREFIX = "cat_"


class DefuncionesInegiTables(StrEnum):
    # Catálogos de dominio cerrado (clave, descripcion)
    CAT_ACCIDENTAL_VIOLENTA = auto()
    CAT_AFROMEXICANO = auto()
    CAT_AREA_URBANA_RURAL = auto()
    CAT_ASISTENCIA_MEDICA = auto()
    CAT_CERTIFICANTE = auto()
    CAT_CIRUGIA = auto()
    CAT_COMPLICARON_EMBARAZO = auto()
    CAT_CONDICION_ACTIVIDAD = auto()
    CAT_CONDICION_EMBARAZO = auto()
    CAT_CONDICION_INDIGENA = auto()
    CAT_DONADOR = auto()
    CAT_EDAD_AGRUPADA = auto()
    CAT_ESCOLARIDAD = auto()
    CAT_ESTADO_CIVIL = auto()
    CAT_LENGUA = auto()
    CAT_LENGUA_INDIGENA = auto()
    CAT_LUGAR_OCURRENCIA = auto()
    CAT_MUERTE_ENCEFALICA = auto()
    CAT_NACIONALIDAD = auto()
    CAT_NECROPSIA = auto()
    CAT_OCURRIO_TRABAJO = auto()
    CAT_PARENTESCO_AGRESOR = auto()
    CAT_PRESUNTA_DEFUNCION_VIOLENTA = auto()
    CAT_RAZON_MATERNA = auto()
    CAT_RELACION_EMBARAZO = auto()
    CAT_SEXO = auto()
    CAT_SITIO_OCURRENCIA = auto()
    CAT_TAMANIO_LOCALIDAD = auto()
    CAT_USO_NECROPSIA = auto()
    CAT_VIOLENCIA_FAMILIAR = auto()

    # Catálogos con clave alfanumérica
    CAT_GRUPO_LISTA_MEXICANA = auto()
    CAT_LISTA_CIE = auto()
    CAT_LISTA_MEXICANA = auto()

    # Catálogos versionados por edición
    CAT_CIE10 = auto()
    CAT_DERECHOHABIENCIA = auto()
    CAT_LOCALIDAD = auto()
    CAT_OCUPACION = auto()

    # Catálogos de estructura propia
    CAT_CAPITULO_GRUPO = auto()
    CAT_PAIS = auto()

    CAT_EDICION = auto()

    STG_DEFUNCIONES = auto()
    STG_DEFUNCIONES_AMPLIACION = auto()

    @property
    def catalog_alias(self) -> str:
        """Nombre del CSV en `catalogos/` que alimenta esta tabla.

        INEGI nombra casi todos los archivos igual que la tabla sin el prefijo;
        las excepciones viven en CATALOG_ALIAS_OVERRIDES.
        """
        return self.removeprefix(CATALOG_PREFIX)

    @classmethod
    def catalogs(cls) -> tuple["DefuncionesInegiTables", ...]:
        """Todas las tablas de catálogo. La edición no lo es: la escribe el ETL."""
        return tuple(table for table in cls if table.startswith(CATALOG_PREFIX) and table != cls.CAT_EDICION)
